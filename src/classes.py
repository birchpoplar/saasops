from enum import Enum
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
    def __init__(self, contracts, start_period, end_period):
        self.contracts = contracts
        self.start_period = start_period
        self.end_period = end_period
        self.metrics = {
            'New': 0,
            'Expansion': 0,
            'Contraction': 0,
            'Churn': 0
        }

    def calculate_arr_changes(self):
        for contract in self.contracts:
            if self.is_new_contract(contract):
                self.metrics['New'] += contract.total_value
            elif self.is_contract_ending(contract):
                if self.is_renewal_contract(contract):
                    change = self.calculate_renewal_change(contract)
                    if change > 0:
                        self.metrics['Expansion'] += change
                    else:
                        self.metrics['Contraction'] += abs(change)
                else:
                    self.metrics['Churn'] += contract.total_value

    def is_new_contract(self, contract):
        return self.start_period <= contract.term_start_date <= self.end_period and contract.renewal_from_contract_id is None

    def is_contract_ending(self, contract):
        return self.start_period <= contract.term_end_date <= self.end_period

    def is_renewal_contract(self, contract):
        # Logic to determine if a contract is a renewal
        # You might need to access previous contracts to check this
        return contract.renewal_from_contract_id is not None

    def calculate_renewal_change(self, contract):
        # Logic to compare the ARR of the current contract with its previous version
        # You'll need to fetch the previous contract using `contract.renewal_from_contract_id`
        # and compare its `total_value` with the current contract's `total_value`
        previous_contract = self.get_previous_contract(contract)
        if previous_contract:
            return contract.total_value - previous_contract.total_value
        return 0

    def get_previous_contract(self, contract):
        # Logic to retrieve the previous contract
        # This might involve searching your contract list or database
        for prev_contract in self.contracts:
            if prev_contract.contract_id == contract.renewal_from_contract_id:
                return prev_contract
        return None
