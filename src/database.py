import os
import psycopg2
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from src.classes import MessageStyle
from src import utils
from rich.console import Console
import textwrap
import pandas as pd

# Database functions

def connect_database(console: Console):

    # Get database credentials from environment variables
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")

    # Create the connection string
    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}")
    
    utils.print_status(console, "Database opened successfully", MessageStyle.SUCCESS)

    return engine


def fetch_data_from_db(engine, table_name):
    # Create a new DataFrame from a database table
    with engine.begin() as conn:
        query = text(f"SELECT * FROM {table_name}")
        df = pd.read_sql(query, conn)
    return df


# Customer functions

def add_customer(engine, name, city, state):
    with engine.begin() as conn:
        query = text("""INSERT INTO Customers (Name, City, State) VALUES (:Name, :City, :State) RETURNING CustomerID;""")
        params = {
            "Name": name,
            "City": city,
            "State": state
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows added."
        else:
            return f"{result.rowcount} row(s) added. CustomerID {result.fetchone()[0]} was successfully added."

def delete_customer(engine, customer_id):
    with engine.begin() as conn:
        query = text("""DELETE FROM Customers WHERE CustomerID = :CustomerID;""")
        params = {
            "CustomerID": customer_id
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows deleted. The specified CustomerID may not exist."
        else:
            return f"{result.rowcount} row(s) deleted. Customer with CustomerID {customer_id} was successfully deleted."


def update_customer(engine, customer_id, field, value):
    with engine.begin() as conn:
        query = text(f"""UPDATE Customers SET {field} = :Value WHERE CustomerID = :CustomerID;""")
        params = {
            "CustomerID": customer_id,
            "Value": value
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows updated. The specified CustomerID may not exist."
        else:
            return f"{result.rowcount} row(s) updated. Customer with CustomerID {customer_id} was successfully updated."

# Contract functions
        
def add_contract(engine, customer_id, renewal_id, reference, contract_date, term_start_date, term_end_date, total_value): 
    with engine.begin() as conn:
        query = text("""INSERT INTO Contracts (CustomerID, RenewalFromID, Reference, ContractDate, TermStartDate, TermEndDate, TotalValue) VALUES (:CustomerID, :RenewalFromID, :Reference, :ContractDate, :TermStartDate, :TermEndDate, :TotalValue) RETURNING ContractID;""")
        params = {
            "CustomerID": customer_id,
            "RenewalFromID": renewal_id,
            "Reference": reference,
            "ContractDate": contract_date,
            "TermStartDate": term_start_date,
            "TermEndDate": term_end_date,
            "TotalValue": total_value
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows added."
        else:
            return f"{result.rowcount} row(s) added. ContractID {result.fetchone()[0]} was successfully added."


def delete_contract(engine, contract_id):
    with engine.begin() as conn:
        query = text("""DELETE FROM Contracts WHERE ContractID = :ContractID;""")
        params = {
            "ContractID": contract_id
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows deleted. The specified ContractID may not exist."
        else:
            return f"{result.rowcount} row(s) deleted. Contract with ContractID {contract_id} was successfully deleted."


def update_contract(engine, contract_id, field, value):
    with engine.begin() as conn:
        query = text(f"""UPDATE Contracts SET {field} = :Value WHERE ContractID = :ContractID;""")
        params = {
            "ContractID": contract_id,
            "Value": value
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows updated. The specified ContractID may not exist."
        else:
            return f"{result.rowcount} row(s) updated. Contract with ContractID {contract_id} was successfully updated."

# Segment functions



def add_segment(engine, contract_id, segment_start_date, segment_end_date, title, type, segment_value):
    with engine.begin() as conn:
        query = text("""INSERT INTO Segments (ContractID, SegmentStartDate, SegmentEndDate, Title, Type, SegmentValue) VALUES (:ContractID, :SegmentStartDate, :SegmentEndDate, :Title, :Type, :SegmentValue) RETURNING SegmentID;""")
        params = {
            "ContractID": contract_id,
            "SegmentStartDate": segment_start_date,
            "SegmentEndDate": segment_end_date,
            "Title": title,
            "Type": type,
            "SegmentValue": segment_value
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows added."
        else:
            return f"{result.rowcount} row(s) added. SegmentID {result.fetchone()[0]} was successfully added."

def delete_segment(engine, segment_id):
    with engine.begin() as conn:
        query = text("""DELETE FROM Segments WHERE SegmentID = :SegmentID;""")
        params = {
            "SegmentID": segment_id
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows deleted. The specified SegmentID may not exist."
        else:
            return f"{result.rowcount} row(s) deleted. Segment with SegmentID {segment_id} was successfully deleted."

def update_segment(engine, segment_id, field, value):
    with engine.begin() as conn:
        query = text(f"""UPDATE Segments SET {field} = :Value WHERE SegmentID = :SegmentID;""")
        params = {
            "SegmentID": segment_id,
            "Value": value
        }
        result = conn.execute(query, params)
        if result.rowcount == 0:
            return "No rows updated. The specified SegmentID may not exist."
        else:
            return f"{result.rowcount} row(s) updated. Segment with SegmentID {segment_id} was successfully updated."
