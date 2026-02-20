# SQL Server Agent Job Analyzer

Analyzes SQL Server Agent jobs and extracts SQL command content for documentation and analysis.

## Features

- **Job Information Retrieval**: Connects to SQL Server msdb and fetches job details including job steps, commands, and schedules
- **SQL Command Extraction**: Extracts SQL commands from job steps for analysis
- **Batch Processing**: Efficiently analyzes multiple jobs in a single query
- **CSV Export**: Generates CSV output with job ID, name, and commands

## Requirements

- Python 3.8+
- SQL Server (with ODBC Driver 17 for SQL Server)
- Read access to msdb database

## Installation

1. Clone or download this project
2. Create virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy `config.example.json` to `config.json`:
   ```bash
   copy config.example.json config.json
   ```

2. Edit `config.json` with your SQL Server details:
   ```json
   {
     "server": "YOUR_SERVER_NAME",
     "database": "msdb",
     "use_windows_auth": true,
     "job_ids": [
       "C5771573-7CF1-4BD7-A6A2-588BDD0E4532"
     ]
   }
   ```

### Connection Options

**Windows Authentication** (recommended):
```json
{
  "server": "SERVER_NAME",
  "database": "msdb",
  "use_windows_auth": true
}
```

**SQL Authentication**:
```json
{
  "server": "SERVER_NAME",
  "database": "msdb",
  "use_windows_auth": false,
  "username": "sa",
  "password": "your_password"
}
```

### Job IDs Configuration

You can specify job IDs in two ways:

1. **In config.json** (preferred):
   ```json
   {
     "job_ids": [
       "C5771573-7CF1-4BD7-A6A2-588BDD0E4532",
       "99BC277A-E1CA-4F40-A4E5-64E90BFA42D5"
     ]
   }
   ```

2. **In job_ids.csv** (fallback):
   Create a CSV file with a `job_id` column containing the job GUIDs

## Usage

```bash
python analyze_sql_agents.py
```

### Output

The script generates `jobs_for_prompt.csv` containing:
- job_id: The SQL Server Agent job GUID
- job_name: The name of the job
- command: The SQL command(s) from the job steps

## SQL Query

The analyzer executes this query to retrieve job information:

```sql
SELECT
    j.job_id,
    j.name AS job_name,
    j.enabled,
    j.description,
    SUSER_SNAME(j.owner_sid) AS job_owner,
    j.date_created,
    j.date_modified,
    js.step_id,
    js.step_name,
    js.subsystem,
    js.command,
    js.database_name,
    js.retry_attempts,
    js.retry_interval,
    sch.name AS schedule_name,
    sch.enabled AS schedule_enabled,
    sch.freq_type,
    sch.freq_interval,
    sch.freq_subday_type,
    sch.freq_subday_interval
FROM msdb.dbo.sysjobs j
LEFT JOIN msdb.dbo.sysjobsteps js ON j.job_id = js.job_id
LEFT JOIN msdb.dbo.sysjobschedules jsched ON j.job_id = jsched.job_id
LEFT JOIN msdb.dbo.sysschedules sch ON jsched.schedule_id = sch.schedule_id
WHERE j.job_id IN (@job_ids)
ORDER BY j.name, js.step_id
```

## Troubleshooting

### ODBC Driver Not Found
Install ODBC Driver 17 for SQL Server:
- [Download from Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Connection Failed
- Verify server name (use FQDN or IP if needed)
- Check Windows/SQL authentication credentials
- Ensure firewall allows SQL Server port (default 1433)
- Verify you have permissions on msdb database
- Test connection: `sqlcmd -S SERVER_NAME -d msdb -Q "SELECT @@VERSION"`

### Job Not Found
- Ensure job_id GUID format is correct
- Verify you have read permissions on msdb database
- Check that the jobs exist: `SELECT job_id, name FROM msdb.dbo.sysjobs`

## License

MIT