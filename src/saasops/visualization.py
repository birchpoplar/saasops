import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
import psycopg2
import dateutil.relativedelta as rd
import textwrap
from dotenv import load_dotenv
import os

import saasops.classes as classes
import saasops.display as display
import saasops.database as database
import saasops.calc as calc
import saasops.visualization as visualization

from matplotlib.ticker import FuncFormatter, FixedLocator
import numpy as np
import math
from saasops.constants import COLOR_MAP
from rich.console import Console

def thousands_formatter(x, pos):
    return f"${x/1000:,.0f}K"


def round_up_to_base(x, base=5000):
    return base * math.ceil(x / base)


def ttm_ndr_gdr_chart(engine, target_date, customer=None, contract=None):

    # Call the new function to calculate metrics
    calculated_metrics = calc.populate_ttm_metrics_df(target_date, engine)

    # Extract metric names and values for the chart
    metrics = [metric[0] for metric in calculated_metrics]
    values = [metric[1] for metric in calculated_metrics]

    # Print metrics
    print(f"Trailing 12-Month Values for {target_date}:")
    for metric, value in calculated_metrics:
        print(f"{metric}: {value:.2f}")
   
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(metrics, values, color=[
        COLOR_MAP["navy_blue"],
        COLOR_MAP["slate_blue"],
        COLOR_MAP["sky_blue"],
        COLOR_MAP["teal"],
        COLOR_MAP["green_1"],
        COLOR_MAP["teal"]
        ])

    # Since the 'values' list is ordered as ['Beginning ARR', 'Churn', ...]
    # Use these values directly from the 'values' list
    beginning_arr = values[0]
    churn = values[1]
    contraction = values[2]
    gross_dollar_retention = values[3]
    expansion = values[4]
    net_dollar_retention = values[5]
    
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
    ax.xaxis.set_major_locator(FixedLocator(locs=range(len(wrapped_labels))))
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
    plt.savefig("exports/trailing_12_month_values.png", dpi=300)


def create_mrr_change_chart(engine, start_date, end_date, customer=None, contract=None, frequency='M'):

    console = Console()
    print_status(console, f"Creating MRR change chart between {start_date} and {end_date}", MessageStyle.INFO)
    metrics_df = calc.populate_metrics_df(start_date, end_date, engine, customer, contract, frequency=frequency)

    # Convert the index to DateTimeIndex if it's not already
    #if not isinstance(metrics_df.index, pd.DatetimeIndex):
    #    metrics_df.index = pd.to_datetime(metrics_df.index)

    # Formatting the index to Year-Month
    if frequency == 'Q':
        periods = metrics_df.index
    else:
        periods = metrics_df.index.strftime('%Y-%m')

    # Values for the bars
    new_mrr = metrics_df['New MRR']
    churn_mrr = -metrics_df['Churn MRR']
    expansion_mrr = metrics_df['Expansion MRR']
    contraction_mrr = -metrics_df['Contraction MRR']

    aggregate_mrr = metrics_df['New MRR'] + metrics_df['Expansion MRR'] - metrics_df['Churn MRR'] - metrics_df['Contraction MRR']
    
    # Color for the bars
    colors = [
        COLOR_MAP["green_2"],
        COLOR_MAP["green_1"],
        COLOR_MAP["slate_blue"],
        COLOR_MAP["sky_blue"]
    ]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the bars
    ax.bar(periods, new_mrr, color=colors[0], label='New MRR')
    ax.bar(periods, expansion_mrr, bottom=new_mrr, color=colors[1], label='Expansion MRR')
    ax.bar(periods, churn_mrr, color=colors[2], label='Churn MRR')
    ax.bar(periods, contraction_mrr, bottom=churn_mrr, color=colors[3], label='Contraction MRR')

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
    ax.plot(periods, aggregate_mrr, color=COLOR_MAP["navy_blue"], linestyle='--', marker='o', label='Aggregate MRR Change')
            
    # Labeling and formatting
    ax.set_ylabel('MRR', fontsize=14)
    ax.set_xlabel('Month' if frequency == 'M' else 'Quarter', fontsize=14)
    ax.set_title('Change in MRR by Month', fontsize=16)
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
    ax.set_ylim(-40000, 40000)  # Setting y-axis min and max values

    # Add a horizontal line at y=0
    ax.axhline(0, color='black', linewidth=0.8)
    
    plt.xticks(rotation=45 if frequency == 'M' else 0)
    plt.tight_layout()
    plt.savefig("exports/mrr_change.png", dpi=300)


def create_monthly_mrr_chart(engine, start_date, end_date, customer=None, contract=None, show_gridlines=False, frequency='M'):

    console = Console()
    print_status(console, f"Creating monthly MRR chart between {start_date} and {end_date}", MessageStyle.INFO)
    metrics_df = calc.populate_metrics_df(start_date, end_date, engine, customer, contract, frequency=frequency)

    # Convert the index to DateTimeIndex if it's not already
    #if not isinstance(metrics_df.index, pd.DatetimeIndex):
    #    metrics_df.index = pd.to_datetime(metrics_df.index)

    # Formatting the index to Year-Month
    if frequency == 'Q':
        periods = metrics_df.index
    else:
        periods = metrics_df.index.strftime('%Y-%m')

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
    rounded_max_abs_value = round_up_to_base(max_abs_value, base=20000)

    # Color for the bars
    colors = [
        COLOR_MAP["electric_green"],
        COLOR_MAP["green_2"],
        COLOR_MAP["green_1"],
        COLOR_MAP["slate_blue"],
        COLOR_MAP["sky_blue"]
    ]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the bars
    ax.bar(periods, starting_mrr, color=colors[0], label='Starting MRR')
    ax.bar(periods, new_mrr, bottom=starting_mrr, color=colors[1], label='New MRR')
    ax.bar(periods, expansion_mrr, bottom=starting_mrr + new_mrr, color=colors[2], label='Expansion MRR')
    ax.bar(periods, churn_mrr, color=colors[3], label='Churn MRR')
    ax.bar(periods, contraction_mrr, bottom=churn_mrr, color=colors[4], label='Contraction MRR')

    # Labeling and formatting
    ax.set_ylabel('MRR', fontsize=14)
    ax.set_xlabel('Month' if frequency == 'M' else 'Quarter', fontsize=14)
    ax.set_title('Monthly MRR', fontsize=16)
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    # Set y-axis min and max values based on the rounded maximum absolute value
    ax.set_ylim(-20000, 60000)
    # ax.set_ylim(-rounded_max_abs_value, rounded_max_abs_value)
    
    # Add gridlines if the show_gridlines argument is set to True
    if show_gridlines:
        ax.grid(which='major', axis='y', linestyle='--', linewidth=0.5)
        ax.grid(which='major', axis='x', linestyle='--', linewidth=0.5)
    
    # Add a horizontal line at y=0
    ax.axhline(0, color='black', linewidth=0.8)

    plt.xticks(rotation=45 if frequency == 'M' else 0)
    plt.tight_layout()
    plt.savefig("exports/monthly_mrr.png", dpi=300)


def create_arr_change_chart(engine, start_date, end_date, customer=None, contract=None, frequency='M'):
    # NOT REALLY STARTED YET
    
    console = Console()
    print_status(console, f"Creating ARR change chart between {start_date} and {end_date}", MessageStyle.INFO)
    metrics_df = calc.populate_metrics_df(start_date, end_date, engine, customer, contract, frequency=frequency)

    # Convert the index to DateTimeIndex if it's not already
    #if not isinstance(metrics_df.index, pd.DatetimeIndex):
    #    metrics_df.index = pd.to_datetime(metrics_df.index)

    # Formatting the index to Year-Month
    if frequency == 'Q':
        periods = metrics_df.index
    else:
        periods = metrics_df.index.strftime('%Y-%m')

    # Values for the bars
    new_mrr = metrics_df['New MRR']
    churn_mrr = -metrics_df['Churn MRR']
    expansion_mrr = metrics_df['Expansion MRR']
    contraction_mrr = -metrics_df['Contraction MRR']

    aggregate_mrr = metrics_df['New MRR'] + metrics_df['Expansion MRR'] - metrics_df['Churn MRR'] - metrics_df['Contraction MRR']
    
    # Color for the bars
    colors = [
        COLOR_MAP["green_2"],
        COLOR_MAP["green_1"],
        COLOR_MAP["slate_blue"],
        COLOR_MAP["sky_blue"]
    ]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the bars
    ax.bar(periods, new_mrr, color=colors[0], label='New MRR')
    ax.bar(periods, expansion_mrr, bottom=new_mrr, color=colors[1], label='Expansion MRR')
    ax.bar(periods, churn_mrr, color=colors[2], label='Churn MRR')
    ax.bar(periods, contraction_mrr, bottom=churn_mrr, color=colors[3], label='Contraction MRR')

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
    ax.plot(periods, aggregate_mrr, color=COLOR_MAP["navy_blue"], linestyle='--', marker='o', label='Aggregate MRR Change')
            
    # Labeling and formatting
    ax.set_ylabel('MRR', fontsize=14)
    ax.set_xlabel('Month' if frequency == 'M' else 'Quarter', fontsize=14)
    ax.set_title('Change in MRR by Month', fontsize=16)
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
    ax.set_ylim(-40000, 40000)  # Setting y-axis min and max values

    # Add a horizontal line at y=0
    ax.axhline(0, color='black', linewidth=0.8)
    
    plt.xticks(rotation=45 if frequency == 'M' else 0)
    plt.tight_layout()
    plt.savefig("exports/mrr_change.png", dpi=300)
    

def create_monthly_arr_chart(engine, start_date, end_date, customer=None, contract=None, show_gridlines=False, frequency='M', ignoreoverrides=False):

    # This function needs updated to sort the y axis limits to allow churn and contraction to be negative (need to check dataframe on that one)
    # Would need more complex limits calculation
    # For now have just excluded setting limits to see if good enough
    
    console = Console()
    print_status(console, f"Creating periodic MRR chart between {start_date} and {end_date}", MessageStyle.INFO)
    metrics_df = calc.populate_arr_metrics_df(start_date, end_date, engine, customer, contract, frequency=frequency)

    # Convert the index to DateTimeIndex if it's not already
    #if not isinstance(metrics_df.index, pd.DatetimeIndex):
    #    metrics_df.index = pd.to_datetime(metrics_df.index)

    # Formatting the index to Year-Month
    if frequency == 'Q':
        periods = metrics_df.index
    else:
        periods = metrics_df.index.strftime('%Y-%m')

    # Values for the bars
    starting_arr = metrics_df['Starting ARR']
    new_arr = metrics_df['New ARR']
    churn_arr = -metrics_df['Churn ARR']
    expansion_arr = metrics_df['Expansion ARR']
    contraction_arr = -metrics_df['Contraction ARR']

    # Calculate the cumulative ARR value for each quarter, which is total of starting, expansion and so on, and find the max for the chart
    max_abs_value = 0
    for i, (starting, new, churn, expansion, contraction) in enumerate(zip(starting_arr, new_arr, churn_arr, expansion_arr, contraction_arr)):
        if i == 0:
            continue
        cumulative = starting + new + churn + expansion + contraction
        if abs(cumulative) > max_abs_value:
            max_abs_value = abs(cumulative)
    
    # Round up the maximum absolute value to the nearest base
    rounded_max_abs_value = max_abs_value + 50000

    # Color for the bars
    colors = [
        COLOR_MAP["electric_green"],
        COLOR_MAP["green_2"],
        COLOR_MAP["green_1"],
        COLOR_MAP["slate_blue"],
        COLOR_MAP["sky_blue"]
    ]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the bars
    ax.bar(periods, starting_arr, color=colors[0], label='Starting ARR')
    ax.bar(periods, new_arr, bottom=starting_arr, color=colors[1], label='New ARR')
    ax.bar(periods, expansion_arr, bottom=starting_arr + new_arr, color=colors[2], label='Expansion ARR')
    ax.bar(periods, churn_arr, color=colors[3], label='Churn ARR')
    ax.bar(periods, contraction_arr, bottom=churn_arr, color=colors[4], label='Contraction ARR')

    # Labeling and formatting
    ax.set_ylabel('ARR', fontsize=14)
    ax.set_xlabel('Month' if frequency == 'M' else 'Quarter', fontsize=14)
    ax.set_title('Monthly ARR' if frequency == 'M' else 'Quarterly ARR', fontsize=16)
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    # Set y-axis min and max values based on the rounded maximum absolute value
    # ax.set_ylim(-20000, 60000)
    # ax.set_ylim(0, rounded_max_abs_value)
    
    # Add gridlines if the show_gridlines argument is set to True
    if show_gridlines:
        ax.grid(which='major', axis='y', linestyle='--', linewidth=0.5)
        ax.grid(which='major', axis='x', linestyle='--', linewidth=0.5)
    
    # Add a horizontal line at y=0
    ax.axhline(0, color='black', linewidth=0.8)

    plt.xticks(rotation=45 if frequency == 'M' else 0)
    plt.tight_layout()
    plt.savefig("exports/periodic_arr.png", dpi=300)

    
def create_bookings_arr_carr_chart(engine, start_date, end_date, customer=None, contract=None, show_gridlines=False, frequency='M', ignoreoverrides=False):

    console = Console()
    print_status(console, f"Creating bookings, ARR, and CARR chart between {start_date} and {end_date}", MessageStyle.INFO)
    df = calc.populate_bkings_carr_arr_df(start_date, end_date, engine, customer, contract, frequency, ignoreoverrides)
    
    # Convert the index to DateTimeIndex if it's not already
    # if not isinstance(df.index, pd.DatetimeIndex):
    #     df.index = pd.to_datetime(df.index)
    
    # Formatting the index to Year-Month
    if frequency == 'Q':
        periods = df.index
    else:
        periods = df.index.strftime('%Y-%m')

    # Values for the bars and lines
    bookings = df['Bookings']
    arr = df['ARR']
    carr = df['CARR']
    
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create the bar chart for 'Bookings'
    bars = ax.bar(periods, bookings, color=COLOR_MAP["slate_blue"], label='Bookings')

    # Create line plots for 'ARR' and 'CARR'
    ax.plot(periods, carr, 'o-', label='CARR', color=COLOR_MAP["electric_green"])
    ax.plot(periods, arr, 'o-', label='ARR', color=COLOR_MAP["navy_blue"])

    # Labeling and formatting
    ax.set_xlabel('Month' if frequency == 'M' else 'Quarter', fontsize=14, color='black')
    ax.set_ylabel('Values', fontsize=14, color='black')
    ax.set_title('Bookings, ARR, and CARR', fontsize=16)
    ax.tick_params(axis='both', labelcolor='black')
    
    # Set thousands formatter for y-axis
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    # Add gridlines if the show_gridlines argument is set to True
    if show_gridlines:
        ax.grid(which='major', axis='y', linestyle='--', linewidth=0.5)
        ax.grid(which='major', axis='x', linestyle='--', linewidth=0.5)
    
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

    plt.xticks(rotation=45 if frequency == 'M' else 0)
    plt.tight_layout()
    plt.savefig("exports/bookings_arr_carr.png", dpi=300)
