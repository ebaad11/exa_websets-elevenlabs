from simple_websets import SeriesATracker

# Use with default parameters
tracker = SeriesATracker()
results = tracker.run()

# Or customize any parameter to match the original Series A in SF config
custom_tracker = SeriesATracker(
    timeout_minutes=10,
    query="companies in SF that just raised their series A last week",
    criteria=[
        {"description": "company is headquartered in san francisco, ca"},
        {"description": "completed a series a fundraising round between 2025-06-24 and 2025-07-01"}
    ],
    days_lookback=7,
    result_count=5,
    entity_type="company",
    output_dir="websites",
    file_prefix="series_a_companies"
)

# Access step by step
custom_tracker.create_webset()
webset = custom_tracker.wait_for_completion()
items = custom_tracker.get_webset_items()
file_path = custom_tracker.save_results()