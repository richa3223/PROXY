-> Initialize Terraform using backend config file
terraform init -backend-config='../../backend_config/dev/common.conf'

-> Validate the terraform
terraform validate

-> Create a plan by passing variable file
terraform plan -out main.plan -var-file='../../env_vars/dev/common.tfvars'

-> Apply the plan created in above
terraform apply 'main.plan'
