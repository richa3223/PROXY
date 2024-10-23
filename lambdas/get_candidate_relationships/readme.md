# Get Candidate Relationships

Get Candidate Relationships is a lambda function that returns the relationships between a proxy and a patient. Essentially a wrapper for the Validate Relationships Step Function Workflow.
As well the lambda verifies some parameters and transforms any errors into FHIR format.

## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose                       |
| ------------ | ----------------------------- |
|              | No specific settings required |

## Parameters

The lambda requires the following inputs

| Parameter name           | Data type | Purpose                                                                                                       |
| ------------------------ | --------- | ------------------------------------------------------------------------------------------------------------- |
| accesstoken.auth_level   | str       | Auth level header - required value 'P9'                                                                       |
| accesstoken.auth_user_id | str       | NHS number of the requester                                                                                   |
| proxyNhsNumber           | str       | NHS number of the proxy                                                                                       |
| patientNhsNumber         | str       | NHS number of the patient                                                                                     |
| correlationId            | str       | A guid that allows the requests to be traced                                                                  |
| originalRequestUrl       | str       | Orginal request URL from APIM Proxy                                                                           |
| _include                 | str       | Additional resources to include in the output.  Only the value 'RelatedPerson:patient' is currently supported |
| requestId                | str       | A guid that allows the requests to be traced                                                                  |

## Outputs

The lambda is expected to return the following when successful

| Output      | Data type | Purpose                                                             |
| ----------- | --------- | ------------------------------------------------------------------- |
| status_code | str       | Status Code from    Validate Relationships Step Function Workflow   |
| body        | dict      | The response from the Validate Relationships Step Function Workflow |


The lambda is expected to return the following when failure

| Output      | Data type | Purpose                                                         |
| ----------- | --------- | --------------------------------------------------------------- |
| status_code | str       | HTTP Status code indicating failure code, eg, 400 - Bad Request |
| body        | str       | FHIR Operational Outcome                                        |

Non-exhaustive list of response codes
400 - Required header 'accesstoken.auth_level' is missing.
400 - Required header 'accesstoken.auth_level' is missing.
400 - Insufficient authorisation - requires P9.
403 - Permission denied.
500 - Internal Server Error - "SERVER ERROR".

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
import os
from lambdas.get_candidate_relationships.main import lambda_handler

event = {
    "proxyNhsNumber": 9730675929,
    "patientNhsNumber": 9730676399,
    "_include": "RelatedPerson:patient",
    "accesstoken.auth_level": "P9",
    "accesstoken.auth_user_id": "9730675929",
    "correlationId": "734f6f44-4513-4894-8a7c-07acc2a27fc7",
    "originalRequestUrl": "www.google.com",
    "requestId": "193d0541-7be2-483c-aac8-e1eda16cc40d",
}
# You can provide an appropriate context here
context = {}
# Parameters
os.environ["VALIDATE_RELATIONSHIPS_STATE_MACHINE_ARN"] = (
    "Place your state machine ARN here"
)

# Invoke the Lambda function
response = lambda_handler(event, context)

# Print the response
print(json.dumps(response, indent=2))
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
