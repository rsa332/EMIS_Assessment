import psycopg2
from io import StringIO
import os
import json


def load_config():
    # Load config from JSON file as default
    with open("config.json", "r") as f:
        config = json.load(f)

    # Override with environment variables if set
    db_config = config["db_config"]
    db_config["host"] = os.getenv("DB_HOST", db_config["host"])
    db_config["port"] = int(os.getenv("DB_PORT", db_config["port"]))
    db_config["dbname"] = os.getenv("DB_NAME", db_config["dbname"])
    db_config["user"] = os.getenv("DB_USER", db_config["user"])
    db_config["password"] = os.getenv("DB_PASSWORD", db_config["password"])

    return db_config


# Create a PostgreSQL connection
def create_connection(db_config):
    conn = psycopg2.connect(
        host=db_config['host'],
        port=db_config['port'],
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password']
    )
    return conn


# Function to create table schema dynamically based on DataFrame
def create_table_schema(df, table_name):
    column_defs = []
    for column in df.columns:
        column_defs.append(f'"{column}" VARCHAR')

    create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(column_defs)}
    );
    '''

    return create_table_sql


def load_df_to_postgresql_using_copy(df, table_name, db_config):
    conn = create_connection(db_config)
    cursor = conn.cursor()

    # Ensure table exists
    create_table_sql = create_table_schema(df, table_name)
    cursor.execute(create_table_sql)
    conn.commit()

    cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")

    # Prepare the DataFrame for insertion by writing it to a StringIO buffer
    output = StringIO()
    df.to_csv(output, index=False, header=False)  # Write to CSV without index and header
    output.seek(0)  # Move back to the beginning of the StringIO buffer

    # Try to insert
    try:
        cursor.copy_from(output, table_name, sep=',', null="")
        conn.commit()
    except Exception as e:
        print(f" Error inserting data into {table_name}: {e}")

    cursor.close()
    conn.close()


# Main function to load data into the database
def load_data_to_database(df_patient, df_condition, df_encounter, db_config):
    load_df_to_postgresql_using_copy(df_patient, 'patient', db_config)
    load_df_to_postgresql_using_copy(df_condition, 'condition', db_config)
    load_df_to_postgresql_using_copy(df_encounter, 'encounter', db_config)
    print("Data loaded successfully into the database.")
