import pytest
import psycopg2
import pandas as pd
from scripts.database_handler import load_data_to_database, load_config, create_connection


# Setup & Teardown for Test Database
@pytest.fixture(scope="module")
def test_db():
    """Create a temporary PostgreSQL test database and provide a connection."""
    db_config = load_config()
    test_db_name = "test_fhir_db"

    # Connect to the main database to create a test DB
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        dbname="postgres",
        user=db_config["user"],
        password=db_config["password"]
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Drop existing test DB and create a new one
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cursor.execute(f"CREATE DATABASE {test_db_name}")

    cursor.close()
    conn.close()

    # Use the new test DB connection
    db_config["dbname"] = test_db_name
    yield db_config

    # Teardown: Drop the test database after tests
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        dbname="postgres",
        user=db_config["user"],
        password=db_config["password"]
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{test_db_name}' AND pid <> pg_backend_pid();
    """)
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cursor.close()
    conn.close()


# Sample DataFrames for Testing
@pytest.fixture
def sample_data():
    """Provides sample patient, condition, and encounter data as DataFrames."""
    df_patient = pd.DataFrame([
        {"id": "P123", "first_name": "John", "last_name": "Doe", "gender": "male", "birthDate": "1980-01-01"}
    ])

    df_condition = pd.DataFrame([
        {"id": "C001", "clinical_status": "active", "verification_status": "confirmed",
         "condition_code": "H123", "condition_display": "Hypertension",
         "subject_reference": "P123", "encounter_reference": "E456"}
    ])

    df_encounter = pd.DataFrame([
        {"id": "E456", "status": "finished", "class_code": "outpatient",
         "subject_reference": "P123", "period_start": "2023-01-01T10:00:00"}
    ])

    return df_patient, df_condition, df_encounter


#  Test: Ensure Tables are Created
def test_table_creation(test_db, sample_data):
    """Test if tables are created correctly in the database."""
    db_config = test_db

    # Load sample data
    df_patient, df_condition, df_encounter = sample_data
    load_data_to_database(df_patient, df_condition, df_encounter, db_config)

    # Connect to test DB
    conn = create_connection(db_config)
    cursor = conn.cursor()

    # Check if tables exist
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'patient');")
    assert cursor.fetchone()[0] is True, "Patient table not created!"

    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'condition');")
    assert cursor.fetchone()[0] is True, "Condition table not created!"

    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'encounter');")
    assert cursor.fetchone()[0] is True, "Encounter table not created!"

    cursor.close()
    conn.close()


# Test: Insert Data and Verify
def test_data_insertion(test_db, sample_data):
    """Test if data is correctly inserted into the database."""
    db_config = test_db

    # Load sample data
    df_patient, df_condition, df_encounter = sample_data
    load_data_to_database(df_patient, df_condition, df_encounter, db_config)

    # Connect to test DB
    conn = create_connection(db_config)
    cursor = conn.cursor()

    # Check Patient Data
    cursor.execute("SELECT * FROM patient")
    patient_records = cursor.fetchall()
    assert len(patient_records) == 1, "Patient data not inserted correctly!"

    # Check Condition Data
    cursor.execute("SELECT * FROM condition")
    condition_records = cursor.fetchall()
    assert len(condition_records) == 1, "Condition data not inserted correctly!"

    # Check Encounter Data
    cursor.execute("SELECT * FROM encounter")
    encounter_records = cursor.fetchall()
    assert len(encounter_records) == 1, "Encounter data not inserted correctly!"

    cursor.close()
    conn.close()
