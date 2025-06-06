import pyodbc
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()

# also need psycopy installed

username = os.getenv('USERNAME', '')
password = os.getenv('PASSWORD', '')
host = os.getenv('HOST', '')
port = os.getenv('PORT', '5432')  # Default PostgreSQL port
database = os.getenv('DATABASE', '')

conn_str = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"


def get_db():
    engine = create_engine(conn_str, echo=True)
    return engine

