# quanta/tests/failure_trace_log.py

def log_test_failure(test_name, reason, severity="CRITICAL"):
    print(f"[TEST FAILURE] Test: {test_name} | Reason: {reason} | Severity: {severity}")
