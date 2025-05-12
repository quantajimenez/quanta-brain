# quanta/memory/snapshots/memory_snapshot_registry.py
def log_snapshot(module_name, status, notes=""):
    print(f"[SNAPSHOT] Module: {module_name} | Status: {status} | Notes: {notes}")
