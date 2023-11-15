# Display functions

from rich.console import Console
from rich.text import Text
from rich.table import Table
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import text
from src.utils import print_status
from src.classes import MessageStyle
from src import classes, database, calc

# Database display functions

def print_customers(engine, console=None):

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
    
    with engine.connect() as conn:
        # Execute the SQL query to fetch data
        result = conn.execute(text("SELECT * FROM Customers;"))
    
        # Fetch all rows
        rows = result.fetchall()
    
    # Add rows to the Rich table
    for row in rows:
        customer_id, name, city, state = row
        table.add_row(str(customer_id), name, city, state)
        
    # Print the table to the console
    console.print(table)


def print_segments(engine, console=None):
    
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
    with engine.connect() as conn:
        query = text("""
        SELECT s.SegmentID, s.ContractID, c.RenewalFromContractID, cu.Name, c.ContractDate, s.SegmentStartDate, s.SegmentEndDate, s.ARROverrideStartDate, s.Title, s.Type, s.SegmentValue
        FROM Segments s
        JOIN Contracts c ON s.ContractID = c.ContractID
        JOIN Customers cu ON c.CustomerID = cu.CustomerID;
        """)
        result = conn.execute(query)
    
    # Fetch all rows
    rows = result.fetchall()
    
    # Add rows to the Rich table
    for row in rows:
        segment_id, contract_id, renewal_from_contract_id, customer_name, contract_date, segment_start_date, segment_end_date, arr_override_date, title, segment_type, segment_value = row
        table.add_row(
            str(segment_id), 
            str(contract_id),
            str(renewal_from_contract_id),
            customer_name,
            str(contract_date),
            str(segment_start_date), 
            str(segment_end_date),
            str(arr_override_date),
            title, 
            segment_type, 
            f"{segment_value:.2f}"
        )
        
    # Print the table to the console
    console.print(table)

def print_segment(engine, segment_id, console=None):
    if console is None:
        console = Console()

    # Initialize the Table
    table = Table(title=f"Segment ID {segment_id}")

    # Add columns
    table.add_column("Field", justify="left")
    table.add_column("Value", justify="right")

    with engine.connect() as conn:
        params = {"segment_id": segment_id}
        result = conn.execute(text("SELECT * FROM Segments WHERE SegmentID = :segment_id;"), params)

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
    

def print_contract(engine, contract_id, console=None):
    if console is None:
        console = Console()

    # Initialize the Table
    table = Table(title=f"Contract ID {contract_id}")

    # Add columns
    table.add_column("Field", justify="left")
    table.add_column("Value", justify="right")

    with engine.connect() as conn:
        params = {"contract_id": contract_id}
        result = conn.execute(text("SELECT * FROM Contracts WHERE ContractID = :contract_id;"), params)

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
        

def print_contracts(engine, console=None):
    
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

    with engine.connect() as conn:
        # Execute the SQL query to fetch data
        result = conn.execute(text("SELECT * FROM Contracts;"))
    
    # Fetch all rows
    rows = result.fetchall()

    # Add rows to the Rich table
    for row in rows:
        contract_id, customer_id, renewal_from_contract_id, reference, contract_date, term_start_date, term_end_date, total_value = row
        table.add_row(
            str(contract_id), 
            str(customer_id), 
            str(renewal_from_contract_id) if renewal_from_contract_id else 'N/A', 
            reference, 
            str(contract_date), 
            str(term_start_date), 
            str(term_end_date), 
            f"{total_value:.2f}"
        )
        
    # Print the table to the console
    console.print(table)
    
    
def print_invoices(engine, console=None):
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
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT c.Name, con.ContractID, s.SegmentID, i.InvoiceID, i.Number, i.Date, i.DaysPayable, i.Amount
            FROM Invoices i
            LEFT JOIN InvoiceSegments iseg ON i.InvoiceID = iseg.InvoiceID
            LEFT JOIN Segments s ON iseg.SegmentID = s.SegmentID
            LEFT JOIN Contracts con ON s.ContractID = con.ContractID
            LEFT JOIN Customers c ON con.CustomerID = c.CustomerID;
        """))
        
        # Fetch all rows
        rows = result.fetchall()
        
        # Add rows to the Rich table
        for row in rows:
            customer_name, contract_id, segment_id, invoice_id, invoice_number, invoice_date, days_payable, amount = row
            table.add_row(
                customer_name,
                str(contract_id),
                str(segment_id),
                str(invoice_id),
                invoice_number,
                str(invoice_date),
                str(days_payable),
                f"{amount:.2f}"
            )
            
    # Print the table to the console
    console.print(table)
    
    
# Dataframe display functions   

def print_dataframe(df, title, console: Console):
    # Transpose DataFrame so customer names become the row index
    transposed_df = df.transpose()

    table = Table(title=title, show_header=True, show_lines=True)
    
    # Add the "Customer" column for row titles (customer names)
    table.add_column("Customer", justify="right")
    
    # Convert datetime index to formatted strings and add as columns
    if isinstance(df.index[0], (pd.Timestamp, pd.DatetimeIndex)):
        formatted_dates = [date.strftime("%b-%Y") for date in df.index]
    else:
        formatted_dates = [str(date) for date in df.index]
        
    for formatted_date in formatted_dates:
        table.add_column(formatted_date, justify="right")
    
    # Add rows to the table
    for customer, row in transposed_df.iterrows():
        values = row.values
        formatted_values = [str(int(value)) for value in values]
        table.add_row(customer, *formatted_values)
    
    console.print(table)
    return True

def print_table(df, title, console: Console):

    # Print a message if the DataFrame is empty
    if df.empty:
        console.print(f"No data available for: {title}")
        return False
    
    table = Table(title=title, show_header=True, show_lines=True)
    
    # Ensure all columns are of type str
    df = df.astype(str)
    df.index = df.index.map(str)

    # Check if the DataFrame's index is a default integer index or named
    has_named_index = not isinstance(df.index[0], (int, np.integer))

    # Add columns
    if has_named_index:
        table.add_column(df.index.name or "Index")  # df.index.name or "Index" retrieves the index name, or uses "Index" if it's None
    for column in df.columns:
        table.add_column(column, justify="right")

    # Add rows to the table
    for _, row in df.iterrows():
        values = row.values
        formatted_values = [str(value) for value in values]
        if has_named_index:
            table.add_row(_, *formatted_values)  # If it has a named index, add the index as the first value
        else:
            table.add_row(*formatted_values)

    console.print(table)
    return True

def print_contract_details(engine, contract_id, console=None):
    if console is None:
        console = Console()
    
    # Print Contract Details
    with engine.connect() as conn:
        contract_query = text("""
            SELECT ContractID, CustomerID, RenewalFromContractID, ContractDate, TermStartDate, TermEndDate, TotalValue
            FROM Contracts
            WHERE ContractID = :contract_id
        """)
        
        contract_result = conn.execute(contract_query, {'contract_id': contract_id})
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

    with engine.connect() as conn:
        segment_query = text("""
            SELECT SegmentID, SegmentStartDate, SegmentEndDate, Title, Type, SegmentValue
            FROM Segments
            WHERE ContractID = :contract_id
        """)

        segment_result = conn.execute(segment_query, {'contract_id': contract_id})
        
        for row in segment_result:
            segment_id, segment_start_date, segment_end_date, title, segment_type, segment_value = row
            segment_table.add_row(str(segment_id), str(segment_start_date), str(segment_end_date), title, segment_type, f"{segment_value:.2f}")
            total_segment_value += segment_value
    
    console.print(segment_table)
    console.print(f"Total Segment Value: {total_segment_value:.2f}")


def print_contracts_without_segments(engine, console=None):
    """
    Find and print contracts that have no segments referring to them.

    Args:
        engine (sqlalchemy.engine): The SQLAlchemy engine to use for database access.

    Returns:
        result (str): A string indicating the contracts that have no segments.
    """

    with engine.begin() as conn:
        query = text("""
        SELECT c.ContractID, c.Reference
        FROM Contracts c
        LEFT JOIN Segments s ON c.ContractID = s.ContractID
        WHERE s.ContractID IS NULL;
        """)
        result = conn.execute(query)
        
        # Fetch all rows where there's no segment corresponding to the contract
        contracts_without_segments = result.fetchall()

        if len(contracts_without_segments) == 0:
            console.print("All contracts have corresponding segments.")
        else:
            contracts_info = "\n".join([f"ContractID: {row[0]}, Reference: {row[1]}" for row in contracts_without_segments])
            console.print(f"Contracts without segments:\n{contracts_info}")

    return
        
