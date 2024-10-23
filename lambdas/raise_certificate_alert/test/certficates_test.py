"""Tests for the certificates module."""

from datetime import datetime, timedelta
from os import environ
from unittest.mock import MagicMock, patch

import pytest

from ..certificates import (
    check_certificate_expiry,
    get_certificate_expiry,
    get_certificate_from_s3,
    list_certificates,
)
from ..email import (
    CERTIFICATE_EXPIRY_WARNING_MESSAGE,
    CERTIFICATE_EXPIRY_WARNING_SUBJECT,
)
from ..slack import EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME

FILE_PATH = "lambdas.raise_certificate_alert.certificates"


@patch(f"{FILE_PATH}.client")
def test_list_certificates(mock_client: MagicMock) -> None:
    """Test list certificates"""
    # Arrange
    mock_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "certificate1.pem"},
            {"Key": "certificate2.crt"},
            {"Key": "certificate3.pem"},
        ]
    }
    bucket_name = "bucket_name"
    # Act
    result = list_certificates(mock_client, bucket_name)
    # Assert
    mock_client.list_objects_v2.assert_called_once_with(Bucket=bucket_name)

    assert result == ["certificate1.pem", "certificate3.pem"]


@patch(f"{FILE_PATH}.x509")
@patch(f"{FILE_PATH}.datetime")
def test_get_certificate_from_s3(
    mock_datetime: MagicMock, mock_x509: MagicMock
) -> None:
    """Test get certificate from s3"""
    # Arrange
    mock_datetime.now.return_value = "now"
    mock_x509.load_pem_x509_certificate.return_value = "certificate"
    mock_client = MagicMock()
    mock_body = MagicMock()
    mock_client.get_object.return_value = {"Body": mock_body}
    bucket_name = "bucket_name"
    key_name = "key_name"
    # Act
    result = get_certificate_from_s3(mock_client, bucket_name, key_name)
    # Assert
    mock_client.get_object.assert_called_once_with(Bucket=bucket_name, Key=key_name)
    mock_x509.load_pem_x509_certificate.assert_called_once_with(
        mock_body.read.return_value
    )

    assert result == "certificate"


@patch(f"{FILE_PATH}.datetime")
def test_get_certificate_expiry(mock_datetime: MagicMock) -> None:
    """Test get certificate expiry"""
    # Arrange
    mock_datetime.now.return_value = datetime(2022, 1, 1)
    mock_certificate = MagicMock()
    mock_certificate.not_valid_after_utc = datetime(2022, 1, 2)
    # Act
    result = get_certificate_expiry(mock_certificate)
    # Assert
    assert result == timedelta(days=1)


@pytest.mark.parametrize(
    "time_left",
    [
        timedelta(days=7),
        timedelta(days=7, hours=23, minutes=59, seconds=59),
        timedelta(days=14),
        timedelta(days=14, hours=23, minutes=59, seconds=59),
        timedelta(days=30),
        timedelta(days=30, hours=23, minutes=59, seconds=59),
        timedelta(days=60),
        timedelta(days=60, hours=23, minutes=59, seconds=59),
        timedelta(days=90),
        timedelta(days=90, hours=23, minutes=59, seconds=59),
    ],
)
@patch(f"{FILE_PATH}.hydrate_email_alert_and_send")
@patch(f"{FILE_PATH}.hydrate_slack_alert_and_send")
@patch(f"{FILE_PATH}.datetime")
def test_check_certificate_expiry(
    mock_datetime: MagicMock,
    mock_hydrate_slack_alert_and_send: MagicMock,
    mock_hydrate_email_alert_and_send: MagicMock,
    time_left: timedelta,
) -> None:
    """Test check certificate expiry"""
    # Arrange
    cert_file_name = "cert_file_name"
    secret_manager = MagicMock()
    environ["ENVIRONMENT"] = environment = "environment"
    environ["WORKSPACE"] = workspace = "workspace"
    mock_datetime.now.return_value = datetime(2022, 1, 1)
    certificate = MagicMock()
    # Act
    check_certificate_expiry(certificate, cert_file_name, time_left, secret_manager)
    # Assert
    mock_hydrate_slack_alert_and_send.assert_called_once_with(
        EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME,
        {
            "MESSAGE": f"Certificate expiry warning for *{cert_file_name}* - Expiry in {time_left.days} days",
            "ENVIRONMENT": environment,
            "WORKSPACE": workspace,
        },
    )
    mock_hydrate_email_alert_and_send.assert_called_once_with(
        CERTIFICATE_EXPIRY_WARNING_SUBJECT,
        CERTIFICATE_EXPIRY_WARNING_MESSAGE,
        {
            "MESSAGE": f"Certificate expiry warning for {cert_file_name} - Expiry in {time_left.days} days",
            "CERTIFICATE_NAME": cert_file_name,
            "ENVIRONMENT": environment,
            "WORKSPACE": workspace,
            "ISSUER": certificate.issuer.rfc4514_string(),
            "NOT_VALID_AFTER_UTC": str(certificate.not_valid_after_utc),
        },
        secret_manager,
    )
    # Cleanup
    del environ["ENVIRONMENT"]
    del environ["WORKSPACE"]


@pytest.mark.parametrize(
    "time_left",
    [
        timedelta(days=1),
        timedelta(days=6, hours=23, minutes=59, seconds=59),
        timedelta(days=8),
        timedelta(days=13, hours=23, minutes=59, seconds=59),
        timedelta(days=15),
        timedelta(days=21),
        timedelta(days=45),
        timedelta(days=75),
        timedelta(days=120),
    ],
)
@patch(f"{FILE_PATH}.hydrate_email_alert_and_send")
@patch(f"{FILE_PATH}.hydrate_slack_alert_and_send")
@patch(f"{FILE_PATH}.datetime")
def test_check_certificate_expiry_with_no_alert(
    mock_datetime: MagicMock,
    mock_hydrate_slack_alert_and_send: MagicMock,
    mock_hydrate_email_alert_and_send: MagicMock,
    time_left: timedelta,
) -> None:
    """Test check certificate expiry"""
    # Arrange
    cert_file_name = "cert_file_name"
    secret_manager = MagicMock()
    environ["ENVIRONMENT"] = "environment"
    environ["WORKSPACE"] = "workspace"
    certificate = MagicMock()
    mock_datetime.now.return_value = datetime(2022, 1, 1)
    # Act
    check_certificate_expiry(certificate, cert_file_name, time_left, secret_manager)
    # Assert
    mock_hydrate_slack_alert_and_send.assert_not_called()
    mock_hydrate_email_alert_and_send.assert_not_called()
    # Cleanup
    del environ["ENVIRONMENT"]
    del environ["WORKSPACE"]
