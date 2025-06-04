import json


def record_to_dict(record):
    if record is None:
        return None
    # Convert Record to dict
    data = dict(record._mapping)
    # Parse JSON fields if any
    if "options" in data and isinstance(data["options"], str):
        try:
            data["options"] = json.loads(data["options"])
        except json.JSONDecodeError:
            pass
    return data


def records_to_list(records):
    return [record_to_dict(r) for r in records]
