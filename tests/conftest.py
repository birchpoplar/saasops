import pytest
from sqlalchemy import create_engine
import random
import string
from src.utils import print_status
from src import classes
from sqlalchemy.sql import text
from rich.console import Console

def random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def create_test_db():
    db_name = f"test_{random_string()}"
    engine = create_engine(f"postgresql://testuser:testuser@localhost/postgres")
    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT").execute(text(f"CREATE DATABASE {db_name} WITH TEMPLATE template_test_db"))
    engine.dispose()
    return db_name

def drop_test_db(db_name):
    engine = create_engine(f"postgresql://testuser:testuser@localhost/postgres")
    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT").execute(text(f"DROP DATABASE {db_name}"))
    engine.dispose()

def populate_sample_data_case1(engine):
    console = Console()
    print_status(console, "...populating sample data case 1", classes.MessageStyle.INFO)
    with open('tests/sample_data_case1.sql') as f:
        sql_stmts = f.read()

    with engine.begin() as connection:
        connection.execute(text(sql_stmts))
        
    
def populate_sample_data_case2(engine):
    pass

@pytest.fixture(scope="function")
def base_db_engine():
    db_name = create_test_db()
    engine = create_engine(f"postgresql://testuser:testuser@localhost/{db_name}")
    yield engine
    engine.dispose()
    drop_test_db(db_name)

@pytest.fixture
def db_engine_case1(base_db_engine):
    populate_sample_data_case1(base_db_engine)
    yield base_db_engine

@pytest.fixture
def db_engine_case2(base_db_engine):
    populate_sample_data_case2(base_db_engine)
    yield base_db_engine
