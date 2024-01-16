import datetime



        
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

