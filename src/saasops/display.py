# Display functions

from rich.console import Console
from rich.text import Text
from rich.table import Table
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import text
import saasops.utils as utils
import saasops.database as database
import saasops.calc as calc
from saasops.classes import MessageStyle


# Database display functions

def print_customers(con, console=None):

    # If no console object is provided, create a new one
    if console is None:
        console = Console()
        
    # Initialize the Table
    table = Table(title="Customers")
    
    # Add columns
    table.add_column("Customer ID", justify="right")
    table.add_column("Name", justify="left")
    table.add_column("City", justify="left")
    table.add_column("State", justify="left")
    
    # Execute the SQL query to fetch data
    result = con.execute("SELECT * FROM Customers;")  # Adjusted this line
    
    # Fetch all rows
    rows = result.fetchall()
    
    # Add rows to the Rich table
    for row in rows:
        customer_id, name, city, state = row
        table.add_row(str(customer_id), name, city, state)
        
    # Print the table to the console
    console.print(table)


def print_segments(con, console=None, sort_column=None):
    
    # If no console object is provided, create a new one
    if console is None:
        console = Console()
    
    # Initialize the Table
    table = Table(title=f"Segments for all Customers")
    
    # Add columns
    table.add_column("Segment ID", justify="right")
    table.add_column("Contract ID", justify="right")
    table.add_column("Renew frm ID", justify="right")
    table.add_column("Customer Name", justify="left")
    table.add_column("Contract Date", justify="right")
    table.add_column("Segment Start Date", justify="right")
    table.add_column("Segment End Date", justify="right")
    table.add_column("ARR Override Start Date", justify="right")
    table.add_column("Title", justify="left")
    table.add_column("Type", justify="left")
    table.add_column("Segment Value", justify="right")
    
    # Execute the SQL query to fetch data
    query = """
    SELECT s.SegmentID, s.ContractID, c.RenewalFromContractID, cu.Name, c.ContractDate, s.SegmentStartDate, s.SegmentEndDate, s.ARROverrideStartDate, s.Title, s.Type, s.SegmentValue
    FROM Segments s
    JOIN Contracts c ON s.ContractID = c.ContractID
    JOIN Customers cu ON c.CustomerID = cu.CustomerID;
    """

    result = con.execute(query)

    # Fetch all rows
    rows = result.fetchall()

    # Get column names
    column_names = [desc[0] for desc in result.description]

    # Create a dataframe from the rows
    df = pd.DataFrame(rows, columns=column_names)

    # Sort the dataframe by the specified column
    if sort_column is not None and sort_column in df.columns:
        df = df.sort_values(by=sort_column)
        
    # Add rows to the Rich table
    for row in rows:
        table.add_row(
            str(row[column_names.index('SegmentID')]), 
            str(row[column_names.index('ContractID')]),
            str(int(row[column_names.index('RenewalFromContractID')])) if row[column_names.index('RenewalFromContractID')] else 'N/A',
            row[column_names.index('Name')],
            str(row[column_names.index('ContractDate')]),
            str(row[column_names.index('SegmentStartDate')]), 
            str(row[column_names.index('SegmentEndDate')]),
            str(row[column_names.index('ARROverrideStartDate')]) if row[column_names.index('ARROverrideStartDate')] else 'N/A',
            row[column_names.index('Title')], 
            row[column_names.index('Type')], 
            f"{row[column_names.index('SegmentValue')]:.2f}"
        )

    # Print the table to the console
    console.print(table)


def print_segment(con, segment_id, console=None):
    if console is None:
        console = Console()

    # Initialize the Table
    table = Table(title=f"Segment ID {segment_id}")

    # Add columns
    table.add_column("Field", justify="left")
    table.add_column("Value", justify="right")

    params = {"segment_id": segment_id}
    result = con.execute(text("SELECT * FROM Segments WHERE SegmentID = :segment_id;"), params)

    # Fetch all rows
    row = result.fetchone()

    if row is None:
        console.print(f"Segment ID {segment_id} does not exist.")
        return

    column_names = result.keys()
    for field, value in zip(column_names, row):
        table.add_row(field, str(value))

    # Print the table to the console
    console.print(table)
    

def print_contract(con, contract_id, console=None):
    if console is None:
        console = Console()

    # Initialize the Table
    table = Table(title=f"Contract ID {contract_id}")

    # Add columns
    table.add_column("Field", justify="left")
    table.add_column("Value", justify="right")

    params = {"contract_id": contract_id}
    result = con.execute(text("SELECT * FROM Contracts WHERE ContractID = :contract_id;"), params)

    # Fetch all rows
    row = result.fetchone()

    if row is None:
        console.print(f"Contract ID {contract_id} does not exist.")
        return

    column_names = result.keys()
    for field, value in zip(column_names, row):
        table.add_row(field, str(value))

    # Print the table to the console
    console.print(table)
        

def print_contracts(con, console=None, sort_column=None):
    
    # If no console object is provided, create a new one
    if console is None:
        console = Console()
    
    # Initialize the Table
    table = Table(title=f"Contracts for all Customers")
    
    # Add columns
    table.add_column("Contract ID", justify="right")
    table.add_column("Customer ID", justify="right")
    table.add_column("Renewal ID", justify="right")
    table.add_column("Reference", justify="left")
    table.add_column("Contract Date", justify="right")
    table.add_column("Term Start Date", justify="right")
    table.add_column("Term End Date", justify="right")
    table.add_column("Total Value", justify="right")

    # Execute the SQL query to fetch data
    result = con.execute(text("SELECT * FROM Contracts;"))
    # Convert the result object to a dataframe
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

    # Sort the dataframe by the specified column
    if sort_column is not None and sort_column in df.columns:
        df = df.sort_values(by=sort_column)

    # Add rows to the Rich table
    for row in df.itertuples(index=False):
        renewalid = 'N/A' if pd.isna(row.renewalfromcontractid) else str(int(row.renewalfromcontractid))
        table.add_row(
            str(row.contractid), 
            str(row.customerid),
            renewalid,
            row.reference, 
            str(row.contractdate), 
            str(row.termstartdate), 
            str(row.termenddate), 
            f"{row.totalvalue:.2f}"
        )

    # Print the table to the console
    console.print(table)
    

def print_invoices(con, console=None, sort_column=None):
    # If no console object is provided, create a new one
    if console is None:
        console = Console()
    
    # Initialize the Table
    table = Table(title="Invoices for all Customers")
    
    # Add columns
    table.add_column("Customer Name", justify="left")
    table.add_column("Contract ID", justify="right")
    table.add_column("Segment ID", justify="right")
    table.add_column("Invoice ID", justify="right")
    table.add_column("Invoice Number", justify="left")
    table.add_column("Invoice Date", justify="right")
    table.add_column("Days Payable", justify="right")
    table.add_column("Amount", justify="right")
    
    # Execute the SQL query to fetch data
    result = con.execute(text("""
    SELECT c.Name, con.ContractID, s.SegmentID, i.InvoiceID, i.Number, i.Date, i.DaysPayable, i.Amount
    FROM Invoices i
    LEFT JOIN InvoiceSegments iseg ON i.InvoiceID = iseg.InvoiceID
    LEFT JOIN Segments s ON iseg.SegmentID = s.SegmentID
    LEFT JOIN Contracts con ON s.ContractID = con.ContractID
    LEFT JOIN Customers c ON con.CustomerID = c.CustomerID;
    """))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

    # Sort the dataframe by the specified column
    if sort_column is not None and sort_column in df.columns:
        df = df.sort_values(by=sort_column)
        
    # Add rows to the Rich table
    for row in df.itertuples(index=False):
        table.add_row(
            row.name,
            str(row.contractid),
            str(row.segmentid),
            str(row.invoiceid),
            row.number,
            row.date.strftime('%Y-%m-%d') if row.date else 'N/A',
            str(row.dayspayable),
            f"{row.amount:.2f}"
        )

    # Print the table to the console
    console.print(table)   

    
# Dataframe display functions   

def print_combined_table(df, title, console: Console, format_type='dollar', transpose=False, lh_column_title='Customer'):
    if df.empty:
        console.print(f"No data available for: {title}")
        return False

    table = Table(title=title, show_header=True, show_lines=True)

    if transpose:
        df = df.transpose()

    # Add the left-hand column
    table.add_column(lh_column_title, justify="right")

    # Add the remaining columns
    for column in df.columns:
        table.add_column(column, justify="right")

    # Add rows to the table
    for index, row in df.iterrows():
        row_data = [str(index)] + [format_value(value, format_type) for value in row.values]
        table.add_row(*row_data)

    console.print(table)
    return True


# def print_dataframe(df, title, console: Console, lh_column_title='Customer'):
#     # Transpose DataFrame so the column names become the row index
#     transposed_df = df.transpose()

#     table = Table(title=title, show_header=True, show_lines=True)
    
#     # Add the left hand column for row titles, the title of which depends on the source dataframe content
#     table.add_column(lh_column_title, justify="right")
    
#     # Convert datetime index to formatted strings and add as columns
#     if isinstance(df.index[0], (pd.Timestamp, pd.DatetimeIndex)):
#         formatted_dates = [date.strftime("%b-%Y") for date in df.index]
#     else:
#         formatted_dates = [str(date) for date in df.index]
        
#     for formatted_date in formatted_dates:
#         table.add_column(formatted_date, justify="right")
    
#     # Add rows to the table
#     for column, row in transposed_df.iterrows():
#         values = row.values
#         formatted_values = ['{:,}'.format(int(value)) if isinstance(value, (int, float)) else value for value in values]
#         #formatted_values = [str(int(value)) for value in values]
#         table.add_row(column, *formatted_values)
    
#     console.print(table)
#     return True


def print_contract_details(con, contract_id, console=None):
    if console is None:
        console = Console()
    
    # Print Contract Details
    contract_query = text("""
    SELECT ContractID, CustomerID, RenewalFromContractID, ContractDate, TermStartDate, TermEndDate, TotalValue
    FROM Contracts
    WHERE ContractID = :contract_id
    """)
        
    contract_result = con.execute(contract_query, {'contract_id': contract_id})
    contract_row = contract_result.fetchone()
    
    if contract_row is None:
        console.print(f"No contract found for Contract ID: {contract_id}")
        return
        
    contract_id, customer_id, renewal_from_contract_id, contract_date, term_start_date, term_end_date, total_value = contract_row

    console.print(f"Contract ID: {contract_id}")
    console.print(f"Customer ID: {customer_id}")
    console.print(f"Renewal From Contract ID: {renewal_from_contract_id}")
    console.print(f"Contract Date: {contract_date}")
    console.print(f"Term Start Date: {term_start_date}")
    console.print(f"Term End Date: {term_end_date}")
    console.print(f"Total Contract Value: {total_value}")

    # Print Segment Details
    segment_table = Table(title="Segments for Contract ID: " + str(contract_id))
    segment_table.add_column("Segment ID")
    segment_table.add_column("Segment Start Date")
    segment_table.add_column("Segment End Date")
    segment_table.add_column("Title")
    segment_table.add_column("Type")
    segment_table.add_column("Segment Value")

    total_segment_value = 0

    segment_query = text("""
    SELECT SegmentID, SegmentStartDate, SegmentEndDate, Title, Type, SegmentValue
    FROM Segments
    WHERE ContractID = :contract_id
    """)

    segment_result = con.execute(segment_query, {'contract_id': contract_id})
        
    for row in segment_result:
        segment_id, segment_start_date, segment_end_date, title, segment_type, segment_value = row
        segment_table.add_row(str(segment_id), str(segment_start_date), str(segment_end_date), title, segment_type, f"{segment_value:.2f}")
        total_segment_value += segment_value
    
    console.print(segment_table)
    console.print(f"Total Segment Value: {total_segment_value:.2f}")


def print_contracts_without_segments(con, console=None):
    """
    Find and print contracts that have no segments referring to them.

    Args:
        engine (sqlalchemy.engine): The SQLAlchemy engine to use for database access.

    Returns:
        result (str): A string indicating the contracts that have no segments.
    """

    query = text("""
    SELECT c.ContractID, c.Reference
    FROM Contracts c
    LEFT JOIN Segments s ON c.ContractID = s.ContractID
    WHERE s.ContractID IS NULL;
    """)
    result = con.execute(query)
        
    # Fetch all rows where there's no segment corresponding to the contract
    contracts_without_segments = result.fetchall()

    if len(contracts_without_segments) == 0:
        console.print("All contracts have corresponding segments.")
    else:
        contracts_info = "\n".join([f"ContractID: {row[0]}, Reference: {row[1]}" for row in contracts_without_segments])
        console.print(f"Contracts without segments:\n{contracts_info}")

    return


# Helper functions

def generate_title(base_title, start_date, end_date, timeframe, format_type, customer=None, contract=None):
    title = f'{base_title}, {start_date.strftime("%b %d, %Y")} to {end_date.strftime("%b %d, %Y")}, Frequency: {timeframe}'

    # Append unit indication based on format_type
    if format_type == 'thousand':
        title += ' ($k)'  # or ' (000s)' based on your preference

    if customer:
        title += f', Customer: {customer}'
    if contract:
        title += f', Contract: {contract}'
    return title


def format_value(value, format_type='dollar'):
    if pd.isna(value):
        return '0'
    elif isinstance(value, (int, float)):
        if format_type == 'dollar':
            return '{:,.0f}'.format(value)  # Rounded to the nearest dollar
        elif format_type == 'cent':
            return '{:,.2f}'.format(value)  # Rounded to cents
        elif format_type == 'thousand':
            return '{:,.0f}'.format(value / 1000)  # Divide by 1000 and round to the nearest
        else:
            raise ValueError("Invalid format type. Choose 'dollar', 'cent', or 'thousand'.")
    else:
        return str(value)
