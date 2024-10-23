
# Create Merged Email

Merges the S3 email template into a hydrated email and save that email to S3

## Parameters

The lambda requires the following inputs

| Parameter name                            | Data type | Purpose                                      |
| ----------------------------------------- | --------- | -------------------------------------------- |
| Item                                      | dict      | DynamoDB item, minimum item in example below |
| email_details.email_content.email_subject | str       | Email subject line from the email template   |
| email_details.email_content.email_body    | str       | Email body from the email template (HTML)    |

### Minimum DynamoDB item

```json
{
    "PatientNHSNumber": {
        "S": "9730676399"
    },
    "ApplicationStatus": {
        "S": "ACCESS_REQUEST_READY_FOR_AUTHORISATION"
    },
    "ReferenceCode": {
        "S": "test_591e2720-7223-47fd-bd3a-e05730da421d"
    },
    "OdsCode": {
        "S": "A20047"
    }
}
```

## Outputs

The lambda is expected to return the following

| Output path | Data type | Purpose                       |
| ----------- | --------- | ----------------------------- |
| file_name   | string    | The S3 key for hydrated email |

## Errors

The lambda can raise a number of errors when attempting to process the request.  In each case the lambda will respond will fail.

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
import os

from lambdas.create_merged_email.main import lambda_handler

os.environ["HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET"] = "" # Example main-dev-hydrated-email-temporary-storage-bucket

event = {
    "Item": {
        "PatientNHSNumber": {"S": "9730676399"},
        "ApplicationStatus": {"S": "ACCESS_REQUEST_READY_FOR_AUTHORISATION"},
        "ReferenceCode": {"S": "test_591e2720-7223-47fd-bd3a-e05730da421d"},
        "OdsCode": {"S": "A20047"},
    },
    "email_details": {
        "email_content": {"email_subject": "Test Subject", "email_body": "Test Body"}
    },
}

result = lambda_handler(event, {})

print("--- ***** ---")
print("Response " + json.dumps(result))
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
