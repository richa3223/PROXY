"""Tests for the main module."""

from os import environ
from unittest.mock import MagicMock, patch

from pytest_mock import MockerFixture

from ..main import RaiseCertificateAlert, lambda_handler
from ..slack import UNABLE_TO_PROCESS_CERTIFICATE_SLACK_ALERT_TEMPLATE_NAME

FILE_PATH = "lambdas.raise_certificate_alert.main"


@patch(f"{FILE_PATH}.check_certificate_expiry")
@patch(f"{FILE_PATH}.get_certificate_expiry")
@patch(f"{FILE_PATH}.get_certificate_from_s3")
@patch(f"{FILE_PATH}.list_certificates")
@patch(f"{FILE_PATH}.client")
@patch(f"{FILE_PATH}.hydrate_slack_alert_and_send")
def test_raise_certificate_alert__main(
    mock_hydrate_slack_alert_and_send: MagicMock,
    mock_s3_client: MagicMock,
    mock_list_certificates: MagicMock,
    mock_get_certificate_from_s3: MagicMock,
    mock_get_certificate_expiry: MagicMock,
    mock_check_certificate_expiry: MagicMock,
):
    """Test the raise_certificate_alert function."""
    # Arrange
    mock_list_certificates.return_value = ["certificate_name"]
    mock_get_certificate_from_s3.return_value = "certificate"
    mock_get_certificate_expiry.return_value = "expiry"
    environ["MTLS_CERTIFICATE_BUCKET_NAME"] = bucket_name = "bucket_name"
    # Act
    raise_certificate_alert = RaiseCertificateAlert()
    raise_certificate_alert.main({}, {})
    # Assert
    assert raise_certificate_alert.response == {
        "message": "Raise certificate alert lambda complete"
    }
    mock_list_certificates.assert_called_once_with(
        mock_s3_client.return_value, bucket_name
    )
    mock_get_certificate_from_s3.assert_called_once_with(
        mock_s3_client.return_value, bucket_name, "certificate_name"
    )
    mock_get_certificate_expiry.assert_called_once_with("certificate")
    mock_check_certificate_expiry.assert_called_once_with(
        "certificate",
        "certificate_name",
        "expiry",
        raise_certificate_alert.secret_manager,
    )
    mock_hydrate_slack_alert_and_send.assert_not_called()
    # Clean up
    del environ["MTLS_CERTIFICATE_BUCKET_NAME"]


@patch(f"{FILE_PATH}.get_certificate_from_s3")
@patch(f"{FILE_PATH}.list_certificates")
@patch(f"{FILE_PATH}.client")
@patch(f"{FILE_PATH}.hydrate_slack_alert_and_send")
def test_raise_certificate_alert__main__slack_alert(
    mock_hydrate_slack_alert_and_send: MagicMock,
    mock_s3_client: MagicMock,
    mock_list_certificates: MagicMock,
    mock_get_certificate_from_s3: MagicMock,
):
    """Test the raise_certificate_alert function."""
    # Arrange
    mock_list_certificates.return_value = ["certificate_name"]
    mock_get_certificate_from_s3.side_effect = Exception("error")
    environ["MTLS_CERTIFICATE_BUCKET_NAME"] = bucket_name = "bucket_name"
    # Act
    raise_certificate_alert = RaiseCertificateAlert()
    raise_certificate_alert.main({}, {})
    # Assert
    mock_list_certificates.assert_called_once_with(
        mock_s3_client.return_value, bucket_name
    )
    mock_get_certificate_from_s3.assert_called_once_with(
        mock_s3_client.return_value, bucket_name, "certificate_name"
    )
    mock_hydrate_slack_alert_and_send.assert_called_once_with(
        UNABLE_TO_PROCESS_CERTIFICATE_SLACK_ALERT_TEMPLATE_NAME,
        {
            "CERTIFICATE_NAME": "certificate_name",
        },
    )
    # Clean up
    del environ["MTLS_CERTIFICATE_BUCKET_NAME"]


def test_lambda_handler(mocker: MockerFixture):
    """Test the lambda handler."""
    # Arrange
    mock_raise_certificate_alert = mocker.patch(
        f"{FILE_PATH}.RaiseCertificateAlert.main"
    )
    # Act
    lambda_handler(None, None)
    # Assert
    mock_raise_certificate_alert.assert_called_once()
