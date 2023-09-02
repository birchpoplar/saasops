from src import classes, display, database, calc, visualization
from rich.console import Console
from rich.text import Text
from dotenv import load_dotenv
import os
from datetime import date, timedelta
import pandas as pd
import logging

load_dotenv()

logging.basicConfig(level=logging.ERROR)

console = Console()

conn, cur = database.connect_database(console)

start_date = date(2022, 4, 15)
end_date = date(2023, 6, 15)

df = calc.populate_revenue_df(start_date, end_date, conn)

metrics_df = calc.populate_metrics_df(start_date, end_date, conn)

# display.print_dataframe(df, "Revenue by Customer", console)

# display.print_dataframe(metrics_df, "Revenue Metrics", console)

display.print_customers(conn, console)

display.print_customer_contracts(conn, 4, console)


# visualization.ttm_ndr_gdr_chart(conn, date(2023,3,15))

# visualization.ttm_ndr_gdr_chart(conn, date(2023,6,15))
