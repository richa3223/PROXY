# Send GP Email

Sends an email using SendNHSMail API.

To rotate the credentials use this [confluence page](https://nhsd-confluence.digital.nhs.uk/display/NPA/Send+NHS+Mail+Subscription+Key)

## Configuration

The following environment variables are required for the lambda to run.

| Environment variable          | Purpose                                                                                           |
| ----------------------------- | ------------------------------------------------------------------------------------------------- |
| SEND_NHS_MAIL_API_CREDENTIALS | Secret in AWS Secret Manager containing credentials used to authenticate with the SendNHSMail API |
| HYDRATED_EMAIL_BUCKET         | Name of AWS S3 bucket that contains hydrated emails                                               |
| DYNAMODB_TABLE_NAME           | Name of the dynamo db table where the details of the record are stored                            |

## Parameters

The lambda is triggered by an Dynamo DB stream update event via the service bus.  This event would be in the form similar to

    {
        "version": "0",
        "id": "5443b54e-6347-e458-ea85-447d625869e0",
        "detail-type": "Event from aws:dynamodb",
        "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
        "account": "723625676534",
        "time": "2024-07-04T12:09:24Z",
        "region": "eu-west-2",
        "resources": [],
        "detail": {
            "eventId": "4406b6ae9ac307d4967cec0522adf021",
            "eventType": "GP_AUTHORISATION_REQUEST_CREATED",
            "referenceCode": "18705qcq6p"
        }
    }

The following are the key fields extracted from within this event

| Parameter name | Data type | Purpose                                |
| -------------- | --------- | -------------------------------------- |
| eventType      | string    | The event type change that occurred    |
| referenceCode  | string    | Refernce code of the record            |

## Outputs

The lambda is expected to return the following

| Output path | Data type | Purpose                                         |
| ----------- | --------- | ----------------------------------------------- |
| statusCode  | int       | An integer representing the status value        |
| body        | string    | A short message detailing the operation outcome |

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.
```python
from os import environ

environ["HYDRATED_EMAIL_BUCKET"] = ""
environ["SEND_NHS_MAIL_API_CREDENTIALS"] = ""
environ["DYNAMODB_TABLE_NAME"] = ""

from lambdas.send_gp_email.main import lambda_handler


result = lambda_handler(
    {
        "version": "0",
        "id": "5443b54e-6347-e458-ea85-447d625869e0",
        "detail-type": "Event from aws:dynamodb",
        "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
        "account": "723625676534",
        "time": "2024-07-04T12:09:24Z",
        "region": "eu-west-2",
        "resources": [],
        "detail": {
            "eventId": "4406b6ae9ac307d4967cec0522adf021",
            "eventType": "GP_AUTHORISATION_REQUEST_CREATED",
            "referenceCode": "18705qcq6p",
        },
    },
    None,
)


print("--- ***** ---")
print("Send gp email result:")
print("Response Body: " + result['body'])
```
## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
