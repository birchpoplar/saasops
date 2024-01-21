from enum import Enum
import pandas as pd
import datetime


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
        arr_start_decision_table = ARRStartDateDecisionTable()
        arr_calculation_table = ARRCalculationDecisionTable()

        arr_start_decision_table.add_rule(has_arr_override, set_arr_to_override)
        arr_start_decision_table.add_rule(booked_before_segment_start, set_arr_to_booked_date)
        arr_start_decision_table.add_rule(segment_start_before_booked, set_arr_to_segment_start)

        evaluated_date = arr_start_decision_table.evaluate(self)
        if evaluated_date:
            self.arr_start_date = evaluated_date

        arr_calculation_table.evaluate(self)

        
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

    def calculate_arr_changes(self):
        # Filter data for the current period
        df = self.arr_table.data
        period_data = df[(df['ARRStartDate'] <= self.end_period) & (df['ARREndDate'] >= self.start_period)]

        # Calculate ARR changes
        for _, row in period_data.iterrows():
            contract_id, total_arr, min_start_date = row['ContractID'], row['ARR'], row['ARRStartDate']

            if self.is_new_contract(min_start_date):
                self.metrics['New'] += total_arr
            elif self.is_contract_ending(contract_id):
                change = self.calculate_contract_change(contract_id, total_arr)
                if change > 0:
                    self.metrics['Expansion'] += change
                elif change < 0:
                    self.metrics['Contraction'] += abs(change)
                else:
                    self.metrics['Churn'] += total_arr

    def is_new_contract(self, start_date):
        return start_date >= self.start_period

    def is_contract_ending(self, contract_id):
        # Check if the contract is ending within the period
        df = self.arr_table.data
        return any((df['ContractID'] == contract_id) & (df['ARREndDate'] <= self.end_period))

    def calculate_contract_change(self, contract_id, current_total_arr):
        # Get the previous ARR value for comparison
        df = self.arr_table.data
        prev_period_data = df[(df['ContractID'] == contract_id) & (df['ARRStartDate'] < self.start_period)]
        previous_arr = prev_period_data['ARR'].sum() if not prev_period_data.empty else 0
        return current_total_arr - previous_arr

    def reset_metrics(self):
        self.metrics = {key: 0 for key in self.metrics}

class ARRTable:
    def __init__(self):
        columns = ['SegmentID', 'ContractID', 'RenewalFromContractID', 'ARRStartDate', 'ARREndDate', 'ARR']
        self.data = pd.DataFrame()

    def add_row(self, segment_data, context):
        new_row = pd.DataFrame([{
            "SegmentID": segment_data.segment_id, 
            "ContractID": segment_data.contract_id,
            "RenewalFromContractID": segment_data.renewal_from_contract_id,
            "CustomerName": segment_data.customer_name,
            "ARRStartDate": pd.to_datetime(context.arr_start_date),
            "ARREndDate": pd.to_datetime(context.arr_end_date),
            "ARR": context.arr
        }])
        self.data = pd.concat([self.data, new_row], ignore_index=True)        

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
