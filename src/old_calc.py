from src import utils
from src.utils import print_status
from sqlalchemy import text
from src.classes import MessageStyle, SegmentData, SegmentContext
from rich.console import Console, Group
from rich.table import Table
from rich.tree import Tree
from datetime import date, timedelta, datetime
import dateutil.relativedelta as rd
import psycopg2
import pandas as pd
import logging
import calendar
import numpy as np

def populate_bkings_carr_arr_df(start_date, end_date, engine, customer=None, contract=None, frequency='M', ignore_arr_override=False):
    """Generate a DataFrame with Bookings, ARR and CARR for each month."""

    console = Console()

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)


    # Adjust start_date and end_date for monthly and quarterly aggregation
    if frequency == 'M':
        start_date = start_date - pd.offsets.MonthBegin(1)  # First day of the month
        end_date = end_date + pd.offsets.MonthEnd(0)  # Last day of the month
    elif frequency == 'Q':
        start_date = start_date - pd.offsets.QuarterBegin(startingMonth=1)  # First day of the quarter
        end_date = end_date + pd.offsets.QuarterEnd(0)  # Last day of the quarter
    
    # Generate list of dates
    date_list = []
    current_date = start_date
    
    print_status(console, f"... generating bkings dataframe from {start_date} to {end_date}", MessageStyle.INFO)
    while current_date <= end_date:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        eom_date = current_date.replace(day=last_day)  # End-of-month date
        date_list.append(eom_date)
        
        # Add one month to get the next start_date
        current_date = eom_date + pd.offsets.MonthEnd(1)

    # Create empty DataFrame with 'ARR' and 'CARR' columns
    df = pd.DataFrame(index=date_list, columns=['Bookings', 'ARR', 'CARR'])

    # ========================
    # Get bookings data 
    query = text("""
    SELECT
    c.CustomerID AS "customer id",
    c.Name AS "customer name",
    con.ContractID AS "contract id",
    con.RenewalFromContractID AS "renewalfromcontractid",
    con.ContractDate AS "contractdate",
    con.TotalValue AS "totalvalue"
    FROM
    Customers c
    JOIN
    Contracts con ON c.CustomerID = con.CustomerID;
    """
                 )
    with engine.begin() as conn:
        result = conn.execute(query)
        src_bookings = result.fetchall()
        columns = result.keys()

    # Convert to DataFrame
    df_bookings = pd.DataFrame(src_bookings, columns=columns)
    # Convert 'contractdate' column to datetime
    df_bookings['contractdate'] = pd.to_datetime(df_bookings['contractdate'])

    # Filter by customer and contract
    if customer:
        df_bookings = df_bookings[df_bookings['customer id'] == customer]
    if contract:
        df_bookings = df_bookings[df_bookings['contract id'] == contract]
    
    # loop over date_list and populate df in the Bookings column, by adding in the contract value for each contract that has the same month and year as the date in date_list
    for d in date_list:
        # Get bookings for the month of d
        bookings = df_bookings.loc[(df_bookings['contractdate'].dt.month == d.month) & (df_bookings['contractdate'].dt.year == d.year)]

        # Sum the bookings for the month of d
        df.at[d, 'Bookings'] = bookings['totalvalue'].sum()

    # ========================
    # Get CARRARR source data
    df_carrarr = generate_subscription_data_table(engine)

    # Filter by customer and contract
    if customer:
        df_carrarr = df_carrarr[df_carrarr['customer id'] == customer]
    if contract:
        df_carrarr = df_carrarr[df_carrarr['contract id'] == contract]
    

    # Calculate ARR
    for d in date_list:
        d_datetime = pd.Timestamp(d)
        temp_df = df_carrarr.copy()

        if ignore_arr_override:
            # Use segmentstartdate as the effective start date
            temp_df['effective_start_date'] = pd.to_datetime(temp_df['segmentstartdate'])
        else:
            # Determine the effective start date based on ARROverrideStartDate if it's not NaT
            condition = pd.notna(temp_df['arroverridestartdate'])
            temp_df.loc[condition, 'effective_start_date'] = pd.to_datetime(temp_df.loc[condition, 'arroverridestartdate'])
            temp_df.loc[~condition, 'effective_start_date'] = pd.to_datetime(temp_df.loc[~condition, 'segmentstartdate'])

        # Identify renewal contracts
        renewal_contracts = temp_df[temp_df['renewalfromcontractid'].notna()]

        # Handle ARR for contracts being renewed by renewal contracts 
        for _, renewal_contract in renewal_contracts.iterrows():
            renewal_start = renewal_contract['effective_start_date']
            renewed_contract_id = renewal_contract['renewalfromcontractid']

            if d_datetime < renewal_start:  # If before renewal contract's effective date
                mask = (temp_df['contract id'] == renewal_contract['contract id'])
                temp_df = temp_df[~mask]  # Remove renewal contract for this date
            else:  # If on/after renewal contract's effective date
                mask = (temp_df['contract id'] == renewed_contract_id) & \
                    (temp_df['effective_start_date'] <= renewal_start) & \
                    (temp_df['segmentenddate'] >= renewal_start)
                temp_df = temp_df[~mask]  # Remove renewed contract for this date

        # Further filter for segments that are active on the provided date
        active_segments = temp_df[(temp_df['effective_start_date'] <= d_datetime) & (temp_df['segmentenddate'] >= d_datetime)]

        # Sum the annual value for the date d
        df.at[d, 'ARR'] = active_segments['annualvalue'].sum()

    # Calculate CARR
    for d in date_list:
        d_datetime = pd.Timestamp(d)
        
        # Filter for segments that are active from the contract date to the segment end date
        active_segments = df_carrarr[(df_carrarr['contractdate'] <= d_datetime) & 
                                     (df_carrarr['segmentenddate'] >= d_datetime)]

        # For contracts that are renewed, remove the original contract if the active segments dataframe contains the renewed contract
        # as well as the renewing contract, which can be done by looping through contract id and seeing if renewalfromcontractid is the same as the contract id
        active_segments = active_segments[~active_segments['contract id'].isin(active_segments['renewalfromcontractid'])]
    
        # Calculate total CARR for the date
        df.at[d, 'CARR'] = active_segments['annualvalue'].sum()
        
    df = df.astype(float)
    df = df.round(1)

    df.index = pd.to_datetime(df.index)

    if frequency == 'Q':
        # Aggregate data for quarters
        df_quarterly = pd.DataFrame()
        df_quarterly['Bookings'] = df['Bookings'].resample('Q').sum()
        df_quarterly['ARR'] = df['ARR'].resample('Q').transform('last')
        df_quarterly['CARR'] = df['CARR'].resample('Q').transform('last')
        
        # Reindexing the DataFrame with the new quarterly labels
        df_quarterly.index = df_quarterly.index.to_period('Q').strftime('Q%q %Y')

        return df_quarterly
    else:
        return df    # check if quarterly


def populate_revenue_df(start_date, end_date, type, engine, customer=None, contract=None, frequency='M'):
    """Populate a DataFrame with active revenue for each customer in each month. The days of the month on each of start_date and end_date are ignored in the creation of date_list that has middle or end of month days only, depending on the string value of type."""

    console = Console()
    
    # Generate list of dates
    date_list = []
    current_date = start_date

    print_status(console, f"... generating revenue dataframe from {start_date} to {end_date}", MessageStyle.INFO)

    while True:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)

        if type == "mid":
            target_day = 15
        elif type == "end":
            target_day = last_day
        else:
            raise ValueError("type must be either 'mid' or 'end'")
        
        target_date = current_date.replace(day=target_day)
        # If type is 'mid', always compare with the 15th of end_date
        if type == "mid" and target_date > end_date.replace(day=15):
            break
        # If type is 'end', compare with the last day of end_date's month
        elif type == "end" and target_date > end_date.replace(day=calendar.monthrange(end_date.year, end_date.month)[1]):
            break

        date_list.append(target_date)

        # Increment current_date by one month
        current_date += rd.relativedelta(months=1)

    # Create empty DataFrame
    df = pd.DataFrame(index=date_list)

    # Add columns for each customer name in df 
    query = text("""
    SELECT
    c.CustomerID AS "customer id",
    c.Name AS "customer name"
    FROM
    Customers c
    """
                 )
    with engine.begin() as conn:
        result = conn.execute(query)
        src_customers = result.fetchall()
        columns = result.keys()

    # Convert to DataFrame
    df_customers = pd.DataFrame(src_customers, columns=columns)
    # Set index to 'customer id'
    df_customers.set_index('customer id', inplace=True)

    # Add columns for each customer name in df
    for customer_id, customer_name in df_customers['customer name'].items():
        df[customer_name] = 0.0
    
    # ========================
    # Get revenue source data
    df_revenue = generate_subscription_data_table(engine)
    
    # Filter by customer ID if provided
    if customer:
        df_revenue = df_revenue[df_revenue['customer id'] == customer]

        # Filter by contract ID if provided
    if contract:
        df_revenue = df_revenue[df_revenue['contract id'] == contract]
        
    # loop over date_list and customer name and populate df in a column with customer name the revenue for the customer where the date in date_list is between the segmentstartdate and segmentenddate (inclusive), the revenue being calculated as the annual value divided by contract length in months
    # ...
    for d in date_list:
        d_datetime = pd.Timestamp(d)
        # Get contracts that are active for the month of d
        contracts = df_revenue.loc[(df_revenue['segmentstartdate'] <= d_datetime) & (df_revenue['segmentenddate'] >= d_datetime)]
        # Loop over customers
        for customer_id, customer_name in df_customers['customer name'].items():
            # Get contracts for the customer
            customer_contracts = contracts.loc[contracts['customer id'] == customer_id].copy()
            # Calculate the monthly revenue for each contract
            customer_contracts['monthly_revenue'] = customer_contracts['segmentvalue'] / customer_contracts['contractlength']
            # Sum the monthly revenues for the month of d
            revenue = customer_contracts['monthly_revenue'].sum()
            # Populate df
            df.at[d, customer_name] = revenue
        
    df = df.astype(float)
    df = df.round(1)
    df.index = pd.to_datetime(df.index)

    if frequency == 'Q':
        df = df.resample('Q').sum()
        df.index = [f"Q{period.quarter} {period.year}" for period in df.index]

    return df

def populate_metrics_df(start_date, end_date, engine, customer=None, contract=None, frequency='M'):
    """Populate a DataFrame with metrics for each month in the date range. Note that the days of the month on each of start_date and end_date are ignored in the creation of date_list that has end of month days only."""

    console = Console()

    # Obtain the revenue DataFrame
    # print(start_date, end_date)
    revenue_df = populate_revenue_df(start_date, end_date, "end", engine, customer, contract)

    # Force start_date and end_date to be the last days of the input months
    #start_date = start_date.replace(day=calendar.monthrange(start_date.year, start_date.month)[1])
    #end_date = end_date.replace(day=calendar.monthrange(end_date.year, end_date.month)[1])
    
    # Generate list of dates
    date_list = []
    current_date = start_date

    print_status(console, f"... generating metrics dataframe from {start_date} to {end_date}", MessageStyle.INFO)
    while current_date <= end_date:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        eom_date = current_date.replace(day=last_day)  # End-of-month date
        date_list.append(eom_date)
        
        # Add one month to get the next start_date
        current_date = eom_date + rd.relativedelta(days=1)    

    with engine.begin() as conn:
        customer_names_str = ("SELECT DISTINCT Name FROM Customers")
        if customer is not None:
            customer_names_str += f" WHERE CustomerID = '{customer}'"
        customer_names_result = conn.execute(text(customer_names_str))
        customer_names = [row[0] for row in customer_names_result.fetchall()]

    # Create a second DataFrame for metrics
    metrics_df = pd.DataFrame(index=date_list, columns=["New MRR", "Churn MRR", "Expansion MRR", "Contraction MRR", "Starting MRR", "Ending MRR"])
   
    # Find the starting MRR figure
    prior_month_date = date_list[0] - rd.relativedelta(months=1)
    prior_month_revenue_df = populate_revenue_df(prior_month_date, prior_month_date, "end", engine, customer, contract)
    prior_month_date = prior_month_revenue_df.index[0]
     
    # Calculate and populate metrics for the second DataFrame
    previous_month = None
    for d in date_list:
        # Initialize the metrics sums
        new_mrr_sum = 0
        churn_mrr_sum = 0
        expansion_mrr_sum = 0
        contraction_mrr_sum = 0
        
        if previous_month:
            ending_mrr_sum = metrics_df.loc[previous_month, "Ending MRR"]
            starting_mrr_sum = ending_mrr_sum
            
            for customer in customer_names:
                previous_month_revenue = revenue_df.loc[pd.Timestamp(previous_month), customer]
                current_month_revenue = revenue_df.loc[pd.Timestamp(d), customer]
                
                new_mrr_sum += current_month_revenue if previous_month_revenue == 0 and current_month_revenue > 0 else 0
                churn_mrr_sum += previous_month_revenue if previous_month_revenue > 0 and current_month_revenue == 0 else 0
                expansion_mrr_sum += current_month_revenue - previous_month_revenue if current_month_revenue > previous_month_revenue and previous_month_revenue > 0 else 0
                contraction_mrr_sum += previous_month_revenue - current_month_revenue if current_month_revenue < previous_month_revenue and current_month_revenue > 0 else 0
                
            ending_mrr_sum += new_mrr_sum + expansion_mrr_sum - churn_mrr_sum - contraction_mrr_sum
            
        else:
            # Summing up all customer revenues for the prior month
            starting_mrr_sum = prior_month_revenue_df.loc[prior_month_date].sum()
            ending_mrr_sum = starting_mrr_sum
            
            for customer in customer_names:
                prior_month_revenue = prior_month_revenue_df.loc[pd.Timestamp(prior_month_date), customer]
                current_month_revenue = revenue_df.loc[pd.Timestamp(d), customer]
            
                new_mrr_sum += current_month_revenue if prior_month_revenue == 0 and current_month_revenue > 0 else 0
                churn_mrr_sum += prior_month_revenue if prior_month_revenue > 0 and current_month_revenue == 0 else 0
                expansion_mrr_sum += current_month_revenue - prior_month_revenue if current_month_revenue > prior_month_revenue and prior_month_revenue > 0 else 0
                contraction_mrr_sum += prior_month_revenue - current_month_revenue if current_month_revenue < prior_month_revenue and current_month_revenue > 0 else 0
            
            ending_mrr_sum += new_mrr_sum + expansion_mrr_sum - churn_mrr_sum - contraction_mrr_sum
        
        metrics_df.at[d, "New MRR"] = new_mrr_sum
        metrics_df.at[d, "Churn MRR"] = churn_mrr_sum
        metrics_df.at[d, "Expansion MRR"] = expansion_mrr_sum
        metrics_df.at[d, "Contraction MRR"] = contraction_mrr_sum
        metrics_df.at[d, "Starting MRR"] = starting_mrr_sum
        metrics_df.at[d, "Ending MRR"] = ending_mrr_sum

        previous_month = d

        logging.info(f"Date: {d}")
        logging.info(f"New MRR: {new_mrr_sum}")
        logging.info(f"Churn MRR: {churn_mrr_sum}")
        logging.info(f"Expansion MRR: {expansion_mrr_sum}")
        logging.info(f"Contraction MRR: {contraction_mrr_sum}")
        logging.info(f"Starting MRR: {starting_mrr_sum}")
        logging.info(f"Ending MRR: {ending_mrr_sum}")

    metrics_df = metrics_df.astype(float)
    metrics_df = metrics_df.round(1)
    metrics_df.index = pd.to_datetime(metrics_df.index)

    if frequency == 'Q':
        metrics_df['Starting MRR'] = metrics_df['Starting MRR'].resample('Q').first()
        metrics_df['Ending MRR'] = metrics_df['Ending MRR'].resample('Q').last()

        metrics_df['New MRR'] = metrics_df['New MRR'].resample('Q').sum()
        metrics_df['Churn MRR'] = metrics_df['Churn MRR'].resample('Q').sum()
        metrics_df['Expansion MRR'] = metrics_df['Expansion MRR'].resample('Q').sum()
        metrics_df['Contraction MRR'] = metrics_df['Contraction MRR'].resample('Q').sum()

        metrics_df = metrics_df.dropna()
        metrics_df.index = metrics_df.index.to_period('Q').strftime('Q%q %Y')

    return metrics_df


def populate_arr_metrics_df(start_date, end_date, engine, customer=None, contract=None, frequency='M', ignore_arr_override=False):
    """Populate a DataFrame with ARR metrics for each month in the date range. Note that the days of the month on each of start_date and end_date are ignored in the creation of date_list that has end of month days only."""

    console = Console()

    # Generate list of dates
    date_list = []
    current_date = start_date

    print_status(console, f"... generating ARR metrics dataframe from {start_date} to {end_date}", MessageStyle.INFO)
    while current_date <= end_date:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        eom_date = current_date.replace(day=last_day)  # End-of-month date
        date_list.append(eom_date)
        
        # Add one month to get the next start_date
        current_date = eom_date + rd.relativedelta(days=1)    

    with engine.begin() as conn:
        customer_names_str = ("SELECT DISTINCT Name FROM Customers")
        if customer is not None:
            customer_names_str += f" WHERE CustomerID = '{customer}'"
        customer_names_result = conn.execute(text(customer_names_str))
        customer_names = [row[0] for row in customer_names_result.fetchall()]

    # Create a second DataFrame for metrics
    arr_metrics_df = pd.DataFrame(index=date_list, columns=["New ARR", "Churn ARR", "Expansion ARR", "Contraction ARR", "Starting ARR", "Ending ARR"])
  
    # Find the starting ARR figure
    prior_month_date = date_list[0] - rd.relativedelta(months=1)
    prior_month_arr_df = customer_arr_df(prior_month_date, engine, ignore_arr_override=ignore_arr_override)
    prior_month_date = prior_month_arr_df.index[0]
     
    # Calculate and populate metrics for the second DataFrame
    previous_month = None
    for d in date_list:
        # Initialize the metrics sums
        new_arr_sum = 0
        churn_arr_sum = 0
        expansion_arr_sum = 0
        contraction_arr_sum = 0

        # Obtain the ARR dataframe for the current month
        current_month_arr_df = customer_arr_df(d, engine, ignore_arr_override)
        
        if previous_month:
            ending_arr_sum = arr_metrics_df.loc[previous_month, "Ending ARR"]
            starting_arr_sum = ending_arr_sum
 
            prior_month_date = d - rd.relativedelta(months=1) 
            _, last_day = calendar.monthrange(prior_month_date.year, prior_month_date.month)
            prior_month_arr_df = customer_arr_df(prior_month_date.replace(day=last_day), engine)
            
            for customer in customer_names:
                previous_month_arr = prior_month_arr_df.loc[customer, "ARR"]
                current_month_arr = current_month_arr_df.loc[customer, "ARR"]
                
                new_arr_sum += current_month_arr if previous_month_arr == 0 and current_month_arr > 0 else 0
                churn_arr_sum += previous_month_arr if previous_month_arr > 0 and current_month_arr == 0 else 0
                expansion_arr_sum += current_month_arr - previous_month_arr if current_month_arr > previous_month_arr and previous_month_arr > 0 else 0
                contraction_arr_sum += previous_month_arr - current_month_arr if current_month_arr < previous_month_arr and current_month_arr > 0 else 0
                
            ending_arr_sum += new_arr_sum + expansion_arr_sum - churn_arr_sum - contraction_arr_sum
            
        else:
            # Summing up all customer revenues for the prior month
            starting_arr_sum = prior_month_arr_df.loc["Total ARR"].sum()
            ending_arr_sum = starting_arr_sum
            
            for customer in customer_names:
                prior_month_arr = prior_month_arr_df.loc[customer, "ARR"]
                current_month_arr = current_month_arr_df.loc[customer, "ARR"]

                new_arr_sum += current_month_arr if prior_month_arr == 0 and current_month_arr > 0 else 0
                churn_arr_sum += prior_month_arr if prior_month_arr > 0 and current_month_arr == 0 else 0
                expansion_arr_sum += current_month_arr - prior_month_arr if current_month_arr > prior_month_arr and prior_month_arr > 0 else 0
                contraction_arr_sum += prior_month_arr - current_month_arr if current_month_arr < prior_month_arr and current_month_arr > 0 else 0
            
            ending_arr_sum += new_arr_sum + expansion_arr_sum - churn_arr_sum - contraction_arr_sum
        
        arr_metrics_df.at[d, "New ARR"] = new_arr_sum
        arr_metrics_df.at[d, "Churn ARR"] = churn_arr_sum
        arr_metrics_df.at[d, "Expansion ARR"] = expansion_arr_sum
        arr_metrics_df.at[d, "Contraction ARR"] = contraction_arr_sum
        arr_metrics_df.at[d, "Starting ARR"] = starting_arr_sum
        arr_metrics_df.at[d, "Ending ARR"] = ending_arr_sum

        previous_month = d
    
    
    arr_metrics_df = arr_metrics_df.astype(float)
    arr_metrics_df = arr_metrics_df.round(1)
    arr_metrics_df.index = pd.to_datetime(arr_metrics_df.index)
        
    if frequency == 'Q':
        arr_metrics_df['Starting ARR'] = arr_metrics_df['Starting ARR'].resample('Q').first()
        arr_metrics_df['Ending ARR'] = arr_metrics_df['Ending ARR'].resample('Q').last()

        arr_metrics_df['New ARR'] = arr_metrics_df['New ARR'].resample('Q').sum()
        arr_metrics_df['Churn ARR'] = arr_metrics_df['Churn ARR'].resample('Q').sum()
        arr_metrics_df['Expansion ARR'] = arr_metrics_df['Expansion ARR'].resample('Q').sum()
        arr_metrics_df['Contraction ARR'] = arr_metrics_df['Contraction ARR'].resample('Q').sum()

        arr_metrics_df = arr_metrics_df.dropna()
        arr_metrics_df.index = arr_metrics_df.index.to_period('Q').strftime('Q%q %Y')

    return arr_metrics_df


def populate_ttm_metrics_df(target_date, engine, customer=None, contract=None):
    """
    Calculate trailing 12-month metrics.

    Args:
        target_date:
        engine:
    
    Returns:
        list: A list of tuples with metric names and their values.
    """
    
    console = Console()
    print_status(console, f"Calculating TTM NDR and GDR for {target_date}...", MessageStyle.INFO)
    # Calculate trailing 12-month values for a given date (e.g., 2023-06-15)
    start_date = pd.to_datetime(target_date) - pd.DateOffset(months=11)
    end_date = pd.to_datetime(target_date)

    # Source the appropriate dataframes for the metrics calcs
    metrics_df = populate_metrics_df(start_date, end_date, engine, customer, contract)
    
    date_list = metrics_df.index.strftime('%Y-%m-%d').tolist()
    
    trailing_start_date = date_list[0]
    trailing_end_date = date_list[-1]
 
    # Convert trailing_start_date to the same format as the index
    
    trailing_df = metrics_df.loc[trailing_start_date:trailing_end_date]

    # Build calcs from the dataframe
    
    beginning_arr = trailing_df.loc[trailing_start_date, "Starting MRR"] * 12
    churn = (-trailing_df["Churn MRR"].sum()) * 12
    contraction = (-trailing_df["Contraction MRR"].sum()) * 12
    gross_dollar_retention = beginning_arr + churn + contraction
    expansion = trailing_df["Expansion MRR"].sum() * 12
    net_dollar_retention = gross_dollar_retention + expansion

    return [
        ("Beginning ARR", beginning_arr),
        ("Churn", churn),
        ("Contraction", contraction),
        ("Gross Dollar Retention", gross_dollar_retention),
        ("Expansion", expansion),
        ("Net Dollar Retention", net_dollar_retention)
    ]


def customer_carr_df(date, engine, ignore_zeros=False, tree_detail=False):
    """Generate a DataFrame with CARR for each customer for a given date."""
    
    # Create an empty DataFrame
    df = pd.DataFrame(columns=['CustomerName', 'CARR'])

    df_carr = generate_subscription_data_table(engine)
    
    # Create a list of all customers
    customer_names_str = "SELECT DISTINCT Name FROM Customers"
    with engine.begin() as conn:
        customer_names_result = conn.execute(text(customer_names_str))
        customer_names = [row[0] for row in customer_names_result.fetchall()]

    # if tree_detail requested
    if tree_detail:
        root = Tree("ARR Tree", highlight=True)        
        
    date_datetime = pd.Timestamp(date)
    for customer in customer_names:
        customer_data = df_carr[df_carr['customer name'] == customer].copy()

        # Filter for segments that are active from the contract date to the segment end date
        active_segments = customer_data[(customer_data['contractdate'] <= date_datetime) & 
                                        (customer_data['segmentenddate'] >= date_datetime)]

        # For contracts that are renewed, remove the original contract if the active segments dataframe contains the renewed contract
        # as well as the renewing contract, which can be done by looping through contract id and seeing if renewalfromcontractid is the same as the contract id
        active_segments = active_segments[~active_segments['contract id'].isin(active_segments['renewalfromcontractid'])]

        # Add table to the tree node if tree_detail requested
        if tree_detail and not active_segments.empty:
            node = root.add(f"Customer: {customer}")
            table = Table(show_header=True, show_lines=True)
            columns = ['contract id', 'contractdate', 'arroverridestartdate', 'segmentstartdate', 'segmentenddate', 'segmentvalue']
            for col in columns:
                table.add_column(col)
            for index, row in active_segments.iterrows():
                row_values = []
                for col in columns:
                    if 'date' in col:  # Check if the column is a date
                        row_values.append(row[col].strftime('%Y-%m-%d') if pd.notna(row[col]) else 'N/A')
                    elif pd.api.types.is_float_dtype(active_segments[col]):  # Check if the column is float
                        # Convert to int and format with thousands separator
                        row_values.append(f"{int(row[col]):,}" if pd.notna(row[col]) else 'N/A')
                    elif pd.api.types.is_numeric_dtype(row[col]):  # Other numeric types
                        row_values.append(f"{row[col]:,}")
                    else:
                        row_values.append(str(row[col]))
                table.add_row(*row_values)
            node.add(Group("Active Segments", table))

        
        # Calculate total CARR for the customer
        total_carr = active_segments['annualvalue'].sum()
        
        # Append to the main DataFrame
        df.loc[len(df)] = [customer, total_carr]
        
    # Set 'CustomerName' as the DataFrame index
    df.set_index('CustomerName', inplace=True)

    # Remove rows where CARR is zero depending on ignore_zeros flag
    if ignore_zeros:
        df = df[df['CARR'] != 0]

    total_carr = df['CARR'].sum()
    df.loc['Total CARR'] = total_carr

    # If tree_detail then print the tree
    if tree_detail:
        console = Console()
        console.print(root)

    return df


def generate_subscription_data_table(engine):
    """
    Generate a DataFrame with all generally required data from the database.
    """
    # Create SQL query
    query = text("""
    SELECT
    c.CustomerID AS "customer id",
    c.Name AS "customer name",
    con.ContractID AS "contract id",
    con.RenewalFromContractID AS "renewalfromcontractid",
    con.ContractDate AS "contractdate",
    con.TotalValue AS "totalvalue",
    seg.SegmentID AS "segmentid",
    seg.SegmentStartDate AS "segmentstartdate",
    seg.SegmentEndDate AS "segmentenddate",
    seg.ARROverrideStartDate AS "arroverridestartdate",
    seg.ARROverrideNote AS "arroverridenote",
    seg.SegmentValue AS "segmentvalue", 
    seg.Type AS "segmenttype"
    FROM
    Customers c
    JOIN
    Contracts con ON c.CustomerID = con.CustomerID
    JOIN
    Segments seg ON con.ContractID = seg.ContractID;
    """)
    # Execute query
    with engine.begin() as conn:
        result = conn.execute(query)
        src_df = result.fetchall()
        columns = result.keys()

    # Convert to DataFrame
    df = pd.DataFrame(src_df, columns=columns)
    
    # Convert date columns to datetime
    df['contractdate'] = pd.to_datetime(df['contractdate'])
    df['segmentstartdate'] = pd.to_datetime(df['segmentstartdate'])
    df['segmentenddate'] = pd.to_datetime(df['segmentenddate'])

    # Remove entries where segmenttype is not 'Subscription'
    df = df.loc[df['segmenttype'] == 'Subscription']
    
    # Add in column 'annualvalue', which is the segmentvalue divided by the number of months in the segment
    df['contractlength'] = (df['segmentenddate'].dt.year - df['segmentstartdate'].dt.year) * 12 + (df['segmentenddate'].dt.month - df['segmentstartdate'].dt.month)

    # Calculate the difference in days
    df['day_diff'] = (df['segmentenddate'].dt.day - df['segmentstartdate'].dt.day)
    
    # Adjust the month count based on day difference
    df['contractlength'] = np.where(df['day_diff'] > 15, df['contractlength'] + 1, df['contractlength'])
    df['contractlength'] = np.where(df['day_diff'] < -15, df['contractlength'] - 1, df['contractlength'])
    
    # Compute the annual value using the contract length
    df['annualvalue'] = df['segmentvalue'] / (df['contractlength'] / 12)
    
    # Optionally, you can drop the 'day_diff' column if you don't need it anymore
    df = df.drop('day_diff', axis=1)

    return df
