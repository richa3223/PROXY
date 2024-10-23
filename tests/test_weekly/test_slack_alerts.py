from ..helpers import WORKSPACE, Helpers

SLACK_ALERTS_FUNCTION_NAME = f"{WORKSPACE}-slack_alerts"


def test_slack_alert(helpers: Helpers) -> None:
    """Test the slack alerts lambda"""
    # Act
    response = helpers.invoke_lambda_function_from_file(
        SLACK_ALERTS_FUNCTION_NAME,
        "test_weekly/test_inputs/slack_alerts/basic_message.json",
    )
    # Assert
    assert response == {"statusCode": 200, "body": "Slack alerts sent"}
    # TODO: Check that the correct message arrived in Slack - NPA-3178
