import pytest
import pandas as pd
from scripts.transform import transform_data, clean_dataframe


#  Sample Data Fixtures
@pytest.fixture
def sample_patient_data():
    return pd.DataFrame([
        {
            "id": "123",
            "name": [{"given": ["John"], "family": "Doe"}],
            "gender": "male",
            "birthDate": "1980-01-01",
            "extension": [{"url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                           "extension": [{"valueCoding": {"display": "White"}}]}],
            "identifier": [
                {"type": {"coding": [{"code": "MR"}]}, "value": "MR123"},
                {"type": {"coding": [{"code": "SS"}]}, "value": "123-45-6789"}
            ],
            "address": [{"line": ["123 Main St"], "city": "New York", "state": "NY", "country": "USA"}],
            "deceasedDateTime": None
        }
    ])


@pytest.fixture
def sample_condition_data():
    return pd.DataFrame([
        {
            "id": "COND001",
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "verificationStatus": {"coding": [{"code": "confirmed"}]},
            "category": [{"coding": [{"code": "problem-list-item", "display": "Problem List Item"}]}],
            "code": {"coding": [{"code": "C001", "display": "Hypertension"}]},
            "subject": {"reference": "urn:uuid:123"},
            "encounter": {"reference": "urn:uuid:ENC001"},
            "onsetDateTime": "2022-05-10",
            "recordedDate": "2022-05-15"
        }
    ])


@pytest.fixture
def sample_encounter_data():
    return pd.DataFrame([
        {
            "id": "ENC001",
            "status": "finished",
            "class": {"code": "outpatient"},
            "type": [{"coding": [{"code": "AMB", "display": "Ambulatory"}]}],
            "subject": {"reference": "urn:uuid:123"},
            "location": [{"location": {"reference": "Location/LOC001", "display": "General Hospital"}}],
            "serviceProvider": {"reference": "Organization/ORG001", "display": "Health System"},
            "period": {"start": "2023-01-01T10:00:00", "end": "2023-01-01T11:00:00"}
        }
    ])


# 📌 Unit Test: Data Cleaning
def test_clean_dataframe():
    df = pd.DataFrame({"col1": [" value1 ", "value,2"], "col2": [None, "value3"]})
    cleaned_df = clean_dataframe(df)

    assert cleaned_df.iloc[0]["col1"] == "value1"
    assert cleaned_df.iloc[1]["col1"] == "value 2"
    assert cleaned_df.iloc[0]["col2"] == "Unknown"


# 📌 Unit Test: Transform Data
def test_transform_data(sample_patient_data, sample_condition_data, sample_encounter_data):
    df_patient_transformed, df_condition_transformed, df_encounter_transformed = transform_data(
        sample_patient_data, sample_condition_data, sample_encounter_data)

    # ✅ Patient Data Tests
    assert df_patient_transformed.shape[0] == 1  # Only 1 patient
    assert df_patient_transformed.iloc[0]["first_name"] == "John"
    assert df_patient_transformed.iloc[0]["last_name"] == "Doe"
    assert df_patient_transformed.iloc[0]["race"] == "White"
    assert df_patient_transformed.iloc[0]["medical_record_number"] == "MR123"
    assert df_patient_transformed.iloc[0]["ssn"] == "123-45-6789"
    assert df_patient_transformed.iloc[0]["city"] == "New York"
    assert df_patient_transformed.iloc[0]["state"] == "NY"

    # ✅ Condition Data Tests
    assert df_condition_transformed.shape[0] == 1  # Only 1 condition
    assert df_condition_transformed.iloc[0]["clinical_status"] == "active"
    assert df_condition_transformed.iloc[0]["verification_status"] == "confirmed"
    assert df_condition_transformed.iloc[0]["condition_code"] == "C001"
    assert df_condition_transformed.iloc[0]["condition_display"] == "Hypertension"
    assert df_condition_transformed.iloc[0]["subject_reference"] == "123"
    assert df_condition_transformed.iloc[0]["encounter_reference"] == "ENC001"

    # ✅ Encounter Data Tests
    assert df_encounter_transformed.shape[0] == 1  # Only 1 encounter
    assert df_encounter_transformed.iloc[0]["status"] == "finished"
    assert df_encounter_transformed.iloc[0]["class_code"] == "outpatient"
    assert df_encounter_transformed.iloc[0]["type_code"] == "AMB"
    assert df_encounter_transformed.iloc[0]["type_display"] == "Ambulatory"
    assert df_encounter_transformed.iloc[0]["subject_reference"] == "123"
    assert df_encounter_transformed.iloc[0]["location_reference"] == "Location/LOC001"
    assert df_encounter_transformed.iloc[0]["location_display"] == "General Hospital"
    assert df_encounter_transformed.iloc[0]["service_provider_reference"] == "Organization/ORG001"
    assert df_encounter_transformed.iloc[0]["service_provider_display"] == "Health System"
    assert df_encounter_transformed.iloc[0]["period_start"] == "2023-01-01T10:00:00"
    assert df_encounter_transformed.iloc[0]["period_end"] == "2023-01-01T11:00:00"
