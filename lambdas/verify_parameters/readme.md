# Verify Parameters

Verifies the parameters are present and match the acceptance criteria.

## Configuration

The following settings are required for the lambda to run.

| Setting name | Purpose                       |
| ------------ | ----------------------------- |
|              | No specific settings required |

## Parameters

The lambda requires the following inputs

| Parameter name     | Data type | Purpose                                                                                                       |
| ------------------ | --------- | ------------------------------------------------------------------------------------------------------------- |
| proxyNhsNumber     | str       | NHS number of the proxy                                                                                       |
| patientNhsNumber   | str       | NHS number of the patient                                                                                     |
| correlationId      | str       | A guid that allows the requests to be traced                                                                  |
| originalRequestUrl | str       | Orginal request URL from APIM Proxy                                                                           |
| _include           | str       | Additional resources to include in the output.  Only the value 'RelatedPerson:patient' is currently supported |
| requestId          | str       | A guid that allows the requests to be traced                                                                  |

## Outputs

The lambda is expected to return the following when successful

| Output             | Data type | Purpose                                                                                             |
| ------------------ | --------- | --------------------------------------------------------------------------------------------------- |
| proxyNhsNumber     | str       | NHS number of the proxy                                                                             |
| patientNhsNumber   | str       | NHS number of the patient                                                                           |
| correlationId      | str       | A guid that allows the requests to be traced                                                        |
| originalRequestUrl | str       | Orginal request URL from APIM Proxy                                                                 |
| _include           | str       | Additional resources to include in the output.  Only 'RelatedPerson:patient' is currently supported |

The lambda is expected to return the following when failure

| Output            | Data type | Purpose                                                         |
| ----------------- | --------- | --------------------------------------------------------------- |
| error             | bool      | Flag indicating an error has occurred                           |
| error_status_code | int       | HTTP Status code indicating failure code, eg, 400 - Bad Request |
| error_description | str       | Description of the error                                        |

Non-exhaustive list of response codes
For a full list of response codes see the [API Specification](https://github.com/NHSDigital/validated-relationships-service-api/blob/e56620340f30965373259ebb92c92c98d72d01e3/specification/validated-relationships-service-api.yaml#L188)
500 - Internal Server Error - "SERVER ERROR".
501 - This request is not currently supported.

## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python
import json
import os
from lambdas.verify_parameters.main import lambda_handler

event = {
    "proxyNhsNumber": "9000000009",
    "patientNhsNumber": "9000000009",
    "originalRequestUrl": "test-url"
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
