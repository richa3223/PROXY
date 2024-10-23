
# Relationship Lookup

Authenticates with the NHS Api service to retrieve a token for usage within the PDS API.

If the process is successful, then a token is returned
Otherwise an error is generated

## Configuration

The following settings are required for the lambda to run.

Environment Variables:
LAMBDA_SECRET_STORE_NAME - Signifies the store name under which the secrets will be kept
LAMBDA_SECRET_STORE_REGION - The name of the region to perform the lookup

## Parameters

There are no expected parameters for this lambdra

## Outputs

The lambda is expected to return the following

| Ouput path | Data type | Purpose |
|---|---|---|
| statusCode | int | The HTTP status code for the operation. |
| body.token | string | A JSON string that contains the token and it's meta data|

## Local Testing

    1. Ensure AWS Login is done - aws sso login --profile=proxy-poc-admin
    2. Ensure AWS profile is exported - export AWS_PROFILE=proxy-poc-admin
    3. Ensure environment variables are set (these are for testing)
        export PDS_CREDENTIALS="nhs/api/credentials"
        export REGION="eu-west-2"

The following is a code sample of a python script that will allow the lambda to be run.

```python
from lambdas.pds_access_token.main import lambda_handler

res = lambda_handler({}, None)

print("")
print("Access token generation :")
print(res)
print("Done")
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
