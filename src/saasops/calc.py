import saasops.utils as utils
from saasops.classes import MessageStyle, SegmentData, SegmentContext
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

    # Build temp table in database of ARR data
    build_arr_table(con)

    # Query to sum ARR per customer and filter by date
    query = f"""
    SELECT cu.Name AS CustomerName, SUM(a.ARR) AS TotalARR
    FROM ARRTable a
    JOIN Segments s ON a.SegmentID = s.SegmentID
    JOIN Contracts c ON s.ContractID = c.ContractID
    JOIN Customers cu ON c.CustomerID = cu.CustomerID
    WHERE a.ARRStartDate <= '{date}' AND a.ARREndDate >= '{date}'
    GROUP BY cu.Name;
    """

    cursor = con.execute(query)
    df = cursor.fetchdf()

    df.set_index('CustomerName', inplace=True)

    if ignore_zeros:
        df = df[df['TotalARR'] != 0]
    
    delete_arr_table(con)
    
    return df


def customer_arr_df(start_date, end_date, con, timeframe='M', ignore_zeros=True):  
    final_df = pd.DataFrame()

    current_date = start_date
    while current_date <= end_date:
        period_start, period_end = calculate_timeframe(current_date, timeframe)
        period_end_str = period_end.strftime('%Y-%m-%d')

        # Build temp table in database of ARR data
        build_arr_table(con)

        # Query to sum ARR per customer for the period
        query = f"""
        SELECT cu.Name AS CustomerName, SUM(a.ARR) AS TotalARR
        FROM ARRTable a
        JOIN Segments s ON a.SegmentID = s.SegmentID
        JOIN Contracts c ON s.ContractID = c.ContractID
        JOIN Customers cu ON c.CustomerID = cu.CustomerID
        WHERE a.ARRStartDate <= '{period_end_str}' AND a.ARREndDate >= '{period_end_str}'
        GROUP BY cu.Name;
        """

        cursor = con.execute(query)
        df = cursor.fetchdf()
        df.set_index('CustomerName', inplace=True)

        delete_arr_table(con)

        if ignore_zeros:
            df = df[df['TotalARR'] != 0]

        # Format column name based on the timeframe
        column_name = format_column_name(period_end, timeframe)
        df.rename(columns={'TotalARR': column_name}, inplace=True)

        final_df = final_df.join(df, how='outer')

        current_date = (period_end + pd.Timedelta(days=1)).date()
    
    final_df.fillna(0, inplace=True)  # Replace NaN with 0
    return final_df


def new_arr_by_timeframe(date, con, timeframe="M", ignore_zeros=False):

    start_date, end_date = calculate_timeframe(date, timeframe)

    # Build temp table in database of ARR data
    build_arr_table(con)

    # Query to sum ARR per customer for segments where ARR start date is between start_date and end_date
    query = f"""
    SELECT cu.Name AS CustomerName, SUM(a.ARR) AS TotalNewARR
    FROM ARRTable a
    JOIN Segments s ON a.SegmentID = s.SegmentID
    JOIN Contracts c ON s.ContractID = c.ContractID
    JOIN Customers cu ON c.CustomerID = cu.CustomerID
    WHERE a.ARRStartDate BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY cu.Name;
    """

    cursor = con.execute(query)
    df = cursor.fetchdf()

    df.set_index('CustomerName', inplace=True)

    if ignore_zeros:
        df = df[df['TotalNewARR'] != 0]
    
    delete_arr_table(con)

    return df


def build_arr_table(con):
    """
    Build the ARR table in the database.
    """

    query = """
    SELECT s.SegmentID, s.ContractID, c.RenewalFromContractID, cu.Name, c.ContractDate, s.SegmentStartDate, s.SegmentEndDate, s.ARROverrideStartDate, s.Title, s.Type, s.SegmentValue
    FROM Segments s
    JOIN Contracts c ON s.ContractID = c.ContractID
    JOIN Customers cu ON c.CustomerID = cu.CustomerID;
    """

    result = con.execute(query)
    rows = result.fetchall()
    column_names = [desc[0] for desc in result.description]

    segment_data_list = []
    for row in rows:
        segment_data = SegmentData(*row)
        segment_data_list.append(segment_data)

    # Create ARR Table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ARRTable (
    SegmentID INT,
    ContractID INT,
    RenewalFromContractID INT,
    ARRStartDate DATE,
    ARREndDate DATE,
    ARR FLOAT
    );
    """
    con.execute(create_table_query)

    # Insert data into ARR Table
    for segment_data in segment_data_list:
        context = SegmentContext(segment_data)
        context.calculate_arr()

        renewal_from_contract_id_value = segment_data.renewal_from_contract_id if segment_data.renewal_from_contract_id else "NULL"
        
        insert_query = f"""
        INSERT INTO ARRTable (SegmentID, ContractID, RenewalFromContractID, ARRStartDate, ARREndDate, ARR)
        VALUES ({segment_data.segment_id}, {segment_data.contract_id}, {renewal_from_contract_id_value}, '{context.arr_start_date}', '{context.arr_end_date}', {context.arr});
        """
        con.execute(insert_query)

    # Second pass to update the ARREndDate for renewed contracts
    for segment_data in segment_data_list:
        if segment_data.renewal_from_contract_id:
            # Retrieve the renewing segment's ARR start date from the ARRTable
            renewing_arr_start_query = f"""
            SELECT ARRStartDate
            FROM ARRTable
            WHERE SegmentID = {segment_data.segment_id};
            """
            renewing_result = con.execute(renewing_arr_start_query)
            renewing_arr_start_date = renewing_result.fetchone()
            
            if renewing_arr_start_date:
                # Retrieve the renewed segment's ARR end date from the ARRTable
                # We are using the renewal_from_contract_id to find the linked segment's ARR end date
                renewed_segment_arr_end_query = f"""
                SELECT ARREndDate
                FROM ARRTable
                INNER JOIN Segments ON ARRTable.SegmentID = Segments.SegmentID
                WHERE Segments.ContractID = {segment_data.renewal_from_contract_id};
                """
                renewed_segment_result = con.execute(renewed_segment_arr_end_query)
                renewed_arr_end_date = renewed_segment_result.fetchone()
                
                if renewed_arr_end_date and (renewing_arr_start_date[0] - renewed_arr_end_date[0]).days > 1:
                    # Calculate the new ARREndDate for the renewed contract's segment
                    new_arr_end_date = renewing_arr_start_date[0] - timedelta(days=1)
                    # Prepare the update query to adjust the ARREndDate in the ARRTable for the renewed contract's segment
                    update_renewed_segment_query = f"""
                    UPDATE ARRTable
                    SET ARREndDate = '{new_arr_end_date}'
                    WHERE SegmentID = (
                    SELECT SegmentID
                    FROM Segments
                    WHERE ContractID = {segment_data.renewal_from_contract_id}
                    );
                    """
                    con.execute(update_renewed_segment_query)
                    
    print("ARRTable updated with renewed contracts.")

    print(con.execute("SELECT * FROM ARRTable;").fetchdf())

    return


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


def get_timeframe_title(date, timeframe):
    """
    Generate a title string for the table based on the given date and timeframe.

    Args:
        date (str): The date in the format 'YYYY-MM-DD'.
        timeframe (str): Either 'M' for month or 'Q' for quarter.

    Returns:
        str: A string representing the title for the table.
    """

    date_obj = datetime.strptime(date, '%Y-%m-%d').date()

    if timeframe == 'M':
        return date_obj.strftime('%B %Y')  # e.g., "January 2023"
    elif timeframe == 'Q':
        quarter = (date_obj.month - 1) // 3 + 1
        return f"Q{quarter} {date_obj.year}"
    else:
        raise ValueError("Invalid timeframe. It should be either 'M' or 'Q'")


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
