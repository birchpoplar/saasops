import os
import psycopg2
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from src.classes import MessageStyle
from src import utils
from rich.console import Console
import textwrap
import pandas as pd

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

def add_new_customer_with_input(engine, console=None):

    if console:
        console.print("Enter the following information to add a new customer:", style="bold underline")
        console.print("Press [Enter] to skip a field.", style="italic")
        console.print("")     
        
    name = input("Enter the name of the customer: ").strip()
    city = input("Enter the city: ").strip()
    state = input("Enter the state: ").strip()

    if name and city and state:
        customer_id = add_new_customer(engine, name, city, state)
        print(f"New customer added with CustomerID: {customer_id}")

    else:
        print("Input invalid. All fields must be populated.")


def add_new_customer(engine, name, city, state):
    with engine.connect() as conn:
        query = """INSERT INTO Customers (Name, City, State) VALUES (%s, %s, %s) RETURNING CustomerID;"""
        result = conn.execute(query, name, city, state)
        customer_id = result.fetchone()[0]
    return customer_id

        
def fetch_data_from_db(engine, table_name):
    # Create a new DataFrame from a database table
    with engine.begin() as conn:
        query = text(f"SELECT * FROM {table_name}")
        df = pd.read_sql(query, conn)
    return df
