# Proxy Validated Relationships Service Terraform

## Structure

The terraform for the Proxy Validated Relationships Service(VRS) project has a stack-based structure where the majority of resources are defined
under [`modules/`](modules) and separated into sensible sections of the system which call the previously defined modules.

# [Stacks](stacks)

1. audit - Audit store
1. baseconfig - Note this is deployed by hand see [stack README](stacks/baseconfig/README.md) for details.
1. bootstrap - Used for initial terraform setup
1. common - Resources required by both audit and proxy-application stacks
1. email - Used for deploying SQS queues for sending emails
1. [github](stacks/github/README.md) - Used to manage VRS GitHub repositories and teams
1. proxy-application - Implements the VRS API
1. security - Used for deploying Scoutsuite S3 Bucket
1. splunk - Splunk stack for sending logs/metrics to splunk, expected to be deployed once per environment by GitHub Actions

## Running terraform:

There is a [Makefile](../Makefile) in the root of the project which has commands available for running any desired terraform.
This has a heavy reliance on passing variables with the command in order to target the correct environment, stack and workspace.

## Using shared resources
The common stack contains a number of shared resources that usually live in the "main" workspace. These resources are used by other stacks (i.e. audit, proxy-application).

However the common stack can also be deployed in its own workspace for cases where we need to make changes to common resources before committing them to main. Other stacks determine if they should use the shared  resources in the "main" workspace or point to a newly deployed common stack by the "use_shared_common_stack" environment value.

When this value is set to `true`, stacks deployed into any workspace will always point to the shared resources in the "main" workspace. If this is set to `false`, then resources will point to the common stack in the same workspace as they are in. In that case the common stack will need to be deployed in the same workspace to ensure a successful E2E deployment.

TLDR: Unless making changes to the common stack, the "use_shared_common_stack" environment value should always be set to `true`.

Using shared resources can be changed in the command line by setting the argument "use_shared_common_stack" to `true` or `false`.

### Command arguments

- `env` - The environment/account to run the terraform against i.e. dev/qa/int/prod
- `stack` - The targeted stack i.e. bootstrap/account/application
- `workspace` - The workspace to deploy within i.e. dev/preprod/prod/xxx. Resources should be prefixed with the workspace name
- `tf-command` - The terraform command to run i.e. plan/apply/destroy
- `use_shared_common_stack` - Should this stack use the shared common resource - true/false. This argument is optional and will default to true. Does not apply to the common stack.
- `args` - supplementary arguments or switches for terraform commands i.e. "-auto-approve=true"

A few examples can be seen below:

#### proxy-application stack

##### Running a plan in each environment for the proxy-application stack:

```
make terraform env=<ENVIRONMENT_TO_RUN_AGAINST> stack=proxy-application workspace=<WORKSPACK_TO_USE> tf-command=plan
```

##### Running apply with prompt in each environment for the proxy-application stack:

```
make terraform env=<ENVIRONMENT_TO_RUN_AGAINST> stack=proxy-application workspace=<WORKSPACE_TO_USE> tf-command=apply
```

##### Running apply with prompt in each environment for the proxy-application stack but not using the shared common resources

```
make terraform env=<ENVIRONMENT_TO_RUN_AGAINST> stack=proxy-application workspace=<WORKSPACE_TO_USE> tf-command=apply use_shared_common_stack=false
```

##### Running apply **without** prompt in each environment for the application stack:

```
make terraform env=<ENVIRONMENT_TO_RUN_AGAINST> stack=proxy-application workspace=<WORKSPACE_TO_USE> tf-command=apply args="-auto-approve=true"
```

##### Building all lambdas and running apply with prompt in each environment for the proxy-application stack:

```
make build-and-terraform env=<ENVIRONMENT_TO_RUN_AGAINST> stack=proxy-application workspace=<WORKSPACE_TO_USE> tf-command=apply
```
