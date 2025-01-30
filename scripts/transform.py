import pandas as pd


# Function to clean DataFrame columns (remove commas, trim spaces)
def clean_dataframe(df):
    df = df.fillna('Unknown')
    df = df.astype(str)
    df = df.map(lambda x: x.replace(',', ' ') if isinstance(x, str) and ',' in x else x)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    return df


# Load the FHIR data into a DataFrame
def transform_data(df_patient, df_condition, df_encounter):
    # 🟢 Transform Patient Data
    df_patient['race'] = df_patient['extension'].apply(
        lambda x: next((ext['extension'][0]['valueCoding']['display'] for ext in x
                        if ext['url'] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race'), None))
    df_patient['medical_record_number'] = df_patient['identifier'].apply(
        lambda x: next((item['value'] for item in x if item.get('type', {}).get('coding', [{}])[0].get('code') == 'MR'),
                       None))
    df_patient['ssn'] = df_patient['identifier'].apply(
        lambda x: next((item['value'] for item in x if item.get('type', {}).get('coding', [{}])[0].get('code') == 'SS'),
                       None))

    df_patient['birthDate'] = pd.to_datetime(df_patient['birthDate'], errors='coerce')
    df_patient['deceasedDateTime'] = pd.to_datetime(df_patient['deceasedDateTime'], errors='coerce')

    df_patient['first_name'] = df_patient['name'].apply(
        lambda x: x[0]['given'][0] if isinstance(x, list) and len(x) > 0 else None)
    df_patient['last_name'] = df_patient['name'].apply(
        lambda x: x[0]['family'] if isinstance(x, list) and len(x) > 0 else None)

    df_patient['gender'] = df_patient['gender'].fillna('Unknown')
    df_patient['address_line'] = df_patient['address'].apply(lambda x: x[0].get('line', [None])[0] if x else None)
    df_patient['city'] = df_patient['address'].apply(lambda x: x[0].get('city') if x else None)
    df_patient['state'] = df_patient['address'].apply(lambda x: x[0].get('state') if x else None)
    df_patient['country'] = df_patient['address'].apply(lambda x: x[0].get('country') if x else None)

    df_patient_transformed = df_patient[['id', 'first_name', 'last_name', 'gender', 'birthDate', 'race',
                                         'deceasedDateTime', 'medical_record_number', 'ssn',
                                         'address_line', 'city', 'state', 'country']]

    df_patient_transformed = clean_dataframe(df_patient_transformed)

    # 🟢 Transform Condition Data
    df_condition['clinical_status'] = df_condition['clinicalStatus'].apply(
        lambda x: x.get('coding', [{}])[0].get('code') if pd.notnull(x) else None)
    df_condition['verification_status'] = df_condition['verificationStatus'].apply(
        lambda x: x.get('coding', [{}])[0].get('code') if pd.notnull(x) else None)
    df_condition['category_code'] = df_condition['category'].apply(
        lambda x: x[0].get('coding', [{}])[0].get('code') if pd.notnull(x) else None)
    df_condition['category_display'] = df_condition['category'].apply(
        lambda x: x[0].get('coding', [{}])[0].get('display') if pd.notnull(x) else None)
    df_condition['condition_code'] = df_condition['code'].apply(
        lambda x: x.get('coding', [{}])[0].get('code') if pd.notnull(x) else None)
    df_condition['condition_display'] = df_condition['code'].apply(
        lambda x: x.get('coding', [{}])[0].get('display') if pd.notnull(x) else None)

    df_condition['subject_reference'] = df_condition['subject'].apply(
        lambda x: x.get('reference', '').replace('urn:uuid:', '') if pd.notnull(x) else None)
    df_condition['encounter_reference'] = df_condition['encounter'].apply(
        lambda x: x.get('reference', '').replace('urn:uuid:', '') if pd.notnull(x) else None)

    df_condition['onset_date'] = df_condition['onsetDateTime']
    df_condition['recorded_date'] = df_condition['recordedDate']

    df_condition_transformed = df_condition[['id', 'clinical_status', 'verification_status', 'category_code',
                                             'category_display', 'condition_code', 'condition_display',
                                             'subject_reference', 'encounter_reference', 'onset_date', 'recorded_date']]

    df_condition_transformed = clean_dataframe(df_condition_transformed)

    # 🟢 Transform Encounter Data
    df_encounter_transformed = pd.DataFrame({
        "id": df_encounter['id'],
        "status": df_encounter['status'],
        "class_code": df_encounter['class'].apply(lambda x: x.get('code') if pd.notnull(x) else None),
        "type_code": df_encounter['type'].apply(lambda x: x[0]['coding'][0]['code'] if pd.notnull(x) else None),
        "type_display": df_encounter['type'].apply(lambda x: x[0]['coding'][0]['display'] if pd.notnull(x) else None),
        "subject_reference": df_encounter['subject'].apply(
            lambda x: x.get('reference', '').replace('urn:uuid:', '') if pd.notnull(x) else None),
        "location_reference": df_encounter['location'].apply(
            lambda x: x[0]['location']['reference'] if pd.notnull(x) and x else None),
        "location_display": df_encounter['location'].apply(
            lambda x: x[0]['location']['display'] if pd.notnull(x) and x else None),
        "service_provider_reference": df_encounter['serviceProvider'].apply(
            lambda x: x.get('reference') if pd.notnull(x) else None),
        "service_provider_display": df_encounter['serviceProvider'].apply(
            lambda x: x.get('display') if pd.notnull(x) else None),
        "period_start": df_encounter['period'].apply(lambda x: x.get('start') if pd.notnull(x) else None),
        "period_end": df_encounter['period'].apply(lambda x: x.get('end') if pd.notnull(x) else None),
    })

    df_encounter_transformed = clean_dataframe(df_encounter_transformed)

    return df_patient_transformed, df_condition_transformed, df_encounter_transformed
