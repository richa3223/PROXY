data "aws_iam_account_alias" "current" {}
data "aws_caller_identity" "current" {}

# Retrieve VPC Attributes
data "aws_vpc" "proxy_vpc" {
  tags = {
    Name = "${local.common_stack_workspace}-vpc"
  }
}

# Retrieve private Security Groups
data "aws_security_groups" "private_lambda_security_groups" {
  filter {
    name   = "group-name"
    values = ["${local.common_stack_workspace}-lambda-base-private-access-sg"]
  }

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.proxy_vpc.id]
  }
}

# Retrieve Private Subnet Attributes
data "aws_subnets" "lambda_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.proxy_vpc.id]
  }

  tags = {
    Name = "${local.common_stack_workspace}-vpc-private-eu-west-*"
  }
}
