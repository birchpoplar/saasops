import pytest
from src.calc import populate_metrics_df
from datetime import datetime
import pandas as pd

def test_populate_metrics_df_case1(db_engine_case1):
    
    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    customer = None
    contract = None
    result_df = populate_metrics_df(start_date, end_date, db_engine_case1, customer, contract)

    # Generate expected data

    starting_mrr = [0]*6 + [10000.0]*12 + [0]*6
    new_mrr = [0]*5 + [10000.0] + [0]*18
    expansion_mrr = [0.0]*24
    churn_mrr = [0]*17 + [10000.0] + [0]*6
    contraction_mrr = [0.0]*24
    ending_mrr = [0]*5 + [10000.0]*12 + [0]*7
    
    expected_data_dict = {
        'New MRR': new_mrr,
        'Churn MRR': churn_mrr,
        'Expansion MRR': expansion_mrr,
        'Contraction MRR': contraction_mrr,
        'Starting MRR': starting_mrr,
        'Ending MRR': ending_mrr
    }
    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    assert result_df.equals(expected_df)

def test_populate_metrics_df_case2(db_engine_case2):

    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    customer = None
    contract = None
    result_df = populate_metrics_df(start_date, end_date, db_engine_case2, customer, contract)

    # Generate expected data

    starting_mrr = [0]*6 + [10000.0]*12 + [20000.0]*6
    new_mrr = [0]*5 + [10000.0] + [0]*18
    expansion_mrr = [0]*17 + [10000.0] + [0]*6
    churn_mrr = [0.0]*24
    contraction_mrr = [0.0]*24
    ending_mrr = [0]*5 + [10000.0]*12 + [20000.0]*7

    expected_data_dict = {
        'New MRR': new_mrr,
        'Churn MRR': churn_mrr,
        'Expansion MRR': expansion_mrr,
        'Contraction MRR': contraction_mrr,
        'Starting MRR': starting_mrr,
        'Ending MRR': ending_mrr
    }
    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    assert result_df.equals(expected_df)

def test_populate_metrics_df_case3(db_engine_case3):

    start_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
    customer = None
    contract = None
    result_df = populate_metrics_df(start_date, end_date, db_engine_case3, customer, contract)

    # Generate expected data

    starting_mrr = [0]*6 + [10000.0]*12 + [5000.0]*6
    new_mrr = [0]*5 + [10000.0] + [0]*18
    expansion_mrr = [0.0]*24
    churn_mrr = [0.0]*24
    contraction_mrr = [0]*17 + [5000.0] + [0]*6
    ending_mrr = [0]*5 + [10000.0]*12 + [5000.0]*7
    
    expected_data_dict = {
        'New MRR': new_mrr,
        'Churn MRR': churn_mrr,
        'Expansion MRR': expansion_mrr,
        'Contraction MRR': contraction_mrr,
        'Starting MRR': starting_mrr,
        'Ending MRR': ending_mrr
    }

    date_range = pd.date_range(start_date, end_date, freq='M')
    expected_df = pd.DataFrame(
        expected_data_dict,
        index=pd.to_datetime(date_range)
    )

    assert result_df.equals(expected_df)
