from enum import Enum
import pandas as pd
import datetime
import warnings


class MessageStyle(Enum):
    INFO = "blue"
    SUCCESS = "green"
    ERROR = "red"
   
class Customer:
    def __init__(self, customer_id, name, city, state):
        self.customer_id = customer_id
        self.name = name
        self.city = city
        self.state = state

        
class Contract:
    def __init__(self, contract_id, customer_id, renewal_from_contract_id, reference, contract_date, term_start_date, term_end_date, total_value):
        self.contract_id = contract_id
        self.customer_id = customer_id
        self.renewal_from_contract_id = renewal_from_contract_id
        self.reference = reference
        self.contract_date = contract_date
        self.term_start_date = term_start_date
        self.term_end_date = term_end_date
        self.total_value = total_value
        self.segments = []

        
class SegmentData:
    def __init__(self, segment_id, customer_id, customer_name, contract_id, contract_date, renewal_from_contract_id, segment_start_date, segment_end_date, arr_override_start_date, arr_override_note, title, segment_type, segment_value, total_contract_value):
        self.segment_id = segment_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.contract_id = contract_id
        self.contract_date = contract_date
        self.renewal_from_contract_id = renewal_from_contract_id
        self.segment_start_date = segment_start_date
        self.segment_end_date = segment_end_date
        self.arr_override_start_date = arr_override_start_date
        self.arr_override_note = arr_override_note
        self.title = title
        self.segment_type = segment_type
        self.segment_value = segment_value
        self.total_contract_value = total_contract_value

        
class ARRStartDateDecisionTable:
    def __init__(self):
        self.rules = []

    def add_rule(self, condition, action):
        self.rules.append((condition, action))

    def evaluate(self, segment_context):
        for condition, action in self.rules:
            if condition(segment_context):
                return action(segment_context)

            
# Condition functions

def has_arr_override(segment_context):
    return segment_context.segment_data.arr_override_start_date is not None

def booked_before_segment_start(segment_context):
    return segment_context.segment_data.contract_date < segment_context.segment_data.segment_start_date

def segment_start_before_booked(segment_context):
    return segment_context.segment_data.segment_start_date <= segment_context.segment_data.contract_date

def is_contract_renewal_and_dates_mismatch(segment_context):
    # Check if the contract is a renewal and the date condition is met
    renewing_contract = ... # Logic to get the renewing contract details
    if renewing_contract and (renewing_contract.term_start_date - segment_context.arr_end_date).days > 1:
        return True
    return False

# Action functions

def set_arr_to_override(segment_context):
    return segment_context.segment_data.arr_override_start_date

def set_arr_to_booked_date(segment_context):
    return segment_context.segment_data.contract_date

def set_arr_to_segment_start(segment_context):
    return segment_context.segment_data.segment_start_date


class ARRCalculationDecisionTable:
    def __init__(self):
        pass

    def evaluate(self, segment_context):
        if segment_context.arr_start_date is not None:
            # Corrected to use segment_data
            contract_length_months = round((segment_context.segment_data.segment_end_date - segment_context.segment_data.segment_start_date).days / 30.42)
            segment_context.arr = (segment_context.segment_data.segment_value / contract_length_months) * 12
            segment_context.length_variance_alert = (contract_length_months % 1) > 0.2
            
        segment_context.arr_end_date = segment_context.segment_data.segment_end_date
            

class SegmentContext:
    def __init__(self, segment_data):
        self.segment_data = segment_data
        self.arr_start_date = None
        self.arr_end_date = None
        self.arr = None
        self.length_variance_alert = False

    def calculate_arr(self):
        # Only proceed if segment type is 'Subscription'
        if self.segment_data.type == 'Subscription':
            arr_start_decision_table = ARRStartDateDecisionTable()
            arr_calculation_table = ARRCalculationDecisionTable()

            arr_start_decision_table.add_rule(has_arr_override, set_arr_to_override)
            arr_start_decision_table.add_rule(booked_before_segment_start, set_arr_to_booked_date)
            arr_start_decision_table.add_rule(segment_start_before_booked, set_arr_to_segment_start)

            evaluated_date = arr_start_decision_table.evaluate(self)
            if evaluated_date:
                self.arr_start_date = evaluated_date

            arr_calculation_table.evaluate(self)

        else:
            # If not a 'Subscription' type, set ARR to None or 0 as appropriate
            self.arr = 0  # Or None, depending on how you want to handle non-subscription types

            
class SegmentData:
    def __init__(self, segment_id, contract_id, renewal_from_contract_id, customer_name, contract_date, segment_start_date, segment_end_date, arr_override_start_date, title, type, segment_value):
        self.segment_id = segment_id
        self.contract_id = contract_id
        self.renewal_from_contract_id = renewal_from_contract_id
        self.customer_name = customer_name
        self.contract_date = contract_date
        self.segment_start_date = segment_start_date
        self.segment_end_date = segment_end_date
        self.arr_override_start_date = arr_override_start_date
        self.title = title
        self.type = type
        self.segment_value = segment_value


class ARRMetricsCalculator:
    def __init__(self, arr_table, start_period, end_period):
        self.arr_table = arr_table
        self.start_period = start_period
        self.end_period = end_period
        self.metrics = {'New': 0, 'Expansion': 0, 'Contraction': 0, 'Churn': 0}

    def calculate_arr_changes(self, carry_forward_churn=None):
        # Initialize carry_forward_churn if not provided
        if carry_forward_churn is None:
            carry_forward_churn = []

        # Filter data for the current period
        df = self.arr_table.data
        period_data = df[(df['ARRStartDate'] <= self.end_period) & (df['ARREndDate'] >= self.start_period)]

        # Additionally, consider contracts from the carry_forward_churn list
        for contract_id in carry_forward_churn:
            contract_data = df[df['ContractID'] == contract_id]
            period_data = pd.concat([period_data, contract_data])

        next_period_carry_forward = []

        # print(f"Calculating ARR changes for {len(period_data)} contracts")
        # print(f"Period start: {self.start_period}, Period end: {self.end_period}")
        # print(period_data[['ContractID', 'ARRStartDate', 'ARREndDate', 'ARR', 'RenewalFromContractID']])

        # So now we have the list of contracts that were active during the period
        # In the sequence, the tests are:
        # If a contract has an ARRStart Date in the period and is not a renewal, it is a new contract
        # If a contract has an ARRStartDate in the period and is a renewal, then:
        # If the ARR is higher than the previous ARR, it is an expansion
        # If the ARR is lower than the previous ARR, it is a contraction
        # If a contract has an ARREndDate in the period, and there is no renewal, it is churn

        for index, row in period_data.iterrows():
            # Handle new and renewal contracts
            if row['ARRStartDate'] >= self.start_period:
                if not row['RenewalFromContractID']:
                    self.metrics['New'] += row['ARR']
                else:
                    renewed_contract_id = row['RenewalFromContractID']
                    renewed_contract = df[df['ContractID'] == renewed_contract_id]
                    if not renewed_contract.empty:
                        prior_arr = renewed_contract.iloc[0]['ARR']
                        if row['ARR'] > prior_arr:
                            self.metrics['Expansion'] += row['ARR'] - prior_arr
                        elif row['ARR'] < prior_arr:
                            self.metrics['Contraction'] += prior_arr - row['ARR']

            # Adjusted churn condition to accurately account for renewals
            if row['ARREndDate'] <= self.end_period:
                if row['ContractID'] in carry_forward_churn:
                    # Process previously identified potential churn
                    self.metrics['Churn'] += row['ARR']
                    carry_forward_churn.remove(row['ContractID'])
                else:
                    # Check for renewals before marking as churn
                    next_contract_start = df[df['RenewalFromContractID'] == row['ContractID']]['ARRStartDate'].min()
                    if pd.isnull(next_contract_start) or next_contract_start > row['ARREndDate'] + pd.Timedelta(days=1):
                        if row['ARREndDate'] == self.end_period:
                            # Potential churn carried forward if ending on the last day without immediate renewal
                            next_period_carry_forward.append(row['ContractID'])
                        else:
                            # Mark as churn if no immediate renewal and not carried forward
                            self.metrics['Churn'] += row['ARR']

        # Return the list of contracts to carry forward for churn calculation in the next period
        return next_period_carry_forward

    def reset_metrics(self):
        self.metrics = {key: 0 for key in self.metrics}

class ARRTable:
    def __init__(self):
        # Define the dtypes for your DataFrame columns
        dtypes = {
            "SegmentID": 'object', 
            "ContractID": 'object',
            "RenewalFromContractID": 'object',
            "CustomerName": 'object',
            "ARRStartDate": 'datetime64[ns]',
            "ARREndDate": 'datetime64[ns]',
            "ARR": 'float'
        }
        # Initialize self.data as an empty DataFrame with these dtypes
        self.data = pd.DataFrame({col: pd.Series(dtype=typ) for col, typ in dtypes.items()})

    def add_row(self, segment_data, context):
        new_row = {
            "SegmentID": segment_data.segment_id, 
            "ContractID": segment_data.contract_id,
            "RenewalFromContractID": segment_data.renewal_from_contract_id,
            "CustomerName": segment_data.customer_name,
            "ARRStartDate": pd.to_datetime(context.arr_start_date),
            "ARREndDate": pd.to_datetime(context.arr_end_date),
            "ARR": context.arr
        }
        # Convert new_row dict to DataFrame with a single row, aligning with self.data's columns
        new_row_df = pd.DataFrame([new_row], columns=self.data.columns)

        # Suppress FutureWarning for DataFrame concatenation
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            self.data = pd.concat([self.data, new_row_df], ignore_index=True)


    def update_renewed_segment_arr_end_date(self, segment_id, new_arr_end_date):
        self.data.loc[self.data['SegmentID'] == segment_id, 'ARREndDate'] = pd.to_datetime(new_arr_end_date)
        
    def update_for_renewal_contracts(self):
        # Iterate over each row in the DataFrame
        for index, row in self.data.iterrows():
            if row['RenewalFromContractID']:
                renewing_segment_id = row['SegmentID']
                # Find the corresponding row for the renewal
                renewing_rows = self.data[self.data['SegmentID'] == renewing_segment_id]
                if not renewing_rows.empty:
                    renewing_arr_start_date = renewing_rows.iloc[0]['ARRStartDate']
                    # Find the corresponding renewed contract's end date
                    renewed_rows = self.data[self.data['ContractID'] == row['RenewalFromContractID']]
                    if not renewed_rows.empty:
                        renewed_arr_end_date = renewed_rows.iloc[0]['ARREndDate']
                        if (renewing_arr_start_date - renewed_arr_end_date).days > 1:
                            new_arr_end_date = renewing_arr_start_date - pd.Timedelta(days=1)
                            self.data.loc[index, 'ARREndDate'] = new_arr_end_date
