from src import database, display, export, calc
from typer import Typer
from rich.console import Console
from datetime import date, datetime

cli_app = Typer()

# Customer commands
    
@cli_app.command()
def listcust():
    """
    List all customers.
    """
    console = Console()
    engine = database.connect_database(console)
    display.print_customers(engine, console)

@cli_app.command()
def custadd(name: str, city: str, state: str):
    """
    Add a new customer.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.add_customer(engine, name, city, state))

@cli_app.command()
def custdel(customer_id: int):
    """
    Delete a customer.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_customer(engine, customer_id))

@cli_app.command()
def custupd(customer_id: int, field: str, value: str):
    """
    Update a customer record with new value.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.update_customer(engine, customer_id, field, value))

# Contract commands

@cli_app.command()
def listcont():
    console = Console()
    engine = database.connect_database(console)
    display.print_contracts(engine, console)

@cli_app.command()
def contadd(customer_id: int, renewal_id: int, reference: str, contract_date: str, term_start_date: str, term_end_date: str, total_value: int):
    console = Console()
    engine = database.connect_database(console)
    print(database.add_contract(engine, customer_id, renewal_id, reference, contract_date, term_start_date, term_end_date, total_value))

@cli_app.command()
def contdel(contract_id: int):
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_contract(engine, contract_id))

@cli_app.command()
def contupd(contract_id: int, field: str, value: str):
    console = Console()
    engine = database.connect_database(console)
    print(database.update_contract(engine, contract_id, field, value))

@cli_app.command()
def prntcont(contract_id: int):
    console = Console()
    engine = database.connect_database(console)
    display.print_contract(engine, contract_id, console)

@cli_app.command()
def prntcustcont(customer_id: int):
    console = Console()
    engine = database.connect_database(console)
    display.print_customer_contracts(engine, customer_id, console)
    
# Segment commands

@cli_app.command()
def listseg():
    console = Console()
    engine = database.connect_database(console)
    display.print_segments(engine, console)

@cli_app.command()
def prntseg(segment_id: int):
    console = Console()
    engine = database.connect_database(console)
    display.print_segment(engine, segment_id, console)

@cli_app.command()
def segadd(contract_id: int, segment_start_date: str, segment_end_date: str, title: str, type: str, segment_value: int):
    console = Console()
    engine = database.connect_database(console)
    print(database.add_segment(engine, contract_id, segment_start_date, segment_end_date, title, type, segment_value))

@cli_app.command()
def segdel(segment_id: int):
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_segment(engine, segment_id))

@cli_app.command()
def segupd(segment_id: int, field: str, value: str):
    console = Console()
    engine = database.connect_database(console)
    print(database.update_segment(engine, segment_id, field, value))
    
# Calculation commands

@cli_app.command()
def bkingsdf(start_date: str, end_date: str):
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df = calc.populate_bkings_carr_arr_df(start_date, end_date, engine)
    display.print_dataframe(df, 'Bookings, ARR and CARR', console)

@cli_app.command()
def revdf(start_date: str, end_date: str, type: str):
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df = calc.populate_revenue_df(start_date, end_date, type, engine)
    display.print_dataframe(df, f'Revenue, type: {type}-month', console)

@cli_app.command()
def metricsdf(start_date: str, end_date: str):
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df = calc.populate_metrics_df(start_date, end_date, engine)
    display.print_dataframe(df, 'Metrics', console)

@cli_app.command()
def arrdf(date: str):
    console = Console()
    engine = database.connect_database(console)
    date = datetime.strptime(date, '%Y-%m-%d').date()
    df = calc.customer_arr_df(date, engine)
    display.print_table(df, f'ARR at {date}', console)

@cli_app.command()
def carrdf(date: str):
    console = Console()
    engine = database.connect_database(console)
    date = datetime.strptime(date, '%Y-%m-%d').date()
    df = calc.customer_carr_df(date, engine)
    display.print_table(df, f'CARR at {date}', console)
    
# Export commands 

@cli_app.command()
def exportall(start_date: str, end_date: str):
    """
    Export all chart data to PowerPoint presentation.
    """
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    export.export_data_to_pptx(engine, start_date, end_date)
