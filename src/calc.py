from src.display import print_status
from src.classes import MessageStyle
from rich.console import Console
from datetime import date, timedelta
import dateutil.relativedelta as rd
import psycopg2
import pandas as pd
import logging

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
