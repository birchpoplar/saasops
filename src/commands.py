from src import database, display, export, calc
from typer import Typer
from rich.console import Console
from datetime import date, datetime, timedelta
from typing import Optional
import calendar

app = Typer(name="saasops")

customer_app = Typer(name="customer", help="Manage customers")
contract_app = Typer(name="contract", help="Manage contracts")
segment_app = Typer(name="segment", help="Manage segments")
invoice_app = Typer(name="invoice", help="Manage invoices")
invoicesegment_app = Typer(name="invoicesegment", help="Map invoices to segments")
calc_app = Typer(name="calc", help="Calculate output data and metrics")
export_app = Typer(name="export", help="Export data to various file type")

app.add_typer(customer_app, name="customer")
app.add_typer(contract_app, name="contract")
app.add_typer(segment_app, name="segment")
app.add_typer(invoice_app, name="invoice")
app.add_typer(invoicesegment_app, name="invoicesegment")
app.add_typer(calc_app, name="calc")
app.add_typer(export_app, name="export")

# Database selection commands

@app.command()
def set_db(db_name: str):
    """
    Set the database to use.
    """
    os.environ["DB_NAME"] = db_name

# Customer commands
    
@customer_app.command("list")
def listcust():
    """
    List all customers.
    """
    console = Console()
    engine = database.connect_database(console)
    display.print_customers(engine, console)

@customer_app.command("add")
def custadd(name: str, city: str, state: str):
    """
    Add a new customer.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.add_customer(engine, name, city, state))

@customer_app.command("del")
def custdel(customer_id: int):
    """
    Delete a customer.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_customer(engine, customer_id))

@customer_app.command("update")
def custupd(customer_id: int, field: str, value: str):
    """
    Update a customer record with new value.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.update_customer(engine, customer_id, field, value))

# Contract commands

@contract_app.command("list")
def listcont():
    """
    List all contracts.
    """
    console = Console()
    engine = database.connect_database(console)
    display.print_contracts(engine, console)

@contract_app.command("add")
def contadd(customer_id: int, reference: str, contract_date: str, term_start_date: str, term_end_date: str, total_value: int, renewal_id: Optional[int]=None):
    """
    Add a new contract.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.add_contract(engine, customer_id, reference, contract_date, term_start_date, term_end_date, total_value, renewal_id))

@contract_app.command("del")
def contdel(contract_id: int):
    """
    Delete a contract.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_contract(engine, contract_id))

@contract_app.command("update")
def contupd(contract_id: int, field: str, value: str):
    """
    Update a contract record with new value.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.update_contract(engine, contract_id, field, value))

@contract_app.command("print")
def prntcont(contract_id: int):
    """
    Print details of a contract.
    """
    console = Console()
    engine = database.connect_database(console)
    display.print_contract(engine, contract_id, console)

# Segment commands

@segment_app.command("list")
def listseg():
    """
    List all segments.
    """
    console = Console()
    engine = database.connect_database(console)
    display.print_segments(engine, console)

@segment_app.command("print")
def prntseg(segment_id: int):
    """
    Print details of a segment.
    """
    console = Console()
    engine = database.connect_database(console)
    display.print_segment(engine, segment_id, console)

@segment_app.command("add")
def segadd(contract_id: int, segment_start_date: str, segment_end_date: str, title: str, type: str, segment_value: int):
    """
    Add a new segment.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.add_segment(engine, contract_id, segment_start_date, segment_end_date, title, type, segment_value))

@segment_app.command("del")
def segdel(segment_id: int):
    """
    Delete a segment.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_segment(engine, segment_id))

@segment_app.command("update")
def segupd(segment_id: int, field: str, value: str):
    """
    Update a segment record with new value.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.update_segment(engine, segment_id, field, value))

# Invoice commands

@invoice_app.command("list")
def listinv():
    """
    List all invoices.
    """
    console = Console()
    engine = database.connect_database(console)
    display.print_invoices(engine, console)

@invoice_app.command("add")
def invadd(number: str, date: str, dayspayable: int, amount: int):
    """
    Add a new invoice.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.add_invoice(engine, number, date, dayspayable, amount))

@invoice_app.command("del")
def invdel(invoice_id: int):
    """
    Delete an invoice.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_invoice(engine, invoice_id))

# Invoice Segment commands

@invoicesegment_app.command("add")
def addinvseg(invoice_id: int, segment_id: int):
    """
    Add a new invoice segment mapping.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.add_invoice_to_segment_mapping(engine, invoice_id, segment_id))

@invoicesegment_app.command("del")
def delinvseg(invoice_segment_id: int):
    """
    Delete an invoice segment mapping.
    """
    console = Console()
    engine = database.connect_database(console)
    print(database.delete_invoice_to_segment_mapping(engine, invoice_segment_id))
    
# Calculation commands

@calc_app.command("bkings")
def bkingsdf(start_date: str, end_date: str, customer: Optional[int]=None, contract: Optional[int]=None):
    """
    Print bookings, CARR and ARR dataframe.
    """
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df = calc.populate_bkings_carr_arr_df(start_date, end_date, engine, customer, contract)
    df_title = f'Bookings, ARR and CARR, {start_date} to {end_date}'
    if customer:
        df_title += f', customer: {customer}'
    if contract:
        df_title += f', contract: {contract}'
    display.print_dataframe(df, df_title, console)

@calc_app.command("rev")
def revdf(
        start_date: str,
        end_date: str,
        type: str,
        customer: Optional[int]=None,
        contract: Optional[int]=None
):
    """
    Print revenue dataframe.
    """
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df = calc.populate_revenue_df(start_date, end_date, type, engine, customer, contract)
    _, last_day_start = calendar.monthrange(start_date.year, start_date.month)
    _, last_day_end = calendar.monthrange(end_date.year, end_date.month)
    if type == 'mid':
        start_date = start_date.replace(day=15)
        end_date = end_date.replace(day=15)
    elif type == 'end':
        start_date = start_date.replace(day=last_day_start)
        end_date = end_date.replace(day=last_day_end)
    df_title = f'Revenue, {start_date} to {end_date}, type: {type}-month'
    if customer:
        df_title += f', customer: {customer}'
    if contract:
        df_title += f', contract: {contract}'
    display.print_dataframe(df, df_title, console)

@calc_app.command("metrics")
def metricsdf(
        start_date: str,
        end_date: str,
        customer: Optional[int]=None,
        contract: Optional[int]=None
):
    """
    Print metrics dataframe.
    """
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    df = calc.populate_metrics_df(start_date, end_date, engine, customer, contract)
    df_title = f'Metrics, {start_date} to {end_date}'
    if customer:
        df_title += f', customer: {customer}'
    if contract:
        df_title += f', contract: {contract}'
    display.print_dataframe(df, df_title, console)

@calc_app.command("arr")
def arrdf(date: str):
    """
    Print ARR table for specific date.
    """
    console = Console()
    engine = database.connect_database(console)
    date = datetime.strptime(date, '%Y-%m-%d').date()
    df = calc.customer_arr_df(date, engine)
    display.print_table(df, f'ARR at {date}', console)

@calc_app.command("carr")
def carrdf(date: str):
    """
    Print CARR table for specific date.
    """
    console = Console()
    engine = database.connect_database(console)
    date = datetime.strptime(date, '%Y-%m-%d').date()
    df = calc.customer_carr_df(date, engine)
    display.print_table(df, f'CARR at {date}', console)
 
# Export commands 

@export_app.command("all")
def exportall(start_date: str, end_date: str):
    """
    Export all chart data to PowerPoint presentation and Excel workbook.
    """
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    export.export_data_to_pptx(engine, start_date, end_date)
    export.export_data_to_xlsx(engine, start_date, end_date)

@export_app.command("charts")
def exportcharts(start_date: str, end_date: str, customer: Optional[int]=None, contract: Optional[int]=None):
    """
    Export all charts to image files.
    """
    console = Console()
    engine = database.connect_database(console)
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    export.export_chart_images(engine, start_date, end_date, customer, contract)
