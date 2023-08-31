import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
import psycopg2
import dateutil.relativedelta as rd
import textwrap
from dotenv import load_dotenv
import os

# Generate list of dates
start_date = date(2022, 1, 15)
end_date = date(2023, 8, 15)
date_list = []
current_date = start_date

while current_date <= end_date:
    date_list.append(current_date)
    current_date += rd.relativedelta(months=1)

load_dotenv()

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

print("Database opened successfully")

# Create a cursor
cur = conn.cursor()

# Retrieve unique customer names from the Customers table
cur.execute("SELECT DISTINCT Name FROM Customers")
customer_names = [row[0] for row in cur.fetchall()]

print(customer_names)

# Create empty DataFrame
df = pd.DataFrame(index=date_list, columns=customer_names)

# Populate DataFrame with active revenue
for d in date_list:
    for customer in customer_names:
        cur.execute(
            f"SELECT SUM(s.SegmentValue) / 12 "
            f"FROM Segments s "
            f"JOIN Contracts c ON s.ContractID = c.ContractID "
            f"JOIN Customers cu ON c.CustomerID = cu.CustomerID "
            f"WHERE '{d}' BETWEEN s.SegmentStartDate AND s.SegmentEndDate "
            f"AND cu.Name = '{customer}'"
        )
        active_revenue = cur.fetchone()[0]
        if active_revenue is None:
            active_revenue = 0
        df.at[d, customer] = active_revenue

# Create a second DataFrame for metrics
metrics_df = pd.DataFrame(index=date_list, columns=["New MRR", "Churn MRR", "Expansion MRR", "Contraction MRR", "Starting MRR", "Ending MRR"])


# Calculate and populate metrics for the second DataFrame
starting_mrr = 31750  # Replace with the actual starting MRR for the first month
previous_month = None
for d in date_list:
    if previous_month:
        new_mrr_sum = 0
        churn_mrr_sum = 0
        expansion_mrr_sum = 0
        contraction_mrr_sum = 0
        starting_mrr_sum = metrics_df.loc[previous_month, "Ending MRR"]
        ending_mrr_sum = starting_mrr_sum

        for customer in customer_names:
            previous_month_revenue = df.loc[previous_month, customer]
            current_month_revenue = df.loc[d, customer]

            new_mrr_sum += current_month_revenue if previous_month_revenue == 0 and current_month_revenue > 0 else 0
            churn_mrr_sum += previous_month_revenue if previous_month_revenue > 0 and current_month_revenue == 0 else 0
            expansion_mrr_sum += current_month_revenue - previous_month_revenue if current_month_revenue > previous_month_revenue and previous_month_revenue > 0 else 0
            contraction_mrr_sum += previous_month_revenue - current_month_revenue if current_month_revenue < previous_month_revenue and current_month_revenue > 0 else 0

        ending_mrr_sum += new_mrr_sum + expansion_mrr_sum - churn_mrr_sum - contraction_mrr_sum

        metrics_df.at[d, "New MRR"] = new_mrr_sum
        metrics_df.at[d, "Churn MRR"] = churn_mrr_sum
        metrics_df.at[d, "Expansion MRR"] = expansion_mrr_sum
        metrics_df.at[d, "Contraction MRR"] = contraction_mrr_sum
        metrics_df.at[d, "Starting MRR"] = starting_mrr_sum
        metrics_df.at[d, "Ending MRR"] = ending_mrr_sum

    else:
        metrics_df.at[d, "New MRR"] = 0
        metrics_df.at[d, "Churn MRR"] = 0
        metrics_df.at[d, "Expansion MRR"] = 0
        metrics_df.at[d, "Contraction MRR"] = 0
        metrics_df.at[d, "Starting MRR"] = starting_mrr
        metrics_df.at[d, "Ending MRR"] = starting_mrr

    previous_month = d

# Close cursor and connection
cur.close()
conn.close()

print(df)
print(metrics_df)

# Calculate trailing 12-month values for a given date (e.g., 2023-06-15)
target_date = "2023-06-15"
trailing_start_date = pd.to_datetime(target_date) - pd.DateOffset(months=12)
trailing_end_date = pd.to_datetime(target_date)

# Convert trailing_start_date to the same format as the index
trailing_start_date = trailing_start_date.date()

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

# Wrap and rotate x-axis tick labels
wrapped_labels = [textwrap.fill(label, width=12) for label in metrics]  # Adjust width as needed
ax.set_xticklabels(wrapped_labels, rotation=0, ha="center")  # Keep rotation as 0

# Add horizontal dotted annotation lines between bars
line_positions = [beginning_arr, beginning_arr + churn, beginning_arr + churn + contraction,
                  gross_dollar_retention, gross_dollar_retention + expansion]

line_labels = ["Beginning ARR", "Churn", "Contraction", "Gross DR", "Expansion", "Net DR"]

i = 0
for line_pos, label in zip(line_positions, line_labels):
    ax.hlines(line_pos, i+0.4, i+0.6, linestyles='dotted', colors='gray', label=label)
    i += 1

i = 0  
for value, top in zip(values, values_bar_tops):
    if value == 0:
        ax.hlines(top, i-0.4, i+0.4, linestyles='dotted', colors='gray')
    i += 1

plt.tight_layout()
plt.savefig("trailing_12_month_values.png", bbox_inches="tight")
