# setup_db.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os
import subprocess

def init_database():
    load_dotenv()
    
    # Connect to default postgres database
    conn = psycopg2.connect(
        dbname='postgres',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cur = conn.cursor()
    
    # Check if database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ('timetraveler',))
    exists = cur.fetchone()
    
    if not exists:
        try:
            cur.execute('CREATE DATABASE timetraveler')
            print("Database created successfully")
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    
    cur.close()
    conn.close()
    
    # Run Alembic migrations
    try:
        subprocess.run(['alembic', 'upgrade', 'head'], check=True)
        print("Migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        return False

if __name__ == "__main__":
    init_database()