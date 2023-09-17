from src import utils
from sqlalchemy import text
from src.classes import MessageStyle
from rich.console import Console
from datetime import date, timedelta
import dateutil.relativedelta as rd
import psycopg2
import pandas as pd
import logging
import calendar

def populate_bkings_carr_arr_df(start_date, end_date, engine, customer=None, contract=None):
    """Generate a DataFrame with Bookings, ARR and CARR for each month. NOTE: the day of the month on each of start_date and end_date is ignored in the creation of date_list that has end of month days only."""

    # Generate list of dates
    date_list = []
    current_date = start_date

    while current_date <= end_date:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        eom_date = current_date.replace(day=last_day)  # End-of-month date
        date_list.append(eom_date)
        
        # Add one month to get the next start_date
        current_date = eom_date + rd.relativedelta(days=1)

    # Create empty DataFrame with 'ARR' and 'CARR' columns
    df = pd.DataFrame(index=date_list, columns=['Bookings', 'ARR', 'CARR'])

    with engine.begin() as conn:
        for date in date_list:

            # define a common WHERE clause for customer and contract
            where_clause = ''
            if customer:
                where_clause += f" AND c.CustomerID = {customer} "
            if contract:
                where_clause += f" AND c.ContractID = {contract} "
            
            # Calculate Bookings
            som_date = date.replace(day=1)  # Start-of-month date
            bookings_sql = text(
                f"SELECT SUM(c.TotalValue) "
                f"FROM Contracts c "
                f"WHERE c.ContractDate::DATE BETWEEN '{som_date}'::DATE AND '{date}'::DATE"
                + where_clause
            )
            bookings_result = conn.execute(bookings_sql, {'som_date': som_date, 'eom_date': date}).fetchone()
            bookings_value = bookings_result[0] if bookings_result[0] is not None else 0
            df.at[date, 'Bookings'] = bookings_value

            # Create the SQL query for ARR
            arr_sql = text(
                f"SELECT SUM(s.SegmentValue) "
                f"FROM Segments s "
                f"JOIN Contracts c ON s.ContractID = c.ContractID "
                f"WHERE s.Type = 'Subscription' "
                f"AND '{date}'::DATE BETWEEN c.TermStartDate::DATE AND s.SegmentEndDate::DATE"
                + where_clause
            )
        
            # Execute ARR SQL
            arr_result = conn.execute(arr_sql, {'date': date}).fetchone()
            arr_value = arr_result[0] if arr_result[0] is not None else 0
            df.at[date, 'ARR'] = arr_value
        
            # Create the SQL query for CARR
            carr_sql = text(
                f"WITH RenewedContracts AS ("
                f"  SELECT ContractID, RenewalFromContractID, ContractDate "
                f"  FROM Contracts "
                f"  WHERE RenewalFromContractID IS NOT NULL"
                f"), "
                f"ValidContracts AS ("
                f"  SELECT c.ContractID, c.CustomerID "
                f"  FROM Contracts c "
                f"  LEFT JOIN Segments s ON c.ContractID = s.ContractID "
                f"  LEFT JOIN RenewedContracts r ON c.ContractID = r.RenewalFromContractID "
                f"  WHERE '{date}'::DATE <= COALESCE(r.ContractDate::DATE, '{date}'::DATE + 1) "
                f"  AND '{date}'::DATE BETWEEN c.ContractDate::DATE AND s.SegmentEndDate::DATE "
                f") "
                f"SELECT SUM(s.SegmentValue) "
                f"FROM Segments s "
                f"JOIN ValidContracts vc ON s.ContractID = vc.ContractID "
                f"WHERE s.Type = 'Subscription'"
                + where_clause.replace('c.', 'vc.')
            )
            
            carr_result = conn.execute(carr_sql, {'date': date}).fetchone()
            carr_value = carr_result[0] if carr_result[0] is not None else 0
            df.at[date, 'CARR'] = carr_value

    df = df.astype(float)
    df = df.round(1)
    return df


def populate_revenue_df(start_date, end_date, type, engine, customer=None, contract=None):
    """Populate a DataFrame with active revenue for each customer in each month. The days of the month on each of start_date and end_date are ignored in the creation of date_list that has middle or end of month days only, depending on the string value of type."""

    # Generate list of dates
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)

        if type == "mid":
            target_day = 15
        elif type == "end":
            target_day = last_day
        else:
            raise ValueError("type must be either 'mid' or 'end'")

        target_date = current_date.replace(day=target_day) 
        date_list.append(target_date)
        
        # Add one month to get the next start_date
        current_date = target_date + rd.relativedelta(months=1)

    # Create empty DataFrame
    df = pd.DataFrame(index=date_list)
    
    # Retrieve unique customer names from the Customers table
    with engine.begin() as conn:
        customer_names_str = ("SELECT DISTINCT Name FROM Customers")
        if customer is not None:
            customer_names_str += f" WHERE CustomerID = '{customer}'"

        customer_names_result = conn.execute(text(customer_names_str))
        customer_names = [row[0] for row in customer_names_result.fetchall()]
        
        # Populate DataFrame with active revenue
        for d in date_list:
            for customer in customer_names:
                query_str = (
                    f"SELECT SUM(s.SegmentValue) / 12 "
                    f"FROM Segments s "
                    f"JOIN Contracts c ON s.ContractID = c.ContractID "
                    f"JOIN Customers cu ON c.CustomerID = cu.CustomerID "
                    f"WHERE '{d}' BETWEEN s.SegmentStartDate AND s.SegmentEndDate "
                    f"AND cu.Name = '{customer}'"
                    f"AND s.Type = 'Subscription'"
                )

                # Add contract filter if specified
                if contract is not None:
                    query_str += f"AND c.ContractID = '{contract}'"

                query = text(query_str)                    
                active_revenue_result = conn.execute(query)
                active_revenue = active_revenue_result.fetchone()[0]
                
                if active_revenue is None:
                    active_revenue = 0
                    
                df.at[d, customer] = active_revenue

    df = df.astype(float)
    df = df.round(1)
    return df

def populate_metrics_df(start_date, end_date, engine, customer=None, contract=None):
    """Populate a DataFrame with metrics for each month in the date range. Note that the days of the month on each of start_date and end_date are ignored in the creation of date_list that has end of month days only."""
    
    # Obtain the revenue DataFrame
    revenue_df = populate_revenue_df(start_date, end_date, "end", engine, customer, contract)
    
    # Generate list of dates
    date_list = []
    current_date = start_date

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
                previous_month_revenue = revenue_df.loc[previous_month, customer]
                current_month_revenue = revenue_df.loc[d, customer]
                
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
                prior_month_revenue = prior_month_revenue_df.loc[prior_month_date, customer]
                current_month_revenue = revenue_df.loc[d, customer]
            
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
    return metrics_df

def customer_arr_df(date, engine):
    """Generate a DataFrame with ARR for each customer for a given date."""

    # Create an empty DataFrame
    df = pd.DataFrame(columns=['CustomerName', 'ARR'])
    
    with engine.begin() as conn:
        # Create the SQL query for ARR by Customer
        arr_by_customer_sql = text(
            f"SELECT cu.Name, SUM(s.SegmentValue) as ARR "
            f"FROM Segments s "
            f"JOIN Contracts c ON s.ContractID = c.ContractID "
            f"JOIN Customers cu ON c.CustomerID = cu.CustomerID "
            f"WHERE s.Type = 'Subscription' "
            f"AND '{date}'::DATE BETWEEN c.TermStartDate::DATE AND s.SegmentEndDate::DATE "
            f"GROUP BY cu.Name"
        )
         
        # Execute SQL to get ARR by customer
        arr_by_customer_result = conn.execute(arr_by_customer_sql, {'date': date}).fetchall()

        # Populate DataFrame
        for row in arr_by_customer_result:
            customer_name = row[0]
            arr_value = row[1] if row[1] is not None else 0
            df = pd.concat([df, pd.DataFrame([[customer_name, arr_value]], columns=['CustomerName', 'ARR'])])

    # Set 'CustomerName' as the DataFrame index
    df.set_index('CustomerName', inplace=True)

    total_arr = df['ARR'].sum()
    df.loc['Total ARR'] = total_arr
    
    return df


def customer_carr_df(date, engine):
    """Generate a DataFrame with CARR for each customer for a given date."""
    
    # Create an empty DataFrame
    df = pd.DataFrame(columns=['CustomerName', 'CARR'])
    
    with engine.begin() as conn:
        
        # Create the SQL query for CARR by Customer
        carr_by_customer_sql = text(
            f"WITH RenewedContracts AS ("
            f"  SELECT ContractID, RenewalFromContractID, ContractDate "
            f"  FROM Contracts "
            f"  WHERE RenewalFromContractID IS NOT NULL"
            f"), "
            f"ValidContracts AS ("
            f"  SELECT c.ContractID, cu.CustomerID "
            f"  FROM Contracts c "
            f"  LEFT JOIN Segments s ON c.ContractID = s.ContractID "
            f"  LEFT JOIN RenewedContracts r ON c.ContractID = r.RenewalFromContractID "
            f"  LEFT JOIN Customers cu ON c.CustomerID = cu.CustomerID "
            f"  WHERE '{date}'::DATE <= COALESCE(r.ContractDate::DATE, '{date}'::DATE + 1) "
            f"  AND '{date}'::DATE BETWEEN c.ContractDate::DATE AND s.SegmentEndDate::DATE "
            f") "
            f"SELECT cu.Name, SUM(s.SegmentValue) as CARR "
            f"FROM Segments s "
            f"JOIN ValidContracts vc ON s.ContractID = vc.ContractID "
            f"JOIN Customers cu ON vc.CustomerID = cu.CustomerID "
            f"WHERE s.Type = 'Subscription' "
            f"GROUP BY cu.Name"
        )
        
        # Execute SQL to get CARR by customer
        carr_by_customer_result = conn.execute(carr_by_customer_sql, {'date': date}).fetchall()

        # Populate DataFrame
        for row in carr_by_customer_result:
            customer_name = row[0]
            carr_value = row[1] if row[1] is not None else 0
            df = pd.concat([df, pd.DataFrame([[customer_name, carr_value]], columns=['CustomerName', 'CARR'])])
    
    # Set 'CustomerName' as the DataFrame index
    df.set_index('CustomerName', inplace=True)
    
    # Calculate and append the total CARR
    total_carr = df['CARR'].sum()
    df.loc['Total CARR'] = total_carr
    
    return df


def populate_customer_metrics_df(start_date, end_date, engine):
    # Obtain the revenue DataFrame (the function 'populate_revenue_df' is not shown in your code)
    revenue_df = populate_revenue_df(start_date, end_date, "end", engine)
    
    with engine.begin() as conn:
        # Retrieve unique customer names from the Customers table
        customer_names_sql = text("SELECT DISTINCT Name FROM Customers")
        customer_names_result = conn.execute(customer_names_sql)
        customer_names = [row[0] for row in customer_names_result.fetchall()]

    # Create a DataFrame for customer-based metrics
    metrics_df = pd.DataFrame(index=["New MRR", "Churn MRR", "Expansion MRR", "Contraction MRR"], columns=customer_names)
    
    # Initialize the metrics sums
    new_mrr_dict = {}
    churn_mrr_dict = {}
    expansion_mrr_dict = {}
    contraction_mrr_dict = {}

    # Calculate metrics for each customer
    for customer in customer_names:
        new_mrr_sum = 0
        churn_mrr_sum = 0
        expansion_mrr_sum = 0
        contraction_mrr_sum = 0
        
        # Loop through each date in the revenue_df DataFrame
        previous_date = None
        for d in revenue_df.index:
            current_month_revenue = revenue_df.loc[d, customer]
            
            if previous_date:
                previous_month_revenue = revenue_df.loc[previous_date, customer]
                
                new_mrr_sum += current_month_revenue if previous_month_revenue == 0 and current_month_revenue > 0 else 0
                churn_mrr_sum += previous_month_revenue if previous_month_revenue > 0 and current_month_revenue == 0 else 0
                expansion_mrr_sum += current_month_revenue - previous_month_revenue if current_month_revenue > previous_month_revenue and previous_month_revenue > 0 else 0
                contraction_mrr_sum += previous_month_revenue - current_month_revenue if current_month_revenue < previous_month_revenue and current_month_revenue > 0 else 0
                
            previous_date = d

        # Populate the metrics sums for each customer
        new_mrr_dict[customer] = new_mrr_sum
        churn_mrr_dict[customer] = churn_mrr_sum
        expansion_mrr_dict[customer] = expansion_mrr_sum
        contraction_mrr_dict[customer] = contraction_mrr_sum

    # Populate the DataFrame
    metrics_df.loc['New MRR'] = pd.Series(new_mrr_dict)
    metrics_df.loc['Churn MRR'] = pd.Series(churn_mrr_dict)
    metrics_df.loc['Expansion MRR'] = pd.Series(expansion_mrr_dict)
    metrics_df.loc['Contraction MRR'] = pd.Series(contraction_mrr_dict)

    return metrics_df
