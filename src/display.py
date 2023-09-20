# Display functions

from rich.console import Console
from rich.text import Text
from rich.table import Table
from datetime import datetime
import pandas as pd
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
    
    print_status(console, "... accessing database", MessageStyle.INFO)
    with engine.connect() as conn:
        # Execute the SQL query to fetch data
        result = conn.execute(text("SELECT * FROM Customers;"))
    
        # Fetch all rows
        rows = result.fetchall()
    
    # Add rows to the Rich table
    print_status(console, "... compiling customer table", MessageStyle.INFO)
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
    table.add_column("Title", justify="left")
    table.add_column("Type", justify="left")
    table.add_column("Segment Value", justify="right")
    
    
    # Execute the SQL query to fetch data
    print_status(console, "... accessing database", MessageStyle.INFO)
    with engine.connect() as conn:
        query = text("""
        SELECT s.SegmentID, s.ContractID, c.RenewalFromContractID, cu.Name, c.ContractDate, s.SegmentStartDate, s.SegmentEndDate, s.Title, s.Type, s.SegmentValue
        FROM Segments s
        JOIN Contracts c ON s.ContractID = c.ContractID
        JOIN Customers cu ON c.CustomerID = cu.CustomerID;
        """)
        result = conn.execute(query)
    
    # Fetch all rows
    rows = result.fetchall()
    
    # Add rows to the Rich table
    print_status(console, "... compiling segment table", MessageStyle.INFO)
    for row in rows:
        segment_id, contract_id, renewal_from_contract_id, customer_name, contract_date, segment_start_date, segment_end_date, title, segment_type, segment_value = row
        table.add_row(
            str(segment_id), 
            str(contract_id),
            str(renewal_from_contract_id),
            customer_name,
            str(contract_date),
            str(segment_start_date), 
            str(segment_end_date), 
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

    print_status(console, "... accessing database", MessageStyle.INFO)
    with engine.connect() as conn:
        params = {"segment_id": segment_id}
        result = conn.execute(text("SELECT * FROM Segments WHERE SegmentID = :segment_id;"), params)

    # Fetch all rows
    row = result.fetchone()

    if row is None:
        console.print(f"Segment ID {segment_id} does not exist.")
        return

    print_status(console, "... compiling segment table", MessageStyle.INFO)
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

    print_status(console, "... accessing database", MessageStyle.INFO)
    with engine.connect() as conn:
        params = {"contract_id": contract_id}
        result = conn.execute(text("SELECT * FROM Contracts WHERE ContractID = :contract_id;"), params)

    # Fetch all rows
    row = result.fetchone()

    if row is None:
        console.print(f"Contract ID {contract_id} does not exist.")
        return

    print_status(console, "... compiling contract table", MessageStyle.INFO)
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

    print_status(console, "... accessing database", MessageStyle.INFO)
    with engine.connect() as conn:
        # Execute the SQL query to fetch data
        result = conn.execute(text("SELECT * FROM Contracts;"))
    
    # Fetch all rows
    rows = result.fetchall()

    # Add rows to the Rich table
    print_status(console, "... compiling contract table", MessageStyle.INFO)
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
    print_status(console, "... accessing database", MessageStyle.INFO)
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
        print_status(console, "... compiling invoice table", MessageStyle.INFO)
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

    print_status(console, "... compiling table", MessageStyle.INFO)
    table = Table(title=title, show_header=True, show_lines=True)
    
    # Add the "Customer" column for row titles (customer names)
    table.add_column("Customer", justify="right")
    
    # Convert datetime index to formatted strings and add as columns
    formatted_dates = [date.strftime("%b-%Y") for date in df.index]
    for formatted_date in formatted_dates:
        table.add_column(formatted_date, justify="right")
    
    # Add rows to the table
    print_status(console, "... adding table details", MessageStyle.INFO)
    for customer, row in transposed_df.iterrows():
        values = row.values
        formatted_values = [str(int(value)) for value in values]
        table.add_row(customer, *formatted_values)
    
    console.print(table)
    return True

def print_table(df, title, console: Console):
    print_status(console, "... compiling table", MessageStyle.INFO)
    table = Table(title=title, show_header=True, show_lines=True)
    
    # Add columns
    for column in df.columns:
        table.add_column(column, justify="right")
    
    # Add rows to the table
    print_status(console, "... adding table details", MessageStyle.INFO)
    for column, row in df.iterrows():
        values = row.values
        formatted_values = [str(value) for value in values]
        table.add_row(column, *formatted_values)
    
    console.print(table)
    return True
