""" Unit tests for the PDS Utility Functions """

import json
import os
from datetime import datetime, timezone

import pytest
from dateutil.relativedelta import relativedelta
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.patient import Patient
from fhirclient.models.period import Period
from fhirclient.models.relatedperson import RelatedPerson

from lambdas.utils.pds.pdsdata import (
    get_is_person_deceased,
    get_patient_age,
    get_relationship,
    get_security_code,
)


@pytest.fixture(name="related_person")
def related_person_one_record():
    """Returns a fake outcome result"""
    data = load_mock_record(mock_related_person_file)[0]
    return RelatedPerson(data)


# Tests cases for get_patient_age()
def test_get_patient_age_when_dob_is_missing_then_none_type_returned():
    """Test to determine NoneType is returned for missing value"""
    expected = None
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = None

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_invalid_then_none_type_returned():
    """Test to determine NoneType is returned for invalid value"""
    expected = None
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = "foo"

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_20_century_then_age_from_2001_returned():
    """Test to determine dob when born 2001-01-01"""
    dob = datetime(2001, 1, 1, tzinfo=timezone.utc)
    today = datetime.now(timezone.utc)
    expected = relativedelta(dt1=today, dt2=dob).years
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = FHIRDate("20")

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_2010_then_age_from_jan_2010_returned():
    """Test to determine dob when born 2010-01-01"""
    dob = datetime(2010, 1, 1, tzinfo=timezone.utc)
    today = datetime.now(timezone.utc)
    expected = relativedelta(dt1=today, dt2=dob).years
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = FHIRDate(dob.strftime("%Y"))

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_oct_2010_then_age_from_01_oct_2010_returned():
    """Test to determine dob when born 2010-10-01"""
    dob = datetime(2010, 10, 1, tzinfo=timezone.utc)
    today = datetime.now(timezone.utc)
    expected = relativedelta(dt1=today, dt2=dob).years
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = FHIRDate(dob.strftime("%Y-%m"))

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_from_file_then_correct_value_returned():
    """Test to determine when file dob is input expected age is returned"""
    # 2010-10-22 from patient file
    dob = datetime(2010, 10, 22, tzinfo=timezone.utc)
    today = datetime.now(timezone.utc)
    expected = relativedelta(dt1=today, dt2=dob).years
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_13_years_1_days_ago_then_age_as_13_returned():
    """Test to determine dob when born 13 year and 1 days ago"""

    expected = 13
    dob = datetime.now(timezone.utc) - relativedelta(years=13, days=1)
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = FHIRDate(dob.strftime("%Y-%m-%d"))

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_13_years_0_days_ago_then_age_as_13_returned():
    """Test to determine dob when born 13 year and 0 days ago"""

    expected = 13
    dob = datetime.now(timezone.utc) - relativedelta(years=13, days=0)
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = FHIRDate(dob.strftime("%Y-%m-%d"))

    actual = get_patient_age(patient)

    assert actual == expected


def test_get_patient_age_when_dob_is_12_years_364_days_ago_then_age_as_12_returned():
    """Test to determine dob when born 13 years and 364 days ago"""

    expected = 12
    dob = datetime.now(timezone.utc) - relativedelta(years=12, days=364)
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.birthDate = FHIRDate(dob.strftime("%Y-%m-%d"))

    actual = get_patient_age(patient)

    assert actual == expected


# Tests for get_is_person_deceased()
def test_get_is_person_deceased_when_bool_not_deceased_then_returns_false():
    """Test to determine if deceased is set, then function returns true"""
    expected = False
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.deceasedBoolean = False

    actual = get_is_person_deceased(patient)

    assert actual == expected


def test_get_is_person_deceased_when_bool_deceased_then_returns_true():
    """Test to determine if deceased is set, then function returns true"""
    expected = True
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.deceasedBoolean = True

    actual = get_is_person_deceased(patient)

    assert actual == expected


def test_get_is_person_deceased_when_not_deceased_then_returns_false():
    """Test to determine if deceased is set, then function returns true"""
    expected = False
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.deceasedDateTime = None

    actual = get_is_person_deceased(patient)

    assert actual == expected


def test_get_is_person_deceased_when_no_datevalue_set_then_returns_false():
    """Test to determine if deceased is set, then function returns true"""
    expected = False
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.deceasedDateTime = FHIRDate()

    actual = get_is_person_deceased(patient)

    assert actual == expected


def test_get_is_person_deceased_when_deceased_then_returns_true():
    """Test to determine when deceased date is set, then function returns true"""
    expected = True
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.deceasedDateTime = FHIRDate("2020-01-01")

    actual = get_is_person_deceased(patient)

    assert actual == expected


# Tests for get_security_code()
def test_get_security_code_when_meta_not_present_returns_none():
    """Test to determine if there is no security code, then none is returned"""
    expected = None
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.meta = None

    actual = get_security_code(patient)

    assert actual == expected


def test_get_security_code_when_security_not_present_returns_none():
    """Test to determine if there is no security code, then none is returned"""
    expected = None
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.meta.security = None

    actual = get_security_code(patient)

    assert actual == expected


def test_get_security_code_when_restricted_returns_s():
    """Test to determine if there is no security code, then none is returned"""
    expected = "S"
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)
    patient.meta.security[0].code = "S"

    actual = get_security_code(patient)

    assert actual == expected


def test_get_security_code_when_unrestricted_returns_u():
    """Test to determine if there is no security code, then none is returned"""
    expected = "U"
    data = load_mock_record(mock_proxy_file_sandpit_patient)
    patient = Patient(data)

    actual = get_security_code(patient)

    assert actual == expected


# get_relationship tests
def test_get_relationship_when_none_returns_empty():
    """Test to confirm relationship is extracted"""

    # Arrange
    data = None
    related = RelatedPerson(data)
    expected = []

    # Act
    actual = get_relationship(related)

    # Assert
    assert actual == expected


def test_get_relationship_when_inactive_returns_empty(related_person: RelatedPerson):
    """
    Test Function : pdsdata.get_relationship
    Scenario: When 'active' property is None
    Expected Result: returns an empty result
    """

    # Arrange
    related_person.active = False
    expected = []

    # Act
    actual = get_relationship(related_person)

    # Assert
    assert actual == expected


@pytest.mark.parametrize(
    "period",
    [
        Period({"start": "null", "end": "null"}),
        Period({"start": "", "end": ""}),
        Period({"start": "2100-01-01", "end": "2110-01-01"}),
        Period({"start": "2000-01-01", "end": "2020-01-01"}),
    ],
)
def test_get_relationship_when_activeperiod_returns_expected(
    related_person: RelatedPerson, period: Period
):
    """
    Test Function : pdsdata.get_relationship
    Scenario: When 'period' property is specified value
    Expected Result: expected result is returned
    """

    # Arrange
    related_person.period = period
    expected = []

    # Act
    actual = get_relationship(related_person)

    # Assert
    assert actual == expected


def test_get_relationship_when_none_period_returns_relationship(
    related_person: RelatedPerson,
):
    """
    Test Function : pdsdata.get_relationship
    Scenario: When 'period' property is None
    Expected Result: Relationship ["Guardian"] value is returned
    """

    # Arrange
    related_person.period = None
    expected = ["Guardian"]

    # Act
    actual = get_relationship(related_person)

    # Assert
    assert actual == expected


def test_get_relationship_when_present_returns_guardian_expected(
    related_person: RelatedPerson,
):
    """
    Test Function : pdsdata.get_relationship
    Scenario: When all checks pass
    Expected Result: ["Guardian"] is returned
    """

    # Arrange
    related_person.period.end = None
    expected = ["Guardian"]

    # Act
    actual = get_relationship(related_person)

    # Assert
    assert actual == expected


def test_get_relationship_when_two_relationships_returns_both():
    """
    Test Function : pdsdata.get_relationship
    Scenario: When source has two active relationships
    Expected Result: both are returned
    """
    # Arrange
    data = load_mock_record(mock_two_relationships_file)
    related = RelatedPerson(data)
    related.period.end = None
    expected = ["Guardian", "Sister"]

    # Act
    actual = get_relationship(related)

    # Assert
    assert actual == expected


# get_relationship - error cases
@pytest.mark.parametrize("relation", [None, [], [CodeableConcept()]])
def test_get_relationship_when_relationship_empty_returns_empty(
    relation, related_person: RelatedPerson
):
    """
    Test Function : pdsdata.get_relationship
    Scenario: When there are no relationships
    Expected Result: returns empty result
    """

    # Arrange
    related_person.relationship = relation
    expected = []

    # Act
    actual = get_relationship(related_person)

    # Assert
    assert actual == expected


@pytest.mark.parametrize("coding", [None, [], [Coding()]])
def test_get_relationship_when_coding_empty_returns_empty(
    coding, related_person: RelatedPerson
):
    """
    Test Function : pdsdata.get_relationship
    Scenario: When relationship collection data is specified
    Expected Result: returns empty result
    """
    # Arrange
    rel = [related_person.relationship[0]]
    rel[0].coding = coding
    related_person.relationship = rel
    expected = []

    # Act
    actual = get_relationship(related_person)

    # Assert
    assert actual == expected


def load_mock_record(file_path):
    """
    Load a mock record from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the mock record.

    Returns:
        dict: The loaded mock record as a Python dictionary.
    """
    with open(file_path, "r", encoding="UTF-8") as file:
        return json.load(file)


mock_proxy_file_sandpit_patient = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../sample_data/patient_details/sample_sandpit_patient.json",
)

mock_related_person_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../sample_data/related_person/sample_sandpit_two_related_person.json",
)

mock_two_relationships_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../sample_data/related_person/related_person_two_relationships.json",
)
