# quanta/tests/test_mesh_resilience.py

import time
from quanta.mesh.mesh_supervisor import MeshSupervisor

def simulate_agent_failure(supervisor, fail_agent="strategist", fail_times=4, health_interval=1):
    # Access the actual agent object
    agent = supervisor.orchestrator.agents[fail_agent]

    # Save the original ping method
    orig_ping = agent.ping

    # Monkey-patch ping to simulate failure N times, then restore
    call_count = {"count": 0}
    def fail_ping():
        if call_count["count"] < fail_times:
            call_count["count"] += 1
            return False
        return True  # After N fails, report healthy

    agent.ping = fail_ping

    print(f"\n[TEST] Forcing {fail_agent} to fail {fail_times} times, then recover.")
    supervisor.start()
    # Let health checks run for (fail_times + 2) intervals
    time.sleep((fail_times + 2) * health_interval)
    supervisor.stop()

    # Restore original ping
    agent.ping = orig_ping

    # Print last 10 audit log lines
    logs = supervisor.audit.query(10)
    print("\n--- Last 10 audit log lines ---")
    for line in logs:
        print(line.strip())

if __name__ == "__main__":
    supervisor = MeshSupervisor(health_interval=1)
    simulate_agent_failure(supervisor)
