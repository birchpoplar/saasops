from src import classes, display, database, calc, visualization, export
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

engine = database.connect_database(console)
print(type(engine))

start_date = date(2022, 2, 28)
end_date = date(2023, 2, 28)

# df = calc.populate_revenue_df(start_date, end_date, engine)

# metrics_df = calc.populate_metrics_df(start_date, end_date, engine)

# display.print_dataframe(df, "Revenue by Customer", console)

# display.print_dataframe(metrics_df, "Revenue Metrics", console)

# display.print_customers(engine, console)

# display.print_contracts(engine, console)

# display.print_segments(engine, console)

# display.print_customer_contracts(engine, 4, console)

# bkings_carr_arr_df = calc.populate_bkings_carr_arr_df(start_date, end_date, engine)

# display.print_dataframe(bkings_carr_arr_df, "Bookings, ARR and CARR", console)

# visualization.create_mrr_change_chart(engine, start_date, end_date)
# visualization.create_monthly_mrr_chart(engine, start_date, end_date)
# visualization.ttm_ndr_gdr_chart(engine, end_date)
# visualization.create_bookings_arr_carr_chart(engine, start_date, end_date)

# display.export_data_to_xlsx(engine, start_date, end_date)

export.export_data_to_pptx(engine, start_date, end_date)
