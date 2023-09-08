# Display functions

from rich.console import Console
from rich.text import Text
from rich.table import Table
from datetime import datetime
import pandas as pd

from src import classes, database, calc

# Database display functions

def print_customers(connection, console=None):

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
    
    # Create a cursor
    cur = connection.cursor()
    
    # Execute the SQL query to fetch data
    cur.execute("SELECT * FROM Customers;")
    
    # Fetch all rows
    rows = cur.fetchall()
    
    # Add rows to the Rich table
    for row in rows:
        customer_id, name, city, state = row
        table.add_row(str(customer_id), name, city, state)
        
    # Close the cursor
    cur.close()
    
    # Print the table to the console
    console.print(table)


def print_segments(connection, console=None):
    
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
    
    # Create a cursor
    cur = connection.cursor()
    
    # Execute the SQL query to fetch data
    query = """
    SELECT s.SegmentID, s.ContractID, c.RenewalFromContractID, cu.Name, c.ContractDate, s.SegmentStartDate, s.SegmentEndDate, s.Title, s.Type, s.SegmentValue
    FROM Segments s
    JOIN Contracts c ON s.ContractID = c.ContractID
    JOIN Customers cu ON c.CustomerID = cu.CustomerID;
    """
    cur.execute(query)
    
    # Fetch all rows
    rows = cur.fetchall()
    
    # Add rows to the Rich table
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
        
    # Close the cursor
    cur.close()
    
    # Print the table to the console
    console.print(table)
    

def print_contracts(connection, console=None):
    
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
    
    # Create a cursor
    cur = connection.cursor()
    
    # Execute the SQL query to fetch data
    cur.execute(f"SELECT * FROM Contracts;")
    
    # Fetch all rows
    rows = cur.fetchall()
    
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
        
    # Close the cursor
    cur.close()
    
    # Print the table to the console
    console.print(table)


    
    
def print_customer_contracts(connection, customer_id, console=None):

    # If no console object is provided, create a new one
    if console is None:
        console = Console()
    
    # Initialize the Table
    table = Table(title=f"Contracts for Customer ID {customer_id}")
    
    # Add columns
    table.add_column("Contract ID", justify="right")
    table.add_column("Customer ID", justify="right")
    table.add_column("Renewal ID", justify="right")
    table.add_column("Reference", justify="left")
    table.add_column("Contract Date", justify="right")
    table.add_column("Term Start Date", justify="right")
    table.add_column("Term End Date", justify="right")
    table.add_column("Total Value", justify="right")
    
    # Create a cursor
    cur = connection.cursor()
    
    # Execute the SQL query to fetch data
    cur.execute(f"SELECT * FROM Contracts WHERE CustomerID = {customer_id};")
    
    # Fetch all rows
    rows = cur.fetchall()
    
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
        
    # Close the cursor
    cur.close()
    
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
    formatted_dates = [date.strftime("%b-%Y") for date in df.index]
    for formatted_date in formatted_dates:
        table.add_column(formatted_date, justify="right")
    
    # Add rows to the table
    for customer, row in transposed_df.iterrows():
        values = row.values
        formatted_values = [str(int(value)) for value in values]
        table.add_row(customer, *formatted_values)
    
    console.print(table)
    return True

