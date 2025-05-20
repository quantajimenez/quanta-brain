import os
import pandas as pd

# Define file paths relative to this script location
PLAN_FILE = os.path.join(os.path.dirname(__file__), '..', 'Quanta_Execution_Master_Plan_v2.3.xlsx')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'Execution LOGS Master.xlsx')

# Load plan and log as DataFrames
plan_df = pd.read_excel(PLAN_FILE)
log_df = pd.read_excel(LOG_FILE)

print("Loaded plan shape:", plan_df.shape)
print("Loaded log shape:", log_df.shape)
print("First few rows of plan:\n", plan_df.head())
print("First few rows of log:\n", log_df.head())
