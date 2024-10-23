# Email stack

Email stack is expected to be run in a GitHub workflow, once per AWS account.

## Prerequisites:

1. Assume into AWS
    1. Run `aws sso login --profile=nhs-dev-admin`
    2. Run `export AWS_PROFILE=nhs-dev-admin`

## Deployment

It is recommended to plan prior to applying but is not necessary

Run from the root of the project

- Plan: `make terraform env= workspace= stack=email tf-command=plan use_shared_common_stack=true`
- Apply: `make terraform env= workspace= stack=email tf-command=apply use_shared_common_stack=true`

Examples for dev environment:

- Plan: `make terraform env=dev workspace=main stack=email tf-command=plan use_shared_common_stack=true`
- Apply: `make terraform env=dev workspace=main stack=email tf-command=apply use_shared_common_stack=true`
