import datetime


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
    def __init__(self, segment_id, contract_id, contract_date, renewal_from_contract_id, segment_start_date, segment_end_date, arr_override_start_date, arr_override_note, title, segment_type, segment_value, total_contract_value):
        self.segment_id = segment_id
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

            
# Updated condition and action functions to use SegmentData
def has_arr_override(segment_context):
    return segment_context.segment_data.arr_override_start_date is not None

def booked_before_segment_start(segment_context):
    return segment_context.segment_data.contract_date < segment_context.segment_data.segment_start_date

def segment_start_before_booked(segment_context):
    return segment_context.segment_data.segment_start_date <= segment_context.segment_data.contract_date

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
            contract_length_months = round((segment_context.segment_data.segment_end_date - segment_context.arr_start_date).days / 30.42)
            segment_context.arr = (segment_context.segment_data.segment_value / contract_length_months) * 12
            segment_context.length_variance_alert = (contract_length_months % 1) > 0.2


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

        arr_end_date = self.segment_data.segment_end_date
            
        arr_calculation_table.evaluate(self)

        
# Sample SegmentData instances
segment_data1 = SegmentData(
    segment_id=201,
    contract_id=101,
    contract_date=datetime.date(2024, 1, 1),
    renewal_from_contract_id=None,
    segment_start_date=datetime.date(2024, 1, 1),
    segment_end_date=datetime.date(2024, 7, 1),
    arr_override_start_date=None,
    arr_override_note=None,
    title="First Half",
    segment_type="Standard",
    segment_value=60000,
    total_contract_value=120000
)

segment_data2 = SegmentData(
    segment_id=202,
    contract_id=101,
    contract_date=datetime.date(2024, 1, 1),
    renewal_from_contract_id=None,
    segment_start_date=datetime.date(2024, 7, 2),
    segment_end_date=datetime.date(2025, 1, 1),
    arr_override_start_date=datetime.date(2024, 8, 1),
    arr_override_note="Special Arrangement",
    title="Second Half",
    segment_type="Special",
    segment_value=60000,
    total_contract_value=120000
)

# Example usage with SegmentData
for segment_data in [segment_data1, segment_data2]:
    context = SegmentContext(segment_data)
    context.calculate_arr()
    print(f"ARR Start Date for segment {segment_data.segment_id}: {context.arr_start_date}")
    print(f"ARR for segment {segment_data.segment_id}: {context.arr}")
    print(f"Contract Length Variance Alert for segment {segment_data.segment_id}: {'Yes' if context.length_variance_alert else 'No'}")

