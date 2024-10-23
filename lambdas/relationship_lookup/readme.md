# Relationship Lookup

Retrieves the relationship information for a given NHS number.

If the lookup is successful, then the PDS record is returned.
Otherwise an error is returned

## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose |
|---|---|
| app_id | The identifier for the application in the NHS API Onboarding web application |
| api_base | The PDS endpoint to use to retrieve the relationship data |

The default configuration points to the sandbox environment.

## Parameters

The lambda requires the following inputs

| Parameter name | Data type | Purpose |
|---|---|---|
| nhsNumber | string | The NHS Number to retrieve relationship lookup information for.  The NHS number is a 10 character number validated using [ISBN-10 check digit](https://en.wikipedia.org/wiki/ISBN#ISBN-10_check_digits) |
| authToken | string | The authorization token to use to retrieve the relationship information |

## Outputs

The lambda is expected to return the following

| Ouput path | Data type | Purpose |
|---|---|---|
| statusCode | int | The HTTP status code for the operation. |
| body.error | string | An string detailing the error message - The value is `None` when there is no error with the operation |
| body.pdsRelationshipRecord | array | An array of [FHIR Relationship](https://build.fhir.org/relatedperson.html) records that have been retrieved from PDS.<br/>The collection can be empty is no results were retrieved.<br/>The value is `None` if there was an error retrieving the information. |

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
from lambdas.relationship_lookup.main import lambda_handler

nhs_number = "9000000009"
auth_token = "auth_token_value"

result = lambda_handler({"nhsNumber": nhs_number, "authToken": auth_token}, None)

print("--- ***** ---")
print("Relationship lookup result:")
print("Response Status Code: " + str(result['statusCode']))
if (result['body']['error'] is not None):
    print("Error: " + result['body']['error'])
if (result['body']['pdsRelationshipRecord'] is not None):
    print("Recieved: " + str(len(result['body']['pdsRelationshipRecord'])) + " records")  # Expected two records
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
