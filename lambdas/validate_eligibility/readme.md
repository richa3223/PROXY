# Validate Eligibility

## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose                       |
| ------------ | ----------------------------- |
|              | No specific settings required |

## Parameters

The lambda requires the following inputs

| Parameter name                  | Data type     | Purpose                                                                                                |
| ------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| pdsProxyDetails                 | object        | PDS Details record of the Proxy User, to confirm they are eligible to use the service                  |
| pdsProxyStatusCode              | number        | Status Code of PDS Details record, to determine if a record has been found                             |
| pdsRelationshipLookup           | object (List) | PDS object Array of Related Person Records, to confirm records have been found and filter if required. |
| pdsRelationshipLookupStatusCode | number        | Status Code of PDS Relationship Look up, to determine if a relationship has been found                 |
| patientNhsNumber [Optional]     | string        | NHS Number of the patient if matching a 1:1 validation. This is an optional value                      |
| correlation_id [Optional]       | string        | A correlation id to allow the request to be traced.  Will be stored with audit on success.             |
| requestId                       | string        | A unique identifier for the request. This is used to track the request through the system.             |

## Outputs

The lambda is expected to return the following

| Output path          | Data type           | Purpose                                                                                                             |
| -------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| statusCode           | HTTPStatus          | The HTTP status code for the operation                                                                              |
| body.elibility       | Boolean             | Value to show if the user is eligible for the service based on parameter values                                     |
| body.relationshipArr | list[RelatedPerson] | An array of FHIR Relationship records, if patientNhsNumber parameter was present the array would have been filtered |
| body.error           | string              | An string detailing the error message - the value is not present on an successful call                              |

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
from lambdas.validate_eligibility.main import lambda_handler
import os
import json

def load_mock_record(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

DATAPATH = "/lambdas/utils/pds/sample_data/"
MOCK_RECORD_FILE_PROXY = (
        os.path.dirname(os.path.realpath(__file__))
        + DATAPATH + "patient_details/proxy_valid.json"
    )

MOCK_RELATIONSHIP_FILE = (
        os.path.dirname(os.path.realpath(__file__))
        + DATAPATH + "related_person_internal_response/proxy_valid_three_children.json"
    )

# Define your test event and context
event = {
    "pdsProxyDetails": load_mock_record(MOCK_RECORD_FILE_PROXY),
    "pdsProxyStatusCode": 200,
    "pdsRelationshipLookup": load_mock_record(MOCK_RELATIONSHIP_FILE),
    "pdsRelationshipLookupStatusCode": 200
}

# You can provide an appropriate context here
context = {}

# Invoke the Lambda function
response = lambda_handler(event, context)

# Print the response
print("--------------------------------------------")
print("Validate Elibility")
print("--------------------------------------------")
print("Status Code: ", response["statusCode"])
if(response["statusCode"] == 200):
    print("Elibility: ", response["body"]["elibility"])
    print("Relationshhip Arr Count: ", len(response["body"]["relationshipArr"]))
else:
    print(response["body"]["error"])
print("--------------------------------------------")
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
