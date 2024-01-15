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

class Segment:
    def __init__(self, segment_id, contract_id, segment_start_date, segment_end_date, arr_override_start_date, arr_override_note, title, segment_type, segment_value):
        self.segment_id = segment_id
        self.contract_id = contract_id
        self.segment_start_date = segment_start_date
        self.segment_end_date = segment_end_date
        self.arr_override_start_date = arr_override_start_date
        self.arr_override_note = arr_override_note
        self.title = title
        self.segment_type = segment_type
        self.segment_value = segment_value

class ARRStartDateDecisionTable:
    def __init__(self):
        self.rules = []

    def add_rule(self, condition, action):
        self.rules.append((condition, action))

    def evaluate(self, segment_context):
        for condition, action in self.rules:
            if condition(segment_context):
                return action(segment_context)

# Create condition functions
def has_arr_override(segment_context):
    return segment_context.segment.arr_override_start_date is not None

def booked_before_segment_start(segment_context):
    return segment_context.contract.contract_date < segment_context.segment.segment_start_date

def segment_start_before_booked(segment_context):
    return segment_context.segment.segment_start_date <= segment_context.contract.contract_date

# Create action functions
def set_arr_to_override(segment_context):
    return segment_context.segment.arr_override_start_date

def set_arr_to_booked_date(segment_context):
    return segment_context.contract.contract_date

def set_arr_to_segment_start(segment_context):
    return segment_context.segment.segment_start_date
            
class ARRCalculationDecisionTable:
    def __init__(self):
        pass

    def evaluate(self, segment_context):
        if segment_context.arr_start_date is not None:
            contract_length_months = round((segment_context.segment.segment_end_date - segment_context.arr_start_date).days / 30.42)
            segment_context.arr = (segment_context.segment.segment_value / contract_length_months) * 12
            segment_context.length_variance_alert = (contract_length_months % 1) > 0.2

class SegmentContext:
    def __init__(self, contract, segment):
        self.contract = contract
        self.segment = segment
        self.arr_start_date = None
        self.arr_end_date = segment.segment_end_date
        self.arr = None
        self.length_variance_alert = False

    def calculate_arr(self):
        arr_start_decision_table = ARRStartDateDecisionTable()
        arr_calculation_table = ARRCalculationDecisionTable()

        arr_start_decision_table.add_rule(has_arr_override, set_arr_to_override)
        arr_start_decision_table.add_rule(booked_before_segment_start, set_arr_to_booked_date)
        arr_start_decision_table.add_rule(segment_start_before_booked, set_arr_to_segment_start)

        # Updated section for setting arr_start_date
        evaluated_date = arr_start_decision_table.evaluate(self)
        if evaluated_date:
            self.arr_start_date = evaluated_date

        arr_calculation_table.evaluate(self)

        
# Sample Data
customer1 = Customer(customer_id=1, name="Acme Corp", city="New York", state="NY")

# Creating a contract
contract1 = Contract(
    contract_id=101,
    customer_id=customer1.customer_id,
    renewal_from_contract_id=None,
    reference="C-2024-ACME",
    contract_date=datetime.date(2024, 1, 1),
    term_start_date=datetime.date(2024, 1, 1),
    term_end_date=datetime.date(2025, 1, 1),
    total_value=120000
)

# Creating segments for the contract
segment1 = Segment(
    segment_id=201,
    contract_id=contract1.contract_id,
    segment_start_date=datetime.date(2024, 1, 1),
    segment_end_date=datetime.date(2024, 7, 1),
    arr_override_start_date=None,
    arr_override_note=None,
    title="First Half",
    segment_type="Standard",
    segment_value=60000
)

segment2 = Segment(
    segment_id=202,
    contract_id=contract1.contract_id,
    segment_start_date=datetime.date(2024, 7, 2),
    segment_end_date=datetime.date(2025, 1, 1),
    arr_override_start_date=datetime.date(2024, 8, 1),
    arr_override_note="Special Arrangement",
    title="Second Half",
    segment_type="Special",
    segment_value=60000
)

# Adding segments to the contract
contract1.segments.append(segment1)
contract1.segments.append(segment2)

        
# Example usage
for segment in contract1.segments:
    context = SegmentContext(contract1, segment)
    context.calculate_arr()
    print(f"ARR Start Date for segment {segment.segment_id}: {context.arr_start_date}")
    print(f"ARR for segment {segment.segment_id}: {context.arr}")
    print(f"Contract Length Variance Alert for segment {segment.segment_id}: {'Yes' if context.length_variance_alert else 'No'}")



