import saasops.utils as utils
from saasops.classes import MessageStyle, SegmentData, SegmentContext, ARRStartDateDecisionTable, ARRMetricsCalculator, ARRTable
from sqlalchemy import text
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


# ARR Calculation Functions

def customer_arr_tbl(date, con, ignore_zeros=False, tree_detail=False):
    # Convert the date to a pandas Timestamp
    date_as_timestamp = pd.to_datetime(date)

    # Build the ARR table instance (which now uses a DataFrame)
    arr_table = build_arr_table(con)

    # print(f"ARR Table: {arr_table.data.shape[0]} rows")
    # print(f"ARR Table Columns: {arr_table.data.columns}")
    # print(f"ARR Table Data Types: {arr_table.data.dtypes}")
    # print(f"ARR Table Data: {arr_table.data}")
    
    active_segments = arr_table.data[(arr_table.data['ARRStartDate'] <= date_as_timestamp) & (arr_table.data['ARREndDate'] >= date_as_timestamp)]
    has_renewal = active_segments['ContractID'].isin(active_segments['RenewalFromContractID'].dropna())
    active_segments = active_segments[~has_renewal]
    # print(active_segments)

    # Sum ARR per customer
    df = active_segments.groupby('CustomerName')['ARR'].sum().reset_index()
    df.rename(columns={'ARR': 'TotalARR'}, inplace=True)
    df.set_index('CustomerName', inplace=True)

    if ignore_zeros:
        df = df[df['TotalARR'] != 0]

    # Add a total ARR sum as last row
    df.loc['Total'] = df.sum()

    return df


def customer_arr_df(start_date, end_date, con, timeframe='M', ignore_zeros=True):  
    final_df = pd.DataFrame()

    current_date = start_date
    while current_date <= end_date:
        period_start, period_end = calculate_timeframe(current_date, timeframe)
        period_end_timestamp = pd.to_datetime(period_end.strftime('%Y-%m-%d'))

        # Build temp table in database of ARR data
        arr_table = build_arr_table(con)
        # print(f"ARR Table: {arr_table.data.shape[0]} rows")
        # print(f"ARR Table Data: {arr_table.data}")
        
        # Filter active segments for the period
        if not arr_table.data.empty:
            active_segments = arr_table.data[
                (arr_table.data['ARRStartDate'] <= period_end_timestamp) &
                (arr_table.data['ARREndDate'] >= period_end_timestamp)
            ]
            has_renewal = active_segments['ContractID'].isin(active_segments['RenewalFromContractID'].dropna())
            active_segments = active_segments[~has_renewal]

            # print("Period Start:", period_start)
            # print("Period End:", period_end)
            # print(active_segments)
        
            # Sum ARR per customer for the period
            if not active_segments.empty:
                df = active_segments.groupby('CustomerName')['ARR'].sum().reset_index()
                df.set_index('CustomerName', inplace=True)
        
                if ignore_zeros:
                    df = df[df['ARR'] != 0]

                # Format column name based on the timeframe
                column_name = format_column_name(period_end, timeframe)
                df.rename(columns={'ARR': column_name}, inplace=True)

                # Join the dataframes
                if final_df.empty:
                    final_df = df
                else:
                    final_df = final_df.join(df, how='outer')

            else:
                # Handle the case where active_segments is empty after filtering
                if final_df.empty:
                    # Initialize final_df with the correct column if it's the first iteration
                    final_df = pd.DataFrame(columns=[format_column_name(period_end, timeframe)])
                else:
                    # If final_df is not empty but no active segments in this period, ensure the column is added
                    final_df[format_column_name(period_end, timeframe)] = 0
        
        current_date = (period_end + pd.Timedelta(days=1)).date()
    
    final_df.fillna(0, inplace=True)  # Replace NaN with 0

    # Add a row that sums ARR per period
    if not final_df.empty:
        final_df.loc['Total ARR'] = final_df.sum()

    return final_df


def new_arr_by_timeframe(date, con, timeframe="M", ignore_zeros=False):
    start_date, end_date = calculate_timeframe(date, timeframe)
    start_timestamp = pd.to_datetime(start_date)
    end_timestamp = pd.to_datetime(end_date)

    # Build the ARR table instance (which now uses a DataFrame)
    arr_table = build_arr_table(con)

    # Filter for segments with ARR start date within the specified period
    new_segments = arr_table.data[
        (arr_table.data['ARRStartDate'] >= start_timestamp) & 
        (arr_table.data['ARRStartDate'] <= end_timestamp)
    ]

    # Exclude segments that are renewals
    new_segments = new_segments[new_segments['RenewalFromContractID'].isna()]

    # Sum new ARR per customer
    df = new_segments.groupby('CustomerName')['ARR'].sum().reset_index()
    df.rename(columns={'ARR': 'TotalNewARR'}, inplace=True)
    df.set_index('CustomerName', inplace=True)

    if ignore_zeros:
        df = df[df['TotalNewARR'] != 0]

    # Add a total ARR sum as last row
    df.loc['Total'] = df.sum()

    return df


def build_arr_change_df(start_date, end_date, con, freq='M'):
    arr_table = build_arr_table(con)
    
    periods = generate_periods(start_date, end_date, freq)
    # columns = [f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}" for start, end in periods]
    columns = [format_column_name(start, freq) for start, end in periods]
    df = pd.DataFrame(index=["Beginning ARR", "New", "Expansion", "Contraction", "Churn", "Ending ARR"], columns=columns)

    # Calculate previous ending ARR, this will be used as the beginning ARR for the first period
    # Have to calculate this before the loop, because it will be used as the beginning ARR for the first period
    # But it is effectively the execution of the loop but for prior period
    # use the customer_arr_tbl function to calculate the ARR for the previous period
    previous_start, previous_end = periods[0]
    previous_end = previous_start - timedelta(days=1)
    # The customer ARR table has a Total row at the bottom of column TotalARR, so we can use that to get the previous ending ARR
    previous_ending_arr = customer_arr_tbl(previous_end, con).loc['Total', 'TotalARR']

    # Set beginning ARR for the first period
    df.at['Beginning ARR', columns[0]] = previous_ending_arr

    carry_forward_churn = []    

    for i, (start, end) in enumerate(periods):
        arr_calculator = ARRMetricsCalculator(arr_table, start, end)

        # Set the beginning ARR for the period
        beginning_arr = previous_ending_arr

        carry_forward_churn = arr_calculator.calculate_arr_changes(carry_forward_churn)

        # Calculate the ending ARR for the period, by adding New + Expansion and subtracting Contraction + Churn
        calculated_ending_arr = beginning_arr + arr_calculator.metrics['New'] + arr_calculator.metrics['Expansion'] - arr_calculator.metrics['Contraction'] - arr_calculator.metrics['Churn']
        
        # Populate the DataFrame for each period
        df.at['Beginning ARR', columns[i]] = beginning_arr
        df.at['New', columns[i]] = arr_calculator.metrics['New']
        df.at['Expansion', columns[i]] = arr_calculator.metrics['Expansion']
        df.at['Contraction', columns[i]] = arr_calculator.metrics['Contraction']
        df.at['Churn', columns[i]] = arr_calculator.metrics['Churn']
        df.at['Ending ARR', columns[i]] = calculated_ending_arr

        previous_ending_arr = calculated_ending_arr
        arr_calculator.reset_metrics()

    return df


def build_arr_table(con):
    # Retrieve segment data from the database
    query = """
    SELECT s.SegmentID, s.ContractID, c.RenewalFromContractID, cu.Name, c.ContractDate, 
           s.SegmentStartDate, s.SegmentEndDate, s.ARROverrideStartDate, 
           s.Title, s.Type, s.SegmentValue
    FROM Segments s
    JOIN Contracts c ON s.ContractID = c.ContractID
    JOIN Customers cu ON c.CustomerID = cu.CustomerID;
    """
    result = con.execute(query)
    rows = result.fetchall()

    arr_table = ARRTable()

    for row in rows:
        segment_data = SegmentData(*row)
        context = SegmentContext(segment_data)
        context.calculate_arr()
        arr_table.add_row(segment_data, context)

    arr_table.update_for_renewal_contracts()

    return arr_table


def delete_arr_table(con):
    """
    Deletes the ARRTable from the database.
    """
    
    delete_table_query = "DROP TABLE IF EXISTS ARRTable;"
    con.execute(delete_table_query)
    print("ARRTable deleted.")
    return 


# Bookings calculation functions

def customer_bkings_tbl(date, con, timeframe='M', ignore_zeros=True, tree_detail=False):  

    # Calculate the start and end dates for the given timeframe
    start_date, end_date = calculate_timeframe(date, timeframe)
    
    # Query contracts table to get all contracts that were signed in the given timeframe
    query = f"""
    SELECT cu.Name AS CustomerName, SUM(c.TotalValue) AS TotalNewBookings
    FROM Contracts c
    JOIN Customers cu ON c.CustomerID = cu.CustomerID
    WHERE c.ContractDate BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY cu.Name;
    """
    
    cursor = con.execute(query)
    df = cursor.fetchdf()

    df.set_index('CustomerName', inplace=True)

    if ignore_zeros:
        df = df[df['TotalNewBookings'] != 0]
     
    return df

def customer_bkings_df(start_date, end_date, con, timeframe='M', ignore_zeros=True):  
    # Create an empty DataFrame for the final results
    final_df = pd.DataFrame()

    current_date = start_date
    while current_date <= end_date:
        # Calculate the start and end dates for the current period
        period_start, period_end = calculate_timeframe(current_date, timeframe)

        # Format period_start and period_end as date strings without time components
        # This is necessary for the SQL query with the DuckDB database
        period_start_str = period_start.strftime('%Y-%m-%d')
        period_end_str = period_end.strftime('%Y-%m-%d')
        
        # Query to get data for the current period
        query = f"""
        SELECT cu.Name AS CustomerName, SUM(c.TotalValue) AS TotalNewBookings
        FROM Contracts c
        JOIN Customers cu ON c.CustomerID = cu.CustomerID
        WHERE c.ContractDate BETWEEN '{period_start_str}' AND '{period_end_str}'
        GROUP BY cu.Name;
        """

        cursor = con.execute(query)
        df = cursor.fetchdf()
        df.set_index('CustomerName', inplace=True)

        print(period_start, period_end)
        print(df)
        
        if ignore_zeros:
            df = df[df['TotalNewBookings'] != 0]

        # Format column name based on the timeframe
        column_name = format_column_name(period_start, timeframe)
        df.rename(columns={'TotalNewBookings': column_name}, inplace=True)

        final_df = final_df.join(df, how='outer')

        current_date = (period_end + pd.Timedelta(days=1)).date()
        
    final_df.fillna(0, inplace=True)  # Replace NaN with 0

    return final_df


# Date & text helper functions

def calculate_timeframe(date, timeframe):
    date_datetime = pd.Timestamp(date)

    if timeframe == 'M':
        start_date = date_datetime.replace(day=1)
        end_date = start_date + pd.offsets.MonthEnd(1)
    elif timeframe == 'Q':
        quarter_mapping = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
        q = (date_datetime.month - 1) // 3 + 1
        start_month, end_month = quarter_mapping[q]
        start_date = date_datetime.replace(month=start_month, day=1)
        end_date = date_datetime.replace(month=end_month).replace(day=1) + pd.offsets.MonthEnd(1)
    else:
        raise ValueError("Invalid timeframe. It should be either 'M' for month or 'Q' for quarter")

    return start_date, end_date


def get_timeframe_title(date_input, timeframe):
    """
    Generates a title for the table based on the date and timeframe.

    Args:
        date_input (str or date): The date for which to generate the title.
        timeframe (str): The timeframe ('M' for month, 'Q' for quarter, etc.).

    Returns:
        str: A string representing the title for the table.
    """
    # Check if date_input is a string and convert to date if necessary
    if isinstance(date_input, str):
        date_obj = datetime.strptime(date_input, '%Y-%m-%d').date()
    elif isinstance(date_input, date):  # Corrected usage of date type
        date_obj = date_input
    else:
        raise ValueError("Date must be a string or a datetime.date object")

    # Format the date based on the timeframe
    if timeframe == 'M':
        return date_obj.strftime('%B %Y')  # e.g., "January 2023"
    elif timeframe == 'Q':
        quarter = (date_obj.month - 1) // 3 + 1
        return f"Q{quarter} {date_obj.year}"
    else:
        # Handle other timeframe formats or raise an error for unsupported ones
        raise ValueError("Unsupported timeframe specified")\
    

def format_column_name(period_start, timeframe):
    if timeframe == 'M':
        # Monthly: Format as "Jan 2024", "Feb 2024", etc.
        return period_start.strftime("%b %Y")
    elif timeframe == 'Q':
        # Quarterly: Format as "Q1 2024", "Q2 2024", etc.
        quarter = (period_start.month - 1) // 3 + 1
        return f"Q{quarter} {period_start.year}"
    else:
        raise ValueError("Invalid timeframe. Use 'M' for monthly or 'Q' for quarterly.")


def generate_periods(start_date, end_date, freq='M'):
    """
    Generate periods between start_date and end_date with given frequency ('M' for months, 'Q' for quarters).
    """
    # Adjust the start date to the first day of the month or quarter
    if freq == 'M':
        adjusted_start_date = start_date - pd.offsets.MonthBegin(n=1)
    elif freq == 'Q':
        adjusted_start_date = start_date - pd.offsets.QuarterBegin(startingMonth=1, n=1)
    else:
        raise ValueError("Frequency must be 'M' for months or 'Q' for quarters.")

    # Generate the periods
    periods = pd.date_range(start=adjusted_start_date, end=end_date, freq=freq)

    return [(start + timedelta(days=1), start + timedelta(days=(end - start).days)) for start, end in zip(periods, periods[1:])]
