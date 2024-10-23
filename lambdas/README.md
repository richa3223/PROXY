# AWS Lambdas

This is collection of the AWS lambdas used by the API.

Each lambda has an individual readme.md file that provides a description of the lambda as well as an outline of the
parameters needed to run the lambda, expected outputs and a sample code block that can be used to run the lambda as a
standalone python script.

# Monitoring and Logging

Monitoring and Logging is defined in Terraform and for each lambda, a log group is created with the name <workspace>-<
lambda-name>

Lambdas that need internet access have the security group attached for egress.
Lambdas that need access to secrets stored in Secrets Manager, have VPC endpoints security group attached.

# Secrets Manager

Secrets manager is configured in Terraform. Secrets are encrypted with the customer managed KMS key.
Related events are registered in NHSDAudit_trail_log_group
