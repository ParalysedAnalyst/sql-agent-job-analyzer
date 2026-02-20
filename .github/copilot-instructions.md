## SQL Server Agent Job Analyzer

Python project to analyze SQL Server Agent jobs, extract command content, and export for analysis.

### Project Goals
1. Connect to SQL Server and retrieve Agent job information
2. Extract and format SQL command content from job steps
3. Output results with job_id, name, and commands for analysis
4. Support batch processing of multiple jobs efficiently

### Key Dependencies
- pyodbc: SQL Server connectivity (via SQLAlchemy)
- pandas: Data manipulation and CSV export
- sqlalchemy: Database abstraction and connection management

### Setup Progress
- [x] Project directory created
- [x] Dependencies identified and documented
- [x] Configuration system implemented (config.json)
- [x] Main script created and optimized
- [x] Documentation updated
- [ ] Virtual environment configured
- [ ] Testing completed

### Usage
1. Create config.json from config.example.json with your SQL Server details
2. Add job IDs to config.json or job_ids.csv
3. Run: `python analyze_sql_agents.py`
4. Output will be saved to jobs_for_prompt.csv