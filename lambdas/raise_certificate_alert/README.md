# Raise Certificate Alert

This lambda function is used to raise a slack and email alert when a certificate nears expiry.

## Configuration

The lambda is configured using the following environment variables

| Variable name                     | Purpose                                                                |
| --------------------------------- | ---------------------------------------------------------------------- |
| ENVIRONMENT                       | The environment the lambda is running in.                              |
| WORKSPACE                         | The workspace the lambda is running in.                                |
| MTLS_CERTIFICATE_BUCKET_NAME      | The name of the bucket containing the certificates                     |
| SEND_NHS_MAIL_API_CREDENTIALS     | The secret manager secret for the credentials of NHS.UK Send email API |
| SLACK_ALERTS_LAMBDA_FUNCTION_NAME | The name of the slack alerts lambda function                           |
| TEAM_EMAIL                        | The email address of the team to send the alerts to.                   |

## Parameters

The lambda requires no inputs.

## Outputs

The lambda returns a response object with a message if the lambda was successful.

| Output path | Data type | Purpose                                   |
| ----------- | --------- | ----------------------------------------- |
| message     | string    | The message to say lambda was successful. |

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
from os import environ

from lambdas.raise_certificate_alert.main import lambda_handler

environ["ENVIRONMENT"] = "environment"
environ["WORKSPACE"] = "workspace"
environ["MTLS_CERTIFICATE_BUCKET_NAME"] = "mtls_certificate_bucket_name"
environ["SEND_NHS_MAIL_API_CREDENTIALS"] = "send_nhs_mail_api_credentials"
environ["SLACK_ALERTS_LAMBDA_FUNCTION_NAME"] = "slack_alerts_lambda_function_name"
environ["TEAM_EMAIL"] = "team_email"

result = lambda_handler({}, None)

print("--- ***** ---")
print("Raise certificate alert result:")
print("Response Body: " + result["message"])

```
