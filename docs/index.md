# Documentation
## Topic 1
Lots of text
## Topic 2
Lots of text
## Trying syntax highlighting

```python
def populate_bkings_carr_arr_df(start_date, end_date, engine, customer=None, contract=None):
    """Generate a DataFrame with Bookings, ARR and CARR for each month. NOTE: the day of the month on each of start_date and end_date is ignored in the creation of date_list that has end of month days only."""

    console = Console()
    
    # Generate list of dates
    date_list = []
    current_date = start_date

    print_status(console, f"... generating bkings dataframe from {start_date} to {end_date}", MessageStyle.INFO)
    while current_date <= end_date:
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        eom_date = current_date.replace(day=last_day)  # End-of-month date
        date_list.append(eom_date)
        
        # Add one month to get the next start_date
        current_date = eom_date + rd.relativedelta(days=1)
```
