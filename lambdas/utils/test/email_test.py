"""Unit tests for the email module."""

from json import dumps
from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from ..email import send_email


@patch("lambdas.utils.email.post")
def test_send_email(mock_post: MagicMock) -> None:
    """Test the send_email function."""
    # Arrange
    email = "test@example.com"
    subject = "Test email"
    body = "This is a test email"
    api_url = "https://example.com"
    subscription_key = "1234567890"
    mock_post.return_value = MagicMock(return_value=Response())
    mock_post.return_value.status_code = status_code = 200
    # Act
    response = send_email(email, subject, body, api_url, subscription_key)
    # Assert
    assert response.status_code == status_code
    mock_post.assert_called_once_with(
        url=api_url,
        headers={"Subscription-Key": subscription_key},
        data=dumps(
            {
                "ToEmail": email,
                "subject": subject,
                "body": body,
            }
        ),
        timeout=10,
    )


@pytest.mark.parametrize("status_code", [400, 500])
@patch("lambdas.utils.email.post")
def test_send_email_failure(mock_post: MagicMock, status_code: int) -> None:
    """Test the send_email function."""
    # Arrange
    email = "test@example.com"
    subject = "Test email"
    body = "This is a test email"
    api_url = "https://example.com"
    subscription_key = "1234567890"
    mock_post.return_value = MagicMock(return_value=Response())
    mock_post.return_value.status_code = status_code
    # Act & Assert
    with pytest.raises(
        ValueError, match="Email failed to be added to NHS Send Mail queue."
    ):
        send_email(email, subject, body, api_url, subscription_key)
    mock_post.assert_called_once_with(
        url=api_url,
        headers={"Subscription-Key": subscription_key},
        data=dumps(
            {
                "ToEmail": email,
                "subject": subject,
                "body": body,
            }
        ),
        timeout=10,
    )
