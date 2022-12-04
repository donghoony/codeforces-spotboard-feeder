import json

def handle_to_id(handle):
    with open("python_scripts/handle_to_id.json", "r", encoding="utf-8") as f:
        h2i = json.load(f)    
    handle = handle.lower()
    if handle not in h2i:
        return 500
    return h2i[handle]