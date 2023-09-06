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
import numpy as np
import math


def thousands_formatter(x, pos):
    return f"${x/1000:,.0f}K"


def round_up_to_base(x, base=5000):
    return base * math.ceil(x / base)


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
    plt.savefig("trailing_12_month_values.png", dpi=300)


def create_mrr_change_chart(conn, start_date, end_date):
    metrics_df = calc.populate_metrics_df(start_date, end_date, conn)

    # Convert the index to DateTimeIndex if it's not already
    if not isinstance(metrics_df.index, pd.DatetimeIndex):
        metrics_df.index = pd.to_datetime(metrics_df.index)

    # Formatting the index to Year-Month
    months = metrics_df.index.strftime('%Y-%m')

    # Values for the bars
    new_mrr = metrics_df['New MRR']
    churn_mrr = -metrics_df['Churn MRR']
    expansion_mrr = metrics_df['Expansion MRR']
    contraction_mrr = -metrics_df['Contraction MRR']

    aggregate_mrr = metrics_df['New MRR'] + metrics_df['Expansion MRR'] - metrics_df['Churn MRR'] - metrics_df['Contraction MRR']
    
    # Color for the bars
    colors = ['royalblue', 'lightsteelblue', 'sandybrown', 'peachpuff']

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the bars
    ax.bar(months, new_mrr, color=colors[0], label='New MRR')
    ax.bar(months, expansion_mrr, bottom=new_mrr, color=colors[1], label='Expansion MRR')
    ax.bar(months, churn_mrr, color=colors[2], label='Churn MRR')
    ax.bar(months, contraction_mrr, bottom=churn_mrr, color=colors[3], label='Contraction MRR')

    # Add data value annotations
    for i, (new, churn, expansion, contraction) in enumerate(zip(new_mrr, churn_mrr, expansion_mrr, contraction_mrr)):
        if new != 0:
            ax.text(i, new/2, f"${new/1000:,.0f}K", ha='center', va='center')
        if expansion != 0:
            ax.text(i, new + expansion/2, f"${expansion/1000:,.0f}K", ha='center', va='center')
        if churn != 0:
            ax.text(i, churn/2, f"${-churn/1000:,.0f}K", ha='center', va='center')
        if contraction != 0:
            ax.text(i, churn + contraction/2, f"${-contraction/1000:,.0f}K", ha='center', va='center')

    # Add a line plot of aggregate MRR
    ax.plot(months, aggregate_mrr, color='grey', linestyle='--', marker='o', label='Aggregate MRR Change')
            
    # Labeling and formatting
    ax.set_ylabel('MRR', fontsize=14)
    ax.set_xlabel('Month', fontsize=14)
    ax.set_title('Change in MRR by Month', fontsize=16)
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
    ax.set_ylim(-20000, 20000)  # Setting y-axis min and max values

    # Add a horizontal line at y=0
    ax.axhline(0, color='black', linewidth=0.8)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("mrr_change.png", dpi=300)


def create_monthly_mrr_chart(conn, start_date, end_date):
    metrics_df = calc.populate_metrics_df(start_date, end_date, conn)

    # Convert the index to DateTimeIndex if it's not already
    if not isinstance(metrics_df.index, pd.DatetimeIndex):
        metrics_df.index = pd.to_datetime(metrics_df.index)

    # Formatting the index to Year-Month
    months = metrics_df.index.strftime('%Y-%m')

    # Values for the bars
    starting_mrr = metrics_df['Starting MRR']
    new_mrr = metrics_df['New MRR']
    churn_mrr = -metrics_df['Churn MRR']
    expansion_mrr = metrics_df['Expansion MRR']
    contraction_mrr = -metrics_df['Contraction MRR']

    max_abs_value = np.max([
        np.abs(starting_mrr).max(),
        np.abs(new_mrr).max(),
        np.abs(expansion_mrr).max(),
        np.abs(churn_mrr).max(),
        np.abs(contraction_mrr).max()
    ])

    # Round up the maximum absolute value to the nearest base
    rounded_max_abs_value = round_up_to_base(max_abs_value, base=10000)

    # Color for the bars
    colors = ['darkkhaki', 'royalblue', 'lightsteelblue', 'sandybrown', 'peachpuff']

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the bars
    ax.bar(months, starting_mrr, color=colors[0], label='Starting MRR')
    ax.bar(months, new_mrr, bottom=starting_mrr, color=colors[1], label='New MRR')
    ax.bar(months, expansion_mrr, bottom=starting_mrr + new_mrr, color=colors[2], label='Expansion MRR')
    ax.bar(months, churn_mrr, color=colors[3], label='Churn MRR')
    ax.bar(months, contraction_mrr, bottom=churn_mrr, color=colors[4], label='Contraction MRR')

    # Labeling and formatting
    ax.set_ylabel('MRR', fontsize=14)
    ax.set_xlabel('Month', fontsize=14)
    ax.set_title('Monthly MRR', fontsize=16)
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    # Set y-axis min and max values based on the rounded maximum absolute value
    ax.set_ylim(-rounded_max_abs_value, rounded_max_abs_value)
    
    # Add a horizontal line at y=0
    ax.axhline(0, color='black', linewidth=0.8)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("monthly_mrr.png", dpi=300)


def create_bookings_arr_carr_chart(conn, start_date, end_date):

    df = calc.populate_bkings_carr_arr_df(start_date, end_date, conn)
    
    # Convert the index to DateTimeIndex if it's not already
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Formatting the index to Year-Month
    months = df.index.strftime('%Y-%m')

    # Values for the bars and lines
    bookings = df['Bookings']
    arr = df['ARR']
    carr = df['CARR']
    
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create the bar chart for 'Bookings'
    bars = ax.bar(months, bookings, color='skyblue', label='Bookings')

    # Create line plots for 'ARR' and 'CARR'
    ax.plot(months, carr, 'o-', label='CARR', color='orange')
    ax.plot(months, arr, 'o-', label='ARR', color='green')

    # Labeling and formatting
    ax.set_xlabel('Month', fontsize=14, color='black')
    ax.set_ylabel('Values', fontsize=14, color='black')
    ax.set_title('Bookings, ARR, and CARR', fontsize=16)
    ax.tick_params(axis='both', labelcolor='black')
    
    # Set thousands formatter for y-axis
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    # Annotate the top of the 'Bookings' bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{thousands_formatter(height, None)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Add legend
    ax.legend(loc='upper left')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("bookings_arr_carr.png", dpi=300)