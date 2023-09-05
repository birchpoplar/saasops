import os
import psycopg2
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

    # Connect to the database
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    utils.print_status(console, "Database opened successfully", MessageStyle.SUCCESS)

    # Create a cursor
    cur = conn.cursor()

    return conn, cur

def add_new_customer_with_input(conn, console=None):

    if console:
        console.print("Enter the following information to add a new customer:", style="bold underline")
        console.print("Press [Enter] to skip a field.", style="italic")
        console.print("")     
        
    name = input("Enter the name of the customer: ").strip()
    city = input("Enter the city: ").strip()
    state = input("Enter the state: ").strip()

    if name and city and state:
        customer_id = add_new_customer(conn, name, city, state)
        print(f"New customer added with CustomerID: {customer_id}")

    else:
        print("Input invalid. All fields must be populated.")


def add_new_customer(conn, name, city, state):
    cur = conn.cursor()
    query = """INSERT INTO Customers (Name, City, State) VALUES (%s, %s, %s) RETURNING CustomerID;"""
    cur.execute(query, (name, city, state))
    customer_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    return customer_id

        
def fetch_data_from_db(conn, table_name):
    # Create a new DataFrame from a database table
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    return df
