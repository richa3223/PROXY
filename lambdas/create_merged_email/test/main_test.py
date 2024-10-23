from json import load
from os import environ, path
from unittest.mock import MagicMock, patch

import pytest

from lambdas.create_merged_email.main import CreateMergedEmail

FILE_PATH = "lambdas.create_merged_email.main"
EXPECTED_REFERENCE_CODE = "18704o5en9"


@pytest.fixture(name="event")
def create_event() -> dict:
    """Returns a valid event data"""
    file_path = path.dirname(path.realpath(__file__)) + "/test_data.json"
    with open(file_path) as file:
        return load(file)


@patch(f"{FILE_PATH}.uuid4")
@patch(f"{FILE_PATH}.put_s3_file")
def test_create_merged_email_start(
    mock_put_s3_file: MagicMock, mock_uuid4: MagicMock, event: dict
) -> None:
    # Arrange
    sut = CreateMergedEmail()
    sut.event = event
    mock_uuid4.return_value = test_uuid = "afdb4304-7959-4947-b491-1b9305467ed1"
    environ["HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET"] = bucket_name = "test-bucket"
    # Act
    sut.start()
    # Assert
    file_name = f"{EXPECTED_REFERENCE_CODE}-{test_uuid}.json"
    assert sut.response == {"file_name": file_name}
    mock_put_s3_file.assert_called_once_with(
        bucket_name,
        file_name,
        '{"email_subject": "Validate Relationship Service", "email_body": "<!doctype html><html><head> <title>Validated Relationship Service</title> <meta name=\\"description\\" content=\\"VRS Email Template\\"></head><body> The reference code 18704o5en9 and odscode is A20047</body></html>"}',
    )
    # Cleanup
    del environ["HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET"]


@patch(f"{FILE_PATH}.uuid4")
@patch(f"{FILE_PATH}.put_s3_file")
def test_create_merged_email_start__with_exception(
    mock_put_s3_file: MagicMock, mock_uuid4: MagicMock, event: dict
) -> None:
    # Arrange
    sut = CreateMergedEmail()
    sut.event = event
    mock_uuid4.return_value = test_uuid = "afdb4304-7959-4947-b491-1b9305467ed1"
    environ["HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET"] = bucket_name = "test-bucket"
    error_msg = "Test Test Test"
    mock_put_s3_file.side_effect = ValueError(error_msg)
    # Act
    with pytest.raises(ValueError, match=error_msg):
        sut.start()
    # Assert
    file_name = f"{EXPECTED_REFERENCE_CODE}-{test_uuid}.json"
    mock_put_s3_file.assert_called_once_with(
        bucket_name,
        file_name,
        '{"email_subject": "Validate Relationship Service", "email_body": "<!doctype html><html><head> <title>Validated Relationship Service</title> <meta name=\\"description\\" content=\\"VRS Email Template\\"></head><body> The reference code 18704o5en9 and odscode is A20047</body></html>"}',
    )
    # Cleanup
    del environ["HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET"]


def test_create_merged_email__get_ods_code(event: dict) -> None:
    # Arrange
    sut = CreateMergedEmail()
    # Act
    ods_code = sut._CreateMergedEmail__get_ods_code(
        event.get("PatientPDSPatientRecord")
    )
    # Assert
    assert ods_code == "A20047"


def test_create_merged_email__get_ods_code__with_exception(event: dict) -> None:
    # Arrange
    sut = CreateMergedEmail()
    # Act
    ods_code = sut._CreateMergedEmail__get_ods_code({})
    # Assert
    assert ods_code == "Unknown"
