# baseconfig stack

The `baseconfig` is only run when a new environment in a new AWS Account is created. It is run by hand from a trusted Admin's local machine.

## Prerequisites:

1. You need to have access to assume the `NHSDAdminRole` in the AWS account for the target environment in order to deploy this stack.
1. Bootstrap the target AWS account. See the [bootstrap README](../bootstrap/README.md). Once the AWS account has been bootstrapped it is ready to have the base resources deployed as described below.

## Deployment

1. `cd` into the `terraform/stacks/baseconfig` folder.
2. Run:

```
rm -r .terraform -f
rm -r terraform-state -f
```

3. If it exists delete the '.terraform' folder to ensure there isn't any information relating to another environment.
4. initialize the terraform environment using the command:

```
terraform init -upgrade -backend-config=../../backend_config/{Account ID i.e. dev}/baseconfig.conf
```

5. With terraform initialized you can then plan / apply the base account resources. Use the following command:

```
terraform plan | apply
```
