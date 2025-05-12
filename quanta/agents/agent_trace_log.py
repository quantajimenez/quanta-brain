# quanta/agents/agent_trace_log.py

def log_agent_activity(agent_name, action, module="", result="PENDING"):
    print(f"[AGENT TRACE] Agent: {agent_name} | Action: {action} | Module: {module} | Result: {result}")
