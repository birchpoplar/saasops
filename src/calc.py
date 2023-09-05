from src import utils
from src.classes import MessageStyle
from rich.console import Console
from datetime import date, timedelta
import dateutil.relativedelta as rd
import psycopg2
import pandas as pd
import logging
import calendar

def populate_bkings_carr_arr_df(start_date, end_date, connection):
    """Generate a DataFrame with Bookings, ARR and CARR for each month. NOTE: the day of the month on each of start_date and end_date is ignored in the creation of date_list that has end of month days only."""

    # Create a cursor
    cur = connection.cursor()

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

    for date in date_list:

        # Calculate Bookings
        som_date = date.replace(day=1)  # Start-of-month date
        bookings_sql = (
            f"SELECT SUM(c.TotalValue) "
            f"FROM Contracts c "
            f"WHERE c.ContractDate::DATE BETWEEN '{som_date}'::DATE AND '{date}'::DATE"
        )
        cur.execute(bookings_sql)
        bookings_value = cur.fetchone()[0]
        if bookings_value is None:
            bookings_value = 0
        df.at[date, 'Bookings'] = bookings_value

        # Create the SQL query for ARR
        arr_sql = (
            f"SELECT SUM(s.SegmentValue) "
            f"FROM Segments s "
            f"JOIN Contracts c ON s.ContractID = c.ContractID "
            f"WHERE s.Type = 'Subscription' "
            f"AND '{date}'::DATE BETWEEN c.TermStartDate::DATE AND s.SegmentEndDate::DATE"
        )
        # Debug print
        # print("Debug ARR SQL:", arr_sql)
        
        # Execute ARR SQL
        cur.execute(arr_sql)
        
        arr_value = cur.fetchone()[0]
        if arr_value is None:
            arr_value = 0
        df.at[date, 'ARR'] = arr_value
        
        # Create the SQL query for CARR
        carr_sql = (
            f"WITH RenewedContracts AS ("
            f"  SELECT ContractID, RenewalFromContractID, ContractDate "
            f"  FROM Contracts "
            f"  WHERE RenewalFromContractID IS NOT NULL"
            f"), "
            f"ValidContracts AS ("
            f"  SELECT c.ContractID "
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
        )
        
        # Debug print
        # print("Debug CARR SQL:", carr_sql)
        
        # Execute CARR SQL
        cur.execute(carr_sql)
        
        carr_value = cur.fetchone()[0]
        if carr_value is None:
            carr_value = 0
        df.at[date, 'CARR'] = carr_value
    
    # Close the cursor
    cur.close()
    
    return df


def populate_revenue_df(start_date, end_date, connection):
    """Populate a DataFrame with active revenue for each customer in each month."""

    # Create a cursor
    cur = connection.cursor()
    
    # Generate list of dates
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += rd.relativedelta(months=1)

    # Retrieve unique customer names from the Customers table
    cur.execute("SELECT DISTINCT Name FROM Customers")
    customer_names = [row[0] for row in cur.fetchall()]
        
    # Create empty DataFrame
    df = pd.DataFrame(index=date_list, columns=customer_names)
    
    # Populate DataFrame with active revenue
    for d in date_list:
        for customer in customer_names:
            cur.execute(
                f"SELECT SUM(s.SegmentValue) / 12 "
                f"FROM Segments s "
                f"JOIN Contracts c ON s.ContractID = c.ContractID "
                f"JOIN Customers cu ON c.CustomerID = cu.CustomerID "
                f"WHERE '{d}' BETWEEN s.SegmentStartDate AND s.SegmentEndDate "
                f"AND cu.Name = '{customer}'"
            )
            active_revenue = cur.fetchone()[0]
            if active_revenue is None:
                active_revenue = 0

            df.at[d, customer] = active_revenue

    cur.close()
    return df

def populate_metrics_df(start_date, end_date, connection):

    # Obtain the revenue DataFrame
    revenue_df = populate_revenue_df(start_date, end_date, connection)
    
    # Create a cursor
    cur = connection.cursor()
    
    # Generate list of dates
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += rd.relativedelta(months=1)

    # Retrieve unique customer names from the Customers table
    cur.execute("SELECT DISTINCT Name FROM Customers")
    customer_names = [row[0] for row in cur.fetchall()]

    # Create a second DataFrame for metrics
    metrics_df = pd.DataFrame(index=date_list, columns=["New MRR", "Churn MRR", "Expansion MRR", "Contraction MRR", "Starting MRR", "Ending MRR"])
   
    # Find the starting MRR figure
    prior_month_date = start_date - rd.relativedelta(months=1)
    prior_month_revenue_df = populate_revenue_df(prior_month_date, prior_month_date, connection)

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

    return metrics_df
