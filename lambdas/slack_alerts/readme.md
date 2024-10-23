# Slack Alerts

This lambda function is used to send a slack alert to a slack channel. This channel is currently `vrs-alerts`

## Configuration

The lambda is configured using the following environment variables

| Variable name     | Purpose                                                                      |
| ----------------- | ---------------------------------------------------------------------------- |
| SLACK_WEBHOOK_URL | The webhook url for the slack channel, currently this is set to `vrs-alerts` |

## Parameters

The lambda requires a valid slack API message as a parameter.

Example:

```json
{"attachments":[{"color":"#fc0303","blocks":[{"type":"header","text":{"type":"plain_text","text":"Certificate expiry warning"}},{"type":"section","text":{"type":"mrkdwn","text":"Certificate expiry warning for *jack4.pem* - Expiry in 7 days"}},{"type":"divider"},{"type":"section","text":{"type":"mrkdwn","text":"Environment: *dev* | Workspace: *npa-2306* "}},{"type":"rich_text","elements":[{"type":"rich_text_section","elements":[{"type":"text","text":"Please add "},{"type":"emoji","name":"eyes","unicode":"1f440"},{"type":"text","text":" If you've seen this message"}]}]}]}]}
```

## Outputs

The lambda returns a response object with a message if the lambda was successful.

| Output path | Data type | Purpose                                   |
| ----------- | --------- | ----------------------------------------- |
| statusCode  | integer   | The status code of the response.          |
| body        | string    | The message to say lambda was successful. |

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
from os import environ

from lambdas.slack_alerts.main import lambda_handler

environ["SLACK_WEBHOOK_URL"] = "slack_webhook_url"

result = lambda_handler({}, None)

print("--- ***** ---")
print("Slack alerts result:")
print("Response Body: " + result["body"])

```
