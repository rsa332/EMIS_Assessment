from scripts.extract import extract_data
from scripts.transform import transform_data
from scripts.database_handler import load_config, load_data_to_database


def main():
    # Step 1: Extract Data
    df_patient, df_condition, df_encounter = extract_data()

    # Step 2: Transform Data
    df_patient_transformed, df_condition_transformed, df_encounter_transformed = transform_data(df_patient,
                                                                                                df_condition,
                                                                                                df_encounter)

    # Step 3: Load Data to Database
    db_config = load_config()
    load_data_to_database(df_patient_transformed, df_condition_transformed, df_encounter_transformed, db_config)


if __name__ == '__main__':
    main()
