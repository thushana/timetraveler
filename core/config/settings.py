import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

# Determine environment and load appropriate .env file
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
env_file = Path(__file__).resolve().parent.parent.parent / f".env.{ENVIRONMENT}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # Fallback to default .env

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Data directory structure
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
METRICS_DATA_DIR = DATA_DIR / "metrics"

# Specific file paths
RAW_JOURNEYS_PATH = RAW_DATA_DIR / "journeys.json"
PROCESSED_JOURNEYS_PATH = PROCESSED_DATA_DIR / "journeys_enriched.json"

# Application settings
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))  # Thread pool size
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# Database settings
def parse_database_url() -> tuple[str, str, str, str, str]:
    """Parse DATABASE_URL if present (Heroku) or return individual components"""
    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        # Parse Heroku DATABASE_URL
        url = urlparse(database_url)
        return (
            url.username or "",
            url.password or "",
            url.hostname or "",
            str(url.port or 5432),
            url.path[1:],  # Remove leading slash
        )

    # Return individual components
    return (
        os.getenv("DB_USER", ""),
        os.getenv("DB_PASSWORD", ""),
        os.getenv("DB_HOST", ""),
        os.getenv("DB_PORT", "5432"),
        os.getenv("DB_NAME", ""),
    )


DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME = parse_database_url()
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Runtime settings
MAX_RUNTIME_SECONDS = float(os.getenv("MAX_RUNTIME_SECONDS", "60"))  # Target runtime limit
HEROKU_TIMEOUT_MARGIN = float(os.getenv("HEROKU_TIMEOUT_MARGIN", "25"))  # Safety margin for Heroku's 30s timeout

# Ensure required directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, METRICS_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def get_google_maps_api_key() -> str:
    """Get Google Maps API key from environment variables."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
    return api_key


def get_metrics_path(journey_name: str) -> Path:
    """Get the path for storing metrics for a specific journey."""
    # Create a directory for today's date
    today = datetime.now().strftime("%Y-%m-%d")
    metrics_dir = METRICS_DATA_DIR / today
    metrics_dir.mkdir(exist_ok=True)

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{journey_name.lower().replace(' ', '_')}_{timestamp}.json"
    return metrics_dir / filename


# Environment-specific settings
IS_HEROKU = "DYNO" in os.environ

# Logging settings
LOG_FORMAT = "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "DEBUG" if DEBUG and not IS_HEROKU else "INFO"
