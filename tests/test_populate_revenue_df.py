import pytest
from src.calc import populate_revenue_df
from datetime import datetime
import pandas as pd

def test_populate_revenue_df_case1a(db_engine_case1):
    # Test is for contract that starts 2022-06-01 and ends 2023-05-31
    # This test is for end-month revenue
    
    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    type = 'end'
    customer = None
    contract = None
    result_df = populate_revenue_df(start_date, end_date, type, db_engine_case1, customer, contract)

    # Generate expected data
    first = [0]*5
    second = [10000.0]*12
    third = [0]*7
    expected_data_dict = {
        'Test Customer': first + second + third
    }
    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    assert result_df.equals(expected_df)

def test_populate_revenue_df_case1b(db_engine_case1):
    # Test is for contract that starts 2022-06-01 and ends 2023-05-31
    # This test is for mid-month revenue
    
    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    type = 'mid'
    customer = None
    contract = None
    result_df = populate_revenue_df(start_date, end_date, type, db_engine_case1, customer, contract)

    # Generate expected data
    first = [0]*5
    second = [10000]*12
    third = [0]*7
    expected_revenue_data = [float("{:.1f}".format(x)) for x in first + second + third]
    expected_data_dict = {
        'Test Customer': expected_revenue_data
    }
    date_range = pd.date_range(start_date, end_date, freq='M')
    date_range = date_range.map(lambda x: x.replace(day=15))
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    print(result_df)
    print(expected_df)
    
    assert result_df.equals(expected_df)
