""" Unit tests for the 'FHIRObjectMapper' module """

import json
import os
from datetime import datetime, timezone

import pytest
from fhirclient.models.identifier import Identifier
from fhirclient.models.patient import Patient
from fhirclient.models.relatedperson import RelatedPerson

import lambdas.utils.pds.errors as err
from lambdas.utils.pds.fhirobjectmapper import FHIRObjectMapper


def test_filter_patient_properties_when_none_returns_none():
    """Test to confirm when a None is input, then the output is also None"""
    sut = FHIRObjectMapper()
    patient = None
    expected = None
    actual = sut.filter_patient_properties(patient)

    assert actual == expected


def test_filter_patient_properties_ensure_id_is_returned():
    """Test to confirm id is correctly output"""
    sut = FHIRObjectMapper()
    param = read_sample_patient()
    expected = map_sample_patient()
    actual = sut.filter_patient_properties(param)

    assert expected.id == actual.id


def test_filter_patient_properties_ensure_identifier_is_returned():
    """Test to confirm identifier is correctly output"""
    sut = FHIRObjectMapper()
    param = read_sample_patient()
    expected = map_sample_patient()
    actual = sut.filter_patient_properties(param)

    assert len(expected.identifier) == 1
    assert expected.identifier[0].value == actual.identifier[0].value


def test_filter_patient_properties_ensure_birthdate_is_returned():
    """Test to confirm birthdate is correctly output"""
    sut = FHIRObjectMapper()
    param = read_sample_patient()
    expected = map_sample_patient()
    actual = sut.filter_patient_properties(param)

    assert expected.birthDate.origval == actual.birthDate.origval


def test_filter_patient_properties_ensure_name_is_returned():
    """Test to confirm name is correctly output"""
    sut = FHIRObjectMapper()
    param = read_sample_patient()
    expected = extract_name(map_sample_patient())
    actual = extract_name(sut.filter_patient_properties(param))

    assert expected == actual


def test_filter_related_person_properties_ensure_name_is_returned():
    """Test to confirm id is correctly output"""
    sut = FHIRObjectMapper()
    param = read_sample_patient()
    expected = map_sample_patient()
    actual = sut.filter_patient_properties(param)

    assert expected.id == actual.id


def test_filter_patient_properties_ensure_resource_type_is_returned():
    """Test to confirm resource type is correctly output"""
    sut = FHIRObjectMapper()
    param = read_sample_patient()
    expected = map_sample_patient()
    actual = sut.filter_patient_properties(param)

    assert expected.resource_type == actual.resource_type


def test_filter_related_person_properties_patient_identifier_matches():
    """
    Test Function : FHIRObjectMapper.filter_related_person_properties
    Scenario: When patient is supplied
    Expected Result: related person patient identifier matches patient identifier
    """
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    persons = read_sample_two_related_person()

    for expected in persons:
        actual = sut.filter_related_person_properties(patient, expected)

        # Patient's NHS No should be applied to actual
        assert patient.identifier[0].value == actual.patient.identifier.value


def test_filter_related_person_properties_ensure_id_is_returned():
    """Test to confirm id is correctly output"""
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    persons = read_sample_two_related_person()

    for expected in persons:
        actual = sut.filter_related_person_properties(patient, expected)
        assert expected.id == actual.id


def test_filter_related_person_properties_ensure_identifier_is_returned():
    """Test to confirm identifier is correctly output"""
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    persons = read_sample_two_related_person()

    for expected in persons:
        actual = sut.filter_related_person_properties(patient, expected)
        assert expected.identifier == actual.identifier


def test_filter_related_person_properties_ensure_patient_is_returned():
    """Test to confirm patient information from a related person is correctly output"""
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    persons = read_sample_two_related_person()

    for expected in persons:
        actual = sut.filter_related_person_properties(patient, expected)
        assert expected.patient.as_json() == actual.patient.as_json()


def test_when_MTH_relationship_then_system_v3_is_applied():
    """
    Scenario: There is one MTH relationship
    When: Filter_related_person_properties is run
    Then: The system property is updated to be correct
    """
    # Arrange
    expected = FHIRObjectMapper.SYSTEM_V3_ROLE_CODE

    # Act
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    person = read_sample_two_related_person()[0]
    # Force MTH relationship with a fake system
    person.relationship[0].coding[0].code = "MTH"
    person.relationship[0].coding[0].system = "some_fake_other_system"

    # Assert
    actual = sut.filter_related_person_properties(patient, person)
    # Confirm system was updated
    assert actual.relationship[0].coding[0].system == expected


def test_filter_related_person_properties_ensure_relationship_is_returned():
    """Test to confirm relationship information is correctly output"""
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    persons = read_sample_two_related_person()

    for expected in persons:
        actual = sut.filter_related_person_properties(patient, expected)
        assert expected.relationship == actual.relationship


def test_filter_related_person_properties_remove_non_mth_relationship():
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    persons = read_test_mother_and_personal_relationship()
    relationship_list = persons[0].relationship[0].coding

    for expected in persons:
        actual = sut.filter_related_person_properties(patient, expected)
        assert len(actual.relationship[0].coding) == 1
        assert len(relationship_list) == 2
        assert actual.relationship[0].coding[0].code == "MTH"


def test_create_related_person_bundle_ensure_bundle_is_returned():
    """Test to confirm bundle is generated correctly"""
    expected_timestamp = datetime.now(timezone.utc)
    sut = FHIRObjectMapper()
    patient = read_sample_patient()
    persons = read_sample_two_related_person()
    include = True
    data = [(patient, persons[0], include), (patient, persons[1], include)]
    original_url = "test-url"
    proxy_identifier = Identifier({"value": "test-id", "system": "test-system"})

    actual = sut.create_related_person_bundle(data, original_url, proxy_identifier)

    assert actual.timestamp.date >= expected_timestamp
    assert actual.type == "searchset"
    assert actual.link[0].url == original_url
    assert actual.total == 4
    assert (
        actual.entry[0].fullUrl == "/validated-relationships/FHIR/R4/Patient/9000000009"
    )
    assert len(actual.entry) == 4
    assert (
        actual.entry[1].resource.identifier[0].as_json() == proxy_identifier.as_json()
    )


def test_create_operation_outcome_ensure_outcome_is_returned():
    """
    Scenario: Test is operation outcome function returns expected FHIR data
    When: Internal server error outcome is supplied
    Then: Operational outcome result containing internal server error is returned
    """

    # Arrange
    expected_json = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "invalid",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                            "version": "1",
                            "code": "SERVER_ERROR",
                            "display": "Failed to generate response",
                        }
                    ]
                },
                "diagnostics": "Internal Server Error - Failed to generate response",
            }
        ],
    }
    sut = FHIRObjectMapper()
    data = err.INTERNAL_SERVER_ERROR

    # Act
    actual = sut.create_operation_outcome(data)

    # Assert
    actual_json = actual.as_json()
    assert actual_json == expected_json


@pytest.mark.parametrize(
    "original_url, expected_url",
    [
        (
            "https://api.service.nhs.uk/validated-relationships/FHIR/R4/RelatedPerson?&identifier=5993544619",
            "https://api.service.nhs.uk",
        ),
        (
            "https://www.nhs.uk/nhs-services/gps/",
            "https://www.nhs.uk",
        ),
        ("no-url-test", ""),
    ],
)
def test_extract_base_url(original_url, expected_url):
    """Test extract_base_url method of FHIRObjectMapper"""
    sut = FHIRObjectMapper()
    actual = sut.extract_base_url(original_url)

    assert actual == expected_url


@pytest.mark.parametrize(
    "pds_proxy_identifier",
    [
        {"value": "test-id", "system": "test-system"},
        {
            "extension": [
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "code": "01",
                                "display": "Number present and verified",
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatus",
                                "version": "1.0.0",
                            }
                        ]
                    },
                }
            ],
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": "9730675929",
        },
    ],
)
def test_create_proxy_identifier(pds_proxy_identifier: dict) -> None:
    # Arrange
    sut = FHIRObjectMapper()
    proxy_identifier = Identifier(
        {
            "value": pds_proxy_identifier.get("system"),
            "system": pds_proxy_identifier.get("system"),
        }
    )
    # Act
    response = sut.create_proxy_identifier(proxy_identifier)
    # Assert
    assert response.as_json() == proxy_identifier.as_json()


def extract_name(patient: Patient) -> list[str]:
    """Extracts the name from a patient FHIR object"""
    rtn = [str]
    for name in patient.name:
        prefix = " ".join(name.prefix)
        given = " ".join(name.given)
        suffix = " ".join(name.suffix)
        fullname = " ".join([prefix, given, name.family, suffix])
        rtn.append(fullname)

    return rtn


def map_sample_patient() -> Patient:
    """Maps a patient record from sample data"""
    full_patient = read_sample_patient()
    rtn = Patient()
    rtn.id = full_patient.id
    rtn.identifier = full_patient.identifier
    rtn.birthDate = full_patient.birthDate
    rtn.name = full_patient.name
    rtn.resource_type = full_patient.resource_type
    return rtn


def read_sample_patient() -> Patient:
    """Reads a sample data file from file"""
    contents = load_json(mock_proxy_file_sandpit_patient)
    patient = Patient(contents)
    return patient


def read_sample_two_related_person() -> list[RelatedPerson]:
    """Reads two related person files"""
    contents = load_json(mock_proxy_file_sandpit_two_related_person)
    rtn = []
    for entry in contents:
        rtn.append(RelatedPerson(entry))

    return rtn


def read_test_mother_and_personal_relationship() -> list[RelatedPerson]:
    """Reads mother and personal relationship file"""
    contents = load_json(mock_proxy_file_mother_and_personal)
    rtn = []
    for entry in contents:
        rtn.append(RelatedPerson(entry))

    return rtn


def load_json(file_path: str) -> dict:
    """
    reads the contents of a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The json contents of the file as a Python dictionary.
    """
    with open(file_path, "r", encoding="UTF-8") as file:
        return json.load(file)


mock_proxy_file_sandpit_patient = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../sample_data/patient_details/sample_sandpit_patient.json",
)

mock_proxy_file_sandpit_two_related_person = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../sample_data/related_person/sample_sandpit_two_related_person.json",
)

mock_proxy_file_mother_and_personal = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../sample_data/related_person/proxy_test_mother_and_personal.json",
)
