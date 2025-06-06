import pyodbc
from sqlalchemy import create_engine

# also need psycopy installed

username = 'postgres'
password = '!#6Mikto6!#'
host = 'goliath.c0f6mwm6g5ra.us-east-1.rds.amazonaws.com'
port = "5432"
database = 'goliath'

conn_str = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"


def get_db():
    engine = create_engine(conn_str, echo=True)
    return engine

