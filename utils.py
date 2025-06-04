import json
from datetime import datetime

def record_to_dict(record):
    """Convert a database record to a dictionary"""
    if record is None:
        return None

    result = {}
    for key, value in record.items():
        if key == "options" and isinstance(value, str):
            # Parse JSON string to list for options
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                result[key] = value
        elif isinstance(value, datetime):
            # Convert datetime to ISO format string
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

def records_to_list(records):
    """Convert a list of database records to a list of dictionaries"""
    return [record_to_dict(record) for record in records]