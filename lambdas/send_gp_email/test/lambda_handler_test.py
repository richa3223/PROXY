from json import dumps
from os import environ
from unittest.mock import MagicMock, patch

from lambdas.send_gp_email.main import SendGPEmail, lambda_handler

FILE_PATH = "lambdas.send_gp_email.main"

DYNAMO_DB_MOCK_EVENT = {
    # Omitting fields not relevant for testing
    "detail": {
        "eventId": "4406b6ae9ac307d4967cec0522adf021",
        "eventType": "GP_AUTHORISATION_REQUEST_CREATED",
        "referenceCode": "y1pr38jpv",
    }
}


@patch(f"{FILE_PATH}.send_gp_email._SendGPEmail__get_item")
@patch(f"{FILE_PATH}.send_gp_email._SendGPEmail__load_email_content")
@patch(f"{FILE_PATH}.send_gp_email.send_gp_email")
@patch(f"{FILE_PATH}.send_gp_email._SendGPEmail__update_status")
def test_lambda_handler_email_missing(
    mock_update_status: MagicMock,
    mock_send_gp_email: MagicMock,
    mock_load_email_content: MagicMock,
    mock_get_item: MagicMock,
):
    # Arrange
    mock_get_item.__get_item.return_value = {}
    # Act
    response = lambda_handler(DYNAMO_DB_MOCK_EVENT.copy(), {})
    # Assert
    mock_get_item.assert_called_once()

    mock_load_email_content.assert_not_called()
    mock_send_gp_email.assert_not_called()
    mock_update_status.assert_not_called()

    assert response == {
        "statusCode": 400,
        "body": {"message": "Email address is not valid"},
    }


@patch(f"{FILE_PATH}.send_gp_email._SendGPEmail__get_item")
@patch(f"{FILE_PATH}.send_gp_email._SendGPEmail__load_email_content")
@patch(f"{FILE_PATH}.send_gp_email.send_gp_email")
@patch(f"{FILE_PATH}.send_gp_email._SendGPEmail__update_status")
def test_lambda_handler(
    mock_update_status: MagicMock,
    mock_send_gp_email: MagicMock,
    mock_load_email_content: MagicMock,
    mock_get_item: MagicMock,
):
    # Arrange
    rtn = {"GPEmailAddresses": {"L": "email"}}
    mock_get_item.return_value = rtn
    # Act
    response = lambda_handler(DYNAMO_DB_MOCK_EVENT.copy(), {})
    # Assert
    mock_get_item.assert_called_once()
    mock_load_email_content.assert_called_once()
    mock_send_gp_email.assert_called_once()
    mock_update_status.assert_called_once()

    assert response == {"statusCode": 200, "body": {"message": "OK"}}
