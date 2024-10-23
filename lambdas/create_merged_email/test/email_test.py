from json import dumps

from ..email import Email


def test_email() -> None:
    """Test the Email class."""
    # Arrange
    body = "Test email body"
    subject = "Test email subject"
    # Act
    email = Email(
        email_body=body,
        email_subject=subject,
    )
    # Assert
    assert email.email_subject == subject
    assert email.email_body == body


def test_email_to_json() -> None:
    """Test the Email class to_json method."""
    # Act
    email = Email(
        email_body="Test email body",
        email_subject="Test email subject",
    )
    # Assert
    assert (
        email.to_json()
        == '{"email_subject": "Test email subject", "email_body": "Test email body"}'
    )


def test_email_replace_with_variables() -> None:
    """Test the Email class replace_with_variables method."""
    # Arrange
    body = "Test email body {{email_value_1}}"
    subject = "Test email subject {{email_value_2}}"
    email = Email(
        email_body=body,
        email_subject=subject,
    )
    # Act
    email.replace_with_variables(
        {
            "email_value_1": "Replaced in email body",
            "email_value_2": "Replaced in email subject",
        }
    )
    # Assert
    assert email.email_body == "Test email body Replaced in email body"
    assert email.email_subject == "Test email subject Replaced in email subject"
