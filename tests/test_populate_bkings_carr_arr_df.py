import pytest
from src.calc import populate_bkings_carr_arr_df
from datetime import datetime
import pandas as pd

def test_populate_bkings_carr_arr_df_case1(db_engine_case1):
    # Test is for contract that is booked 2022-05-01, has revenue starting 2022-06-01 and ending 2023-05-31
    # This test is for bookings, ARR and CARR
    
    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    customer = None
    contract = None
    result_df = populate_bkings_carr_arr_df(start_date, end_date, db_engine_case1, customer, contract)

    # Generate expected data
    # Bookings
    bookings_data = [0]*4 + [120000.0] + [0]*19
    arr_data = [0]*5 + [120000.0]*12 + [0]*7
    carr_data = [0]*4 + [120000.0]*13 + [0]*7
    
    expected_data_dict = {
        'Bookings': bookings_data,
        'ARR': arr_data,
        'CARR': carr_data
    }
    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    print(result_df)
    print(expected_df)
    
    assert result_df.equals(expected_df)


def test_populate_bkings_carr_arr_df_case2(db_engine_case2):
    
    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    customer = None
    contract = None
    result_df = populate_bkings_carr_arr_df(start_date, end_date, db_engine_case2, customer, contract)

    # Generate expected data
    bookings_data = [0]*4 + [120000.0] + [0]*11 + [240000.0] + [0]*7
    arr_data = [0]*5 + [120000.0]*12 + [240000.0]*7
    carr_data = [0]*4 + [120000.0]*12 + [240000.0]*8

    expected_data_dict = {
        'Bookings': bookings_data,
        'ARR': arr_data,
        'CARR': carr_data
    }
    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    print(result_df)
    print(expected_df)

    assert result_df.equals(expected_df)

def test_populate_bkings_carr_arr_df_case3(db_engine_case3):

    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    customer = None
    contract = None
    result_df = populate_bkings_carr_arr_df(start_date, end_date, db_engine_case3, customer, contract)

    # Generate expected data
    bookings_data = [0]*4 + [120000.0] + [0]*11 + [60000.0] + [0]*7
    arr_data = [0]*5 + [120000.0]*12 + [60000.0]*7
    carr_data = [0]*4 + [120000.0]*13 + [60000.0]*7

    expected_data_dict = {
        'Bookings': bookings_data,
        'ARR': arr_data,
        'CARR': carr_data
    }
    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    print(result_df)
    print(expected_df)

    assert result_df.equals(expected_df)

def test_populate_bkings_carr_arr_df_case4(db_engine_case4):

    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    customer = None
    contract = None
    result_df = populate_bkings_carr_arr_df(start_date, end_date, db_engine_case4, customer, contract)

    # Generate expected data
    bookings_data = [0]*4 + [60000.0] + [0]*19
    arr_data = [0]*5 + [120000.0]*6 + [0]*13
    carr_data = [0]*4 + [120000.0]*7 + [0]*13

    expected_data_dict = {
        'Bookings': bookings_data,
        'ARR': arr_data,
        'CARR': carr_data
    }

    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    print(result_df)
    print(expected_df)

    assert result_df.equals(expected_df)
