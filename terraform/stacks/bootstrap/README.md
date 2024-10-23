
# bootstrap stack

## Prerequisites:

1. You need to have access to assume the `NHSDAdminRole` in the AWS account for the target environment in order to deploy this stack.

## Deployment

### To generate the initial state bucket and DynamoDB lock table perform the following actions
0) Create/Set the account alias for the account you are setting up
Create the account alias by going to IAM in the env and clicking Create under Account Alias on the right hand side of the screen. Should be in the following format: nhsd-demog-proxy-<env>
1) cd into the terraform/stacks/bootstrap directory
1a) Do clean up the bootstrap/terraform/.terraform and bootstrap/terraform/terraform-state folders using the commands from within the bootstrap/terraform/ directory:
    - rm -r .terraform -f
    - rm -r terraform-state -f
2) Edit the backend.tf as follows:
    uncomment the 'local' backend block.
    comment out the 'S3' backend block.
    save the changes
3) Initialize the Terraform environment using the following command (this assumes terraform is installed locally)
    terraform init -upgrade
4) once initialized successfully you can go ahead and bootstrap the AWS account using the following command, remember to note down the outputs for the next step
    terraform apply
    Note: Its recommended to run a plan before apply
5) With the S3 bucket and DynamoDB lock table generated you must now update the backend-config file for the AWS Account with the kms key id
    The KMS Key Arn is listed in the outputs of step 4.
    Copy the ARN value
    Back in the code base add the ARN to the 'kms_key_id' value in the following files:
        'terraform/backend_config/<Account ID i.e. dev>/bootstrap.conf
        'terraform/backend_config/<Account ID i.e. dev>/baseconfig.conf

    After changes, the contents of the backend configuration files should look something like the following:
    ```
        bucket         = "pvrs-nhsd-demog-proxy-{env}-tfstate"
        key            = "baseconfig/{env}-bootstrap.tfstate"
        dynamodb_table = "pvrs-nhsd-demog-proxy-qa-tflock"
        region         = "eu-west-2"
        encrypt        = "true"
        kms_key_id     = "arn:aws:kms:eu-west-2:{acc-no}:key/{key-id}"
    ```
6) You can now transfer the bootstrap state file into the created S3 bucket by editing the backend.tf again
    comment out the 'local' backend block.
    uncomment the 'S3' backend block.
    save the changes
7) To transfer the locally stored state file into S3 run the following command
    terraform init -upgrade -migrate-state -backend-config=../../backend_config/<Account ID i.e. dev>/bootstrap.conf
8) confirm that you want to migrate the current state file to the new location
9) Once this is completed you can initialize the encryption on the state file and create the dynamodb item with the following command
    terraform apply
10) you can confirm this has been successful by checking the dynamodb table for a new md5 item entry.
11) finally you should clean up the bootstrap/terraform/.terraform and bootstrap/terraform/terraform-state folders using the commands from within the bootstrap/terraform/ directory:
    - rm -r .terraform -f
    - rm -r terraform-state -f

### Routine Deployment

After the initial setup has been completed you can now deploy the baseconfig stack to the AWS account using the following steps:

1. `cd` into the `terraform/stacks/bootstrap` folder.
2. Run:

```
rm -r .terraform -f
rm -r terraform-state -f
```

3. If it exists delete the '.terraform' folder to ensure there isn't any information relating to another environment.
4. initialize the terraform environment using the command:

```
terraform init -upgrade -backend-config=../../backend_config/{Account ID i.e. dev}/bootstrap.conf
```

5. With terraform initialized you can then plan / apply the base account resources. Use the following command:

```
terraform plan | apply
```
