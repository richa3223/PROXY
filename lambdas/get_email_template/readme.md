
# Get Email Template

Get the email template (subject and content) for the email that will be sent to the GP.

The lambda uses the AWS S3 bucket to retrieve the email template.

## Parameters

The lambda requires the following parameters to be passed in the event:

| Parameter           | Data type | Purpose                                      |
| ------------------- | --------- | -------------------------------------------- |
| template_identifier | string    | The identifier of the email template to use. |

## Outputs

The lambda is expected to return the following

| Output path | Data type | Purpose          |
| ----------- | --------- | ---------------- |
| NO-PATH     | dict      | The s3 template. |


## Errors

The lambda can raise a number of errors when attempting to process the request.  In each case the lambda will respond will fail.

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
import os

from lambdas.get_email_template.main import lambda_handler

os.environ["ODS_LOOKUP_CREDENTIALS"] = "Ods secret" # e.g /main/ods-lookup-credentials-nI6W5BQWlWGssbLg
os.environ["EMAIL_TEMPLATE_BUCKET"] = "Add bucket name here (consider using main's bucket to test)" # e.g main-dev-email-template-bucket

event = {"template_identifier": "adult_to_child"}

result = lambda_handler(event, {})
print("--- ***** ---")
print("Get Email Template result:")
print("Response " + json.dumps(result))
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
