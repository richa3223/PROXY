# security stack

`security` should only need to be run once for each environment as it only sets up the creation of the `scoutsuite-bucket`

## Prerequisites:

1. You need to have access to assume the `NHSDAdminRole` in the AWS account for the target environment in order to deploy this stack

## Deployment

1. `cd` into the `terraform/stacks/security` folder
2. Run:

```
rm -r .terraform -f
rm -r terraform-state -f
```

3. If it exists, delete the `.terraform` folder to ensure there isn't any information relating to another environment 
4. Ensure AWS Login is done: 
```
aws sso login --profile=nhs-dev-admin
```
5. Ensure AWS profile is exported:
```
export AWS_PROFILE=nhs-dev-admin
```
6. Initialise the terraform environment using the command:

```
terraform init -upgrade -backend-config=../../backend_config/{Account ID i.e. dev}/security.conf
```

7. With terraform initialised, you can then run a plan and see the changes:

```
terraform plan
```
8. Enter the `Environment` when prompted e.g. `dev`
9. Enter the `main workspace` when prompted as `main`
10. Enter `true` when prompted whether to `use the common stack`
11. You can then run an apply to commit the changes:
```
terraform apply
```