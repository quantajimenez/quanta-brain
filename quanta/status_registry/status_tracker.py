# quanta/status_registry/status_tracker.py
module_status = {}

def update_status(module, status):
    module_status[module] = status
    print(f"[STATUS] {module} updated to {status}")

def get_status(module):
    return module_status.get(module, "Unknown")
