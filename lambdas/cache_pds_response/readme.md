# Cache PDS responses

This lambda provides a DynamoDB backed cache for requests to the PDS INT environment
to insulate us against it not being available or request frequency being over the rate
limit.

## Configuration

The following settings are required for the lambda to run.

Environment Variables:

`DYNAMODB_TABLE_NAME` - DynamoDB table used to cache PDS responses

## Input Event

The event passed to the lambda is expected to come from an
[API Gateway Proxy Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html)

e.g.

```json
{

    "resource": "/{proxy+}",
    "path": "/FHIR/R4/Patient/9730675953/RelatedPerson",
    "httpMethod": "GET",
    "headers": {
        "Accept": "application/json",
        "X-Request-ID": "id",
        "Authorization": "Bearer AUTH"
    },
    "queryStringParameters": {
        "parameter1": "value1,value2",
        "parameter2": "value"
    }
}
```

## Output Response

The lambda is expected to return the response from PDS in a format which can be
consumed by an API Gateway Proxy Integration e.g.

```json
 {
    "statusCode": 200,
    "body": "...",
    "headers": {"Content-Type": "application/json"}
}
```


## Local Testing

    1. Ensure AWS profile is exported - `export AWS_PROFILE=proxy-nhs-dev`
    2. Ensure AWS Login is done - e.g. `aws sso login`
    3. Ensure environment variables are set:
        ```
        export PDS_CREDENTIALS="nhs/api/credentials"
        export REGION="eu-west-2"
        ```

The following is a code sample of a python script that will allow the lambda to be run.

```python
from lambdas.cache_pds_response.main import lambda_handler

    auth_token = AUTH_TOKEN
    headers = {"Accept": "application/json",
               "X-Request-ID": str(uuid4()),
               "Authorization": f"Bearer {auth_token}"}

    id 9730675929
    path = f"/FHIR/R4/Patient/{id}" # /RelatedPerson"

    event = {
        "resource": "/{proxy+}",
        "path": path,
        "httpMethod": "GET",
        "headers": headers,
        "queryStringParameters": {
            "parameter1": "value1,value2",
            "parameter2": "value"
        }
    }

    response = lambda_handler(event, None)

    print("Event:")
    print(dumps(event))
```

## Deployment

This lambda function is deployed to AWS using Terraform.
