# ODS Lookup

Retrieves the GP ODS information for a given GP ODS code.

The lambda uses the AWS secrets to retrieve the subscription key for calling the ODS service.

## Parameters

The lambda requires the following inputs

| Parameter name | Data type | Purpose                                              |
| -------------- | --------- | ---------------------------------------------------- |
| ods_code       | str       | The ods code that further information is required on |

## Configuration

The following settings are required for the lambda to run.

| Setting name           | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| ENVIRONMENT            | Environment that lambda is run in e.g. dev |
| ODS_LOOKUP_BASE_URL    | Ods Lookup API URL                         |
| ODS_LOOKUP_CREDENTIALS | Secret Name for ODS lookup API credentials |

## Outputs

The lambda is expected to return a dynamodb list of email addresses.

Example:
```json
{
    "L": [
        {"S": "test@test.com"},
        {"S": "test2@test.com"},
        {"S": "test3@test.com"},
    ]
}
```

## Errors

The lambda can raise a number of errors when attempting to process the request.  In each case the lambda will respond will fail.

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
import os

os.environ["ODS_LOOKUP_CREDENTIALS"] = "/main/ods-lookup-credentials-nI6W5BQWlWGssbLg"

from lambdas.ods_lookup.main import lambda_handler

os.environ["ENVIRONMENT"] = "dev"
os.environ["ODS_LOOKUP_BASE_URL"] = (
    "https://nhsuk-apim-stag-uks.azure-api.net/account-proxy-uks/gp-surgery"
)

event = {"ods_code": "A20047"}

result = lambda_handler(event, {})

print("--- ***** ---")
print("ODS Lookup result:")
print("Response " + json.dumps(result))

```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
