# TimeTraveler → ⏱️ 🚗 🚶‍♂️ 🚲 🚌 

TimeTraveler is a route traffic analysis system designed to study and compare traffic patterns on specific routes over time across different modes. It captures and analyzes route data at 15-minute intervals, to deliver insight on traffic patterns across days, weeks, months and years.

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Virtual environment tool (venv recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/thushana/timetraveler
cd timetraveler
```

2. Create and activate a virtual environment:
```bash
python -m venv timetraveler_venv
source timetraveler_venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env # Edit .env with your configuration settings
```

5. Initialize the database:
```bash
python scripts/setup_db.py
```

### Project Structure
The project consists of several key components that work together to collect and analyze route data:
```route_processor.py``` handles the core logic for processing route information
```route_scheduler.py``` manages when and how often routes are analyzed
```route_reporter.py``` prints out the collected data
```route_cron.py``` automates regular data collection

Database migrations are managed through Alembic, with configuration in the migrations directory.