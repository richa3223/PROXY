# Provisioning a new AWS account

There a few resources which are essential for the operation of an AWS environment with terraform:
- S3 bucket for tfstate
- DynamoDB state locking table

These are all defined in the bootstrap module `terraform/modules/bootstrap` and invoked within the bootstrap
stack `terraform/stacks/bootstrap`.

All terraform will be run locally and there are some manual steps to follow to get these resources created.

## Prerequisites

- Terraform installed locally (see project prerequisites)
- Access to the admin role for the AWS account
- A tfvars file must exist for the AWS account in `terraform/stacks/_shared/tfvars`

## 1. Running the bootstrap stack

### 1.1 Search and replace the `demographics-serverless-template` with your project name

Replace:

* dst in the default_variables project_name
* DemographicsServerlessTemplate in the default tags
* Demographics in the default tags
with your project.

### 1.2 Comment out the backend config in `terraform/stacks/bootstrap/state.tf` like below:

```
terraform {
  required_version = ">= 0.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
#  backend "s3" {
#    region = "eu-west-2"
#  }
}
```

This needs to be done as the remote backend within S3 does not yet exist, so we need to store the state locally until that bucket has been created.

### 1.3 Run a terraform plan with the following (substitute in <ACCOUNT> for the target account):

_Note: `args=` can be used to target specific modules within the stack i.e. `args="-target=module.tfstate -target=module.terraform_base_role"`_

```
make bootstrap-terraform env=<ACCOUNT> tf-command=plan
```

If the initialisation fails, this could be due to a previous initialisation - to remedy, rerun the command after deleting:

- `terraform/stacks/account/.terraform`
- `terraform/stacks/account/.terraform.lock.hcl`

### 1.4 Create a workspace with the same name as the account

```
make terraform-workspace env=<ACCOUNT> stack=bootstrap workspace=<ACCOUNT>
```

### 1.5 If the plan output is as expected

Deploy terraform using the following (substitute in <ACCOUNT> for the target account):

```
make bootstrap-terraform env=<ACCOUNT> tf-command=apply args="-auto-approve=true"
```

## 2. Push local state to newly created remote S3 state bucket

### 2.1 Uncomment the backend config in `terraform/stacks/bootstrap/state.tf` like below:

```
terraform {
  required_version = ">= 0.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    region = "eu-west-2"
  }
}
```

### 2.2 Rerun The bootstrap terraform using the correct backend config with:

```
make terraform env=<ACCOUNT> workspace=<ACCOUNT> stack=bootstrap tf-command=apply
```

You should see a prompt like the below:

```
terraform -chdir=./terraform/stacks/bootstrap init -var-file=terraform/stacks/_shared/tfvars/dev.tfvars -backend-config=backends/dev.bootstrap.tfbackend -upgrade
Upgrading modules...
- terraform_base_role in ../../modules/bootstrap/base_iam_roles
- tfstate in ../../modules/bootstrap/tfstate

Initializing the backend...
Do you want to migrate all workspaces to "s3"?
  Both the existing "local" backend and the newly configured "s3" backend
  support workspaces. When migrating between backends, Terraform will copy
  all workspaces (with the same names). THIS WILL OVERWRITE any conflicting
  states in the destination.

  Terraform initialization doesn't currently migrate only select workspaces.
  If you want to migrate a select number of workspaces, you must manually
  pull and push those states.

  If you answer "yes", Terraform will migrate all states. If you answer
  "no", Terraform will abort.

  Enter a value:

```

Type `yes` and press enter, this will push the local state to the remote S3 state bucket and reinitialise the terraform
against the remote S3 state bucket.

## 3. Deletion of the default VPC resource

At this point the default VPC should be deleted from each region. Deletion of default VPC resources can be done in the AWS Console, for each region:

- In the AWS Console select the "VPC" service
- Select the default VPC, ensuring the "Default" column is marked "yes"
- Click on actions and Delete VPC and check the necessary boxes to confirm
