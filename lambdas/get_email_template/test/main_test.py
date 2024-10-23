"""
Collection of tests for the get_email_template lambda function
"""

from json import dumps
from os import environ

import pytest
from pytest_mock import MockerFixture

from lambdas.get_email_template.main import GetEmailTemplate, lambda_handler

EXPECTED_EMAIL_CONTENTS = {"body": "test", "subject": "test"}
JSON_EXPECTED_EMAIL_CONTENTS = dumps(EXPECTED_EMAIL_CONTENTS)


def test_lambda_handler(mocker: MockerFixture) -> None:
    # Arrange
    event = {"template_identifier": "adult_to_child"}
    mock_get_email_template = mocker.patch(
        "lambdas.get_email_template.main.GetEmailTemplate.start"
    )
    # Act
    lambda_handler(event, {})
    # Assert
    mock_get_email_template.assert_called_once_with()


def test_get_email_template(mocker: MockerFixture) -> None:
    """
    Test Function : main.start
    Scenario: When start function is called without args
    Expected Result: Then response is set to the file contents
    """
    # Arrange
    environ["EMAIL_TEMPLATE_BUCKET"] = bucket_name = "EMAIL_TEMPLATE_BUCKET"
    mock_get_s3_file = mocker.patch(
        "lambdas.get_email_template.main.get_s3_file",
        return_value=JSON_EXPECTED_EMAIL_CONTENTS,
    )
    get_email_template = GetEmailTemplate(additional_log_config={})
    get_email_template.event = {"template_identifier": "adult_to_child"}
    # Act
    get_email_template.start()
    actual = get_email_template.response
    # Assert
    mock_get_s3_file.assert_called_once_with(
        bucket=bucket_name, file_name="adult_to_child_template.json"
    )
    assert actual == EXPECTED_EMAIL_CONTENTS
    # Cleanup
    del environ["EMAIL_TEMPLATE_BUCKET"]


def test_get_email_template_error(mocker: MockerFixture) -> None:
    """
    Test Function : main.start
    Scenario: When start function is called
    Expected Result: an exception is raised
    """
    # Arrange
    environ["EMAIL_TEMPLATE_BUCKET"] = bucket_name = "EMAIL_TEMPLATE_BUCKET"
    mock_get_s3_file = mocker.patch(
        "lambdas.get_email_template.main.get_s3_file",
        side_effect=Exception("test error"),
    )
    get_email_template = GetEmailTemplate(additional_log_config={})
    get_email_template.event = {"template_identifier": "adult_to_child"}
    # Act
    with pytest.raises(Exception):
        get_email_template.start()
    # Assert
    mock_get_s3_file.assert_called_once_with(
        bucket=bucket_name, file_name="adult_to_child_template.json"
    )
    # Cleanup
    del environ["EMAIL_TEMPLATE_BUCKET"]


def test_get_email_template_invalid_template(mocker: MockerFixture) -> None:
    """
    Test Function : main.start
    Scenario: When start function is called
    Expected Result: an exception is raised
    """
    # Arrange
    get_email_template = GetEmailTemplate(additional_log_config={})
    get_email_template.event = {"template_identifier": "na"}
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid template name"):
        get_email_template.start()
