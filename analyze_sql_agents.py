"""
SQL Server Agent Job Analyzer
Analyzes SQL Server Agent jobs and generates descriptions based on job step commands.
"""

import json
import sys
from typing import List
import pandas as pd
from sqlalchemy import create_engine

# Load configuration
def load_config(config_path: str = 'config.json') -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        print("Please create config.json from config.example.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)

# Read csv file containing job IDs
def read_job_ids(file_path: str) -> List[str]:
    """Read job IDs from CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df['job_id'].tolist()
    except Exception as e:
        print(f"Error reading job IDs from {file_path}: {e}")
        sys.exit(1)

def create_connection_string(config: dict) -> str:
    """Create SQL Server connection string from configuration."""
    server = config.get('server')
    database = config.get('database', 'msdb')
    driver = config.get('driver', 'ODBC Driver 17 for SQL Server')
    
    if config.get('use_windows_auth', True):
        conn_string = f'mssql+pyodbc://{server}/{database}?driver={driver}&trusted_connection=yes'
    else:
        username = config.get('username')
        password = config.get('password')
        conn_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}'
    
    return conn_string

# Load configuration
config = load_config()

# Create SQLAlchemy engine
connection_string = create_connection_string(config)
engine = create_engine(connection_string)

# Read job IDs from config or CSV
job_ids = config.get('job_ids', []) or read_job_ids('job_ids.csv')

if not job_ids:
    print("Error: No job IDs found in configuration or job_ids.csv")
    sys.exit(1)

print(f"Processing {len(job_ids)} job(s)...")

# Build query with all job IDs at once (more efficient than looping)
job_ids_str = "', '".join(job_ids)
jobs_query = f""" 
SELECT
    j.job_id,
    j.name AS job_name,
    j.enabled,
    j.description,
    SUSER_SNAME(j.owner_sid) AS job_owner,
    j.date_created,
    j.date_modified,
    
    -- Job Step Info
    js.step_id,
    js.step_name,
    js.subsystem,
    js.command,
    js.database_name,
    js.retry_attempts,
    js.retry_interval,
    
    -- Schedule Info
    sch.name AS schedule_name,
    sch.enabled AS schedule_enabled,
    sch.freq_type,
    sch.freq_interval,
    sch.freq_subday_type,
    sch.freq_subday_interval
 
FROM msdb.dbo.sysjobs j
LEFT JOIN msdb.dbo.sysjobsteps js
    ON j.job_id = js.job_id
LEFT JOIN msdb.dbo.sysjobschedules jsched
    ON j.job_id = jsched.job_id
LEFT JOIN msdb.dbo.sysschedules sch
    ON jsched.schedule_id = sch.schedule_id
WHERE j.job_id IN ('{job_ids_str}')
ORDER BY j.name, js.step_id;
"""

# Execute query and fetch all jobs at once
try:
    with engine.connect() as connection:
        jobs = pd.read_sql(jobs_query, connection)
        print(f"Successfully retrieved {len(jobs)} job step(s)")
except Exception as e:
    print(f"Error executing query: {e}")
    sys.exit(1)

# Create a spreadsheet of the job ID, name, and the command formatted as SQL for use in the LLM prompt
jobs_for_prompt = jobs[['job_id', 'job_name', 'command']]

# Save to CSV
output_file = 'jobs_for_prompt.csv'
jobs_for_prompt.to_csv(output_file, index=False)
print(f"Results saved to {output_file}")