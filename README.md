# TimeTraveler → ⏱️ 🚗 🚶‍♂️ 🚲 🚌

(In progress - Basic direction timing captured, now working on saving it into a database)

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

### How We Chose 15-Minute Time Slices

We carefully considered how to divide and track time in our system. After exploring various options, including looking into Department of Transportation standards, we settled on a structure that combines precise measurement intervals with natural time periods:

- We use **15-minute measurement intervals**, based on reading the FHWA Traffic Monitoring Guide and Travel Time Data Collection Handbook  ([Source](https://www.fhwa.dot.gov/policyinformation/tmguide/2022_TMG_Updated_20241008.pdf))
- We divided the 24-hour day into **six equal 4-hour periods**:
  - **Overnight** (00:00-03:59)
  - **Dawn** (04:00-07:59)
  - **Morning** (08:00-11:59)
  - **Afternoon** (12:00-15:59)
  - **Evening** (16:00-19:59)
  - **Night** (20:00-23:59)
- Each poll of the travel time is slotted into one of these intervals to speed analysis.

**References:**
- [Travel Time Data Collection Handbook - US DOT](https://www.fhwa.dot.gov/ohim/tvtw/natmec/00020.pdf)
- [Traffic Monitoring Guide – US DOT](https://www.fhwa.dot.gov/policyinformation/tmguide/2022_TMG_Updated_20241008.pdf)
