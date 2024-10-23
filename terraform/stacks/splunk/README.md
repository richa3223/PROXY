# Splunk stack

Splunk stack is expected to be run in a GitHub workflow, once per AWS account. But it won't hurt to run multiple Splunk stacks in the dev environment, but you may just get duplicated metrics in Splunk.

## Prerequisites:

1. The `splunk_log_and_metric_formatter` lambda code and layer must be built prior to running the terraform, use `make build-all-lambdas` from the root of the project
2. Assume into AWS
   1. Run `aws sso login --profile=nhs-dev-admin`
   2. Run `export AWS_PROFILE=nhs-dev-admin`
3. Acquire the Splunk Hec Token, this is in GitHub actions or if you're upgrading an existing environment can be found in the existing AWS Firehose credentials section

## Deployment

It is recommended to plan prior to applying but is not necessary

Run from the root of the project

- Plan: `make terraform env= workspace= stack=splunk tf-command=plan use_shared_common_stack=true TF_VAR_SPLUNK_HEC_TOKEN=`
- Apply: `make build-all-lambdas terraform env= workspace= stack=splunk tf-command=apply use_shared_common_stack=true TF_VAR_SPLUNK_HEC_TOKEN=`

Examples for dev environment:

- Plan: `make terraform env=dev workspace=main stack=splunk tf-command=plan use_shared_common_stack=true TF_VAR_SPLUNK_HEC_TOKEN=xxx`
- Apply: `make build-all-lambdas terraform env=dev workspace=main stack=splunk tf-command=apply use_shared_common_stack=true TF_VAR_SPLUNK_HEC_TOKEN=xxx`

## Development

For rapid development make targets can be daisy chained

`make build-all-lambdas terraform env=dev workspace=main stack=splunk tf-command=apply use_shared_common_stack=true args="-auto-approve" TF_VAR_SPLUNK_HEC_TOKEN=xxx`
