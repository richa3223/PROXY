# PDS get Patient Details


## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose |
|---|---|
| app_id | The identifier for the application in the NHS API Onboarding web application |
| api_base | The PDS endpoint to use to retrieve the Patient details |

The default configuration points to the sandbox environment.

## Parameters

The lambda requires the following inputs

| Parameter name | Data type | Purpose |
|---|---|---|
| nhsNumber | string | The NHS Number to retrieve Patient details for.  The NHS number is a 10 character number validated using [ISBN-10 check digit](https://en.wikipedia.org/wiki/ISBN#ISBN-10_check_digits) |
| authToken | string | The authorization token to use to retrieve the Patient details |

## Outputs

The lambda is expected to return the following

| Ouput path | Data type | Purpose |
|---|---|---|
| statusCode | int | The HTTP status code for the operation. |
| body.error | string | An string detailing the error message - The value is `None` when there is no error with the operation |
| body.pdsPatientRecord | object | The FHIR object containing the Patient details from the PDS record<br/>The value is `None` if there was an error retrieving the information. |

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
from lambdas.pds_get_patient_details.main import lambda_handler

# Define your test event and context
event = {
    "authToken": "abc",
    "nhsNumber": "9000000009"
}

# You can provide an appropriate context here
context = {}

# Invoke the Lambda function
response = lambda_handler(event, context)

# Print the response
print(json.dumps(response, indent=2))
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
