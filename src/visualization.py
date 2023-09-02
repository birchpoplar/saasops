import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
import psycopg2
import dateutil.relativedelta as rd
import textwrap
from dotenv import load_dotenv
import os
from src import classes, display, database, calc, visualization
from matplotlib.ticker import FuncFormatter


def thousands_formatter(x, pos):
    return f"${x/1000:,.0f}K"


def ttm_ndr_gdr_chart(conn, target_date):

    # Calculate trailing 12-month values for a given date (e.g., 2023-06-15)
    trailing_start_date = pd.to_datetime(target_date) - pd.DateOffset(months=11)
    trailing_end_date = pd.to_datetime(target_date)

    # Source the appropriate dataframes for the metrics calcs
    metrics_df = calc.populate_metrics_df(trailing_start_date, trailing_end_date, conn)

    # Convert trailing_start_date to the same format as the index
    trailing_start_date = trailing_start_date.strftime("%Y-%m-%d")
    
    trailing_df = metrics_df.loc[trailing_start_date:trailing_end_date]

    beginning_arr = trailing_df.loc[trailing_start_date, "Starting MRR"] * 12
    churn = (-trailing_df["Churn MRR"].sum()) * 12
    contraction = (-trailing_df["Contraction MRR"].sum()) * 12
    gross_dollar_retention = beginning_arr + churn + contraction
    expansion = trailing_df["Expansion MRR"].sum() * 12
    net_dollar_retention = gross_dollar_retention + expansion
    
    print(f"Trailing 12-Month Values for {target_date}:")
    print(f"Beginning ARR: {beginning_arr:.2f}")
    print(f"Churn: {-churn:.2f}")
    print(f"Contraction: {-contraction:.2f}")
    print(f"Gross Dollar Retention: {gross_dollar_retention:.2f}")
    print(f"Expansion: {expansion:.2f}")
    print(f"Net Dollar Retention: {net_dollar_retention:.2f}")
    
    # Calculate metrics for trailing 12 months
    beginning_arr = trailing_df.loc[trailing_start_date, "Starting MRR"] * 12
    churn = (-trailing_df["Churn MRR"].sum()) * 12
    contraction = (-trailing_df["Contraction MRR"].sum()) * 12
    gross_dollar_retention = beginning_arr + churn + contraction
    expansion = trailing_df["Expansion MRR"].sum() * 12
    net_dollar_retention = gross_dollar_retention + expansion
    
    # Create a bar chart
    metrics = ["Beginning ARR", "Churn", "Contraction", "Gross Dollar Retention", "Expansion", "Net Dollar Retention"]
    values = [beginning_arr, churn, contraction, gross_dollar_retention, expansion, net_dollar_retention]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(metrics, values, color=['blue', 'gray', 'gray', 'orange', 'blue', 'orange'])
    
    # Adjust the positioning of floating bars
    bars[1].set_y(beginning_arr)
    bars[2].set_y(beginning_arr + churn)
    bars[4].set_y(gross_dollar_retention)
    
    values_bar_tops = [beginning_arr, beginning_arr, beginning_arr + churn, gross_dollar_retention,
                   gross_dollar_retention + expansion, net_dollar_retention]
    
    ax.set_ylabel("Revenue")
    ax.set_title(f"Trailing 12-Month Values for {target_date}")
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
    
    # Wrap and rotate x-axis tick labels
    wrapped_labels = [textwrap.fill(label, width=12) for label in metrics]  # Adjust width as needed
    ax.set_xticklabels(wrapped_labels, rotation=0, ha="center")  # Keep rotation as 0
    
    # Add horizontal dotted annotation lines between bars
    line_positions = [beginning_arr, beginning_arr + churn, beginning_arr + churn + contraction,
                      gross_dollar_retention, gross_dollar_retention + expansion]
    
    line_labels = ["Beginning ARR", "Churn", "Contraction", "Gross DR", "Expansion", "Net DR"]

    # Add in dotted lines between bars
    i = 0
    for line_pos, label in zip(line_positions, line_labels):
        ax.hlines(line_pos, i+0.4, i+0.6, linestyles='dotted', colors='gray', label=label)
        i += 1

    # If floating bars are almost the same height, add dotted line between them
    i = 0
    for value, top in zip(values, values_bar_tops):
        if value - top < 0.1:
            ax.hlines(top, i-0.4, i+0.4, linestyles='dotted', colors='gray')
        i += 1
        
    # i = 0
    # for value, top in zip(values, values_bar_tops):
    #     print(value, top)
    #     if value - top < 0.1:
    #         ax.hlines(top, i-0.4, i+0.4, linestyles='dotted', colors='gray')
    #     i += 1

    # Calculate percentages for annotation
    gdr_percentage = (gross_dollar_retention / beginning_arr) * 100
    ndr_percentage = (net_dollar_retention / beginning_arr) * 100
    
    # Annotate bars with calculated percentages
    ax.annotate(f"{gdr_percentage:.2f}%", xy=(3, gross_dollar_retention), xytext=(0, 3), 
                textcoords="offset points", ha='center', va='bottom')
    ax.annotate(f"{ndr_percentage:.2f}%", xy=(5, net_dollar_retention), xytext=(0, 3), 
                textcoords="offset points", ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()
