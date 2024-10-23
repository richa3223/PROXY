# Testing stack

The testing stack is ran manually in the `dev` AWS environment to
provide infrastructure for running the [locust](https://locust.io/) load tests.

## Prerequisites:

Sign in to AWS:

```sh
export AWS_PROFILE=nhs-dev-admin
aws sso login
```

Make sure the lambda for the PDS Cache is built by running the `make build-lambda-mock_cache_pds_response` in the root of the project.

## Deployment

In the root of the project:

- Plan: `make terraform env=dev workspace=main stack=testing tf-command=plan use_shared_common_stack=true`
- Apply: `make terraform env=dev workspace=main stack=testing tf-command=apply use_shared_common_stack=true`

## Running the load tests

For details of how to run the load tests see
the [Guide to running Load Tests in EC2](https://nhsd-confluence.digital.nhs.uk/display/NPA/Guide+to+running+Load+Tests+in+EC2)
on Confluence.
