# Process validation result

Returns a result FHIR response based on the inputs

## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose |
|---|---|
|  | No specific settings required |

## Parameters

The lambda requires the following inputs

| Parameter name | Data type | Purpose |
|---|---|---|
| pdsPatientRelationship | json | Array containing two objects pdsPatient = PDS patient record, & pdsRelationship = PDS relationship record |
| originalRequestUrl | str | Original request URL from APIM Proxy |
| _include | str | Additional resources to include in the output.  Only the value 'RelatedPerson:patient' is currently supported |
| proxyIdentifier | json | Proxy Identifier json, expected keys (system, value) |

or in the event of an error the following inputs

| Parameter name | Data type | Purpose |
|---|---|---|
| error | json | with the following values |
| - http_status | string | The HTTP status code of the output |
| - response_code | string | The response code string of the response |
| - audit_msg | string | A detailed message of that provides details of the error |
| - system | string | The system that indicates the source of the codes |
| - version | string | Version number indicator |
| - display | string | A short message that indicates what the error is |
| - severity | string | The severity level of the error |
| - issue_code | string | The error code |
| - expression | [string] | Array of expressions that caused the error |

## Outputs

The lambda is expected to return the following

| Output path | Data type | Purpose |
|---|---|---|
| FHIR Content | json | Bundle response containing the relationship and patient information or an operational response if an error occurred |

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
import os
from lambdas.process_validation_result.main import lambda_handler

mock_proxy_file_sandpit_patient = (
    os.path.dirname(os.path.realpath(__file__))
    + "/lambdas/utils/pds/sample_data/patient_details/sample_sandpit_patient.json"
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
relatedjson = load_mock_record(mock_proxy_file_sandpit_two_related_person)[0]

# Define your test event and context
event = {
    "pdsPatientRelationship": [{"pdsPatient": patientjson, "pdsRelationship": relatedjson}]
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
