"""Collection ofo test to verify the functionality of FHIRValidateQuestionnaire class"""

import json
import os

from lambdas.utils.validation.fhir_validate_questionnaire import (
    FHIRValidateQuestionnaire,
)


def test_validate_questionnaire_when_valid_returns_true():
    """
    Test Function : FHIRValidateQuestionnaire.validate_questionnaire_response
    Scenario: When function is called with *valid* FHIR content
    Expected Result: Then it returns True
    """
    # Arrange
    validator = FHIRValidateQuestionnaire()
    expected = True
    request = read_sample_patient()

    # Act
    actual = validator.validate_questionnaire_response(request)

    # Assert
    assert actual == expected


def test_validate_questionnaire_when_invalid_json_returns_false():
    """
    Test Function : FHIRValidateQuestionnaire.validate_questionnaire_response
    Scenario: When function is called with invalid JSON content
    Expected Result: Then it returns False
    """
    # Arrange
    validator = FHIRValidateQuestionnaire()
    expected = False
    request = read_sample_patient()
    # Append a string to the JSON to make it invalid
    request = request + "{}"

    # Act
    actual = validator.validate_questionnaire_response(request)

    # Assert
    assert actual == expected


def test_validate_questionnaire_when_invalid_fhir_returns_false():
    """
    Test Function : FHIRValidateQuestionnaire.validate_questionnaire_response
    Scenario: When function is called with invalid FHIR content
    Expected Result: Then it returns False
    """
    # Arrange
    validator = FHIRValidateQuestionnaire()
    expected = False
    request = json.loads(read_sample_patient())
    # Append a key to json to invalidate the FHIR record
    request["somerandomkey"] = "somerandomvalue"
    jstr = json.dumps(request)

    # Act
    actual = validator.validate_questionnaire_response(jstr)

    # Assert
    assert actual == expected


def test_validate_questisonnaire_when_invalid_fhir_returns_false():
    """
    Test Function : FHIRValidateQuestionnaire.validate_questionnaire_response
    Scenario: When function is called with invalid FHIR content
    Expected Result: Then it returns False
    """
    # Arrange
    validator = FHIRValidateQuestionnaire()
    expected = False
    data = None

    # Act
    # Added a NOSONAR to prevent linting form highlight None input
    actual = validator.validate_questionnaire_response(data)  # NOSONAR

    # Assert
    assert actual == expected


def read_sample_patient() -> str:
    """Reads a sample data file from file"""
    return load_file(sample_question_response_martha_timmy)


def load_file(file_path: str) -> str:
    """
    reads the contents of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        dict: The contents of the file as a str.
    """
    with open(file_path, "r", encoding="UTF-8") as file:
        return file.read()


sample_question_response_martha_timmy = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../test_data/questionnaire/requests/martha_timmy.json",
)
