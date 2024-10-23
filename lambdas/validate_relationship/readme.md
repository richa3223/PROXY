# Validate Relationship

Validates the eligibility and the relationship for a person relating to the primary lookup.

The primary lookup is the main record from PDS (referred to as proxy in some documents).

## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose |
|---|---|
|  | No specific settings required |

## Parameters

The lambda requires the following inputs

| Parameter name | Data type | Purpose |
|---|---|---|
| proxyNhsNumber| str | NHS number of the proxy |
| pdsPatientStatus | int | Status code indicating the outcome for GetPatient request |
| pdsPatient | json | PDS patient record to check |
| pdsRelationshipLookupStatus | int | Status code indicate the outcome for GetRelationship request |
| pdsRelationshipLookup | json | An array of the PDS relationship records returned as part of the relationship lookup |
| correlation_id [Optional] | string | Correlation ID to be used in the audit store on validation outcome |

## Outputs

The lambda is expected to return the following when successful

| Output | Data type | Purpose |
|---|---|---|
| statusCode | int | HTTP Status code indicating successful 200 OK |
| body | json | Two values 'pdsPatient', and 'pdsRelationship' which in turn contain the FHIR data |

The lambda is expected to return the following when failure

| Output | Data type | Purpose |
|---|---|---|
| statusCode | int | HTTP Status code indicating failure code, eg, 400 - Bad Request |
| body | json | Contain a value 'error' which indicates the error reason |

Non-exhaustive list of response codes
400 - Bad Request - "Insufficient information to process request."
400 - Bad Request - "Supplied data cannot be processed"
500 - Internal Server Error - "Request Failed - Unexpected Error"

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
import os
from lambdas.validate_relationship.main import lambda_handler
from http import HTTPStatus

mock_proxy_file_sandpit_patient = (
    os.path.dirname(os.path.realpath(__file__))
    + "/lambdas/utils/pds/sample_data/patient_details/proxy_deceased.json"
)
mock_proxy_file_sandpit_two_related_person = (
    os.path.dirname(os.path.realpath(__file__))
    + "/lambdas/utils/pds/sample_data/related_person/sample_sandpit_two_related_person.json"
)

def load_mock_record(file_path):
    """
    Load a mock record from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the mock record.

    Returns:
        dict: The loaded mock record as a Python dictionary.
    """
    with open(file_path, "r") as file:
        return json.load(file)

# load data from sample PDS responses
# 1 patient
# First element from a list of related people
patientjson = load_mock_record(mock_proxy_file_sandpit_patient)
relatedjson = load_mock_record(mock_proxy_file_sandpit_two_related_person)

# Define your test event and context
# Overwriting to ensure patient and relationship exist
patientjson["birthDate"] = "2020-01-01"
patientjson["deceasedDateTime"] = None
relatedjson[0]["relationship"][0]["coding"][0]["code"] = "MTH"

event = {
    "proxyNhsNumber": "9000000009",
    "pdsRelationshipLookupStatus": HTTPStatus.OK,
    "pdsPatientStatus": HTTPStatus.OK,
    "pdsPatient": patientjson,
    "pdsRelationshipLookup":  relatedjson
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
