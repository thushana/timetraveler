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

### Usage

Common project tasks can be simplified using the provided `Makefile` commands:

1. **Set up the environment and initialize the database:**
   ```bash
   make setup
   ```

2. **Run the journey cron script in debug mode:**
   ```bash
   make run
   ```

3. **Apply Alembic migrations manually:**
   ```bash
   make migrate
   ```

4. **Reset the database (drop and recreate):**
   ```bash
   make reset-db
   ```

5. **Clean the virtual environment:**
   ```bash
   make clean
   ```
