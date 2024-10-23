data "aws_caller_identity" "current" {}

data "aws_iam_account_alias" "current" {}

# Retrieve VPC Attributes
data "aws_vpc" "proxy_vpc" {
  tags = {
    Name = "${local.common_stack_workspace}-vpc"
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

# Retrieve all Security Groups
data "aws_security_groups" "lambda_security_groups" {
  filter {
    name = "group-name"
    values = [
      "${local.common_stack_workspace}-lambda-base-private-access-sg",
      "${local.common_stack_workspace}-lambda-base-internet-access-sg"
    ]
  }

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.proxy_vpc.id]
  }
}

# DNS

data "aws_route53_zone" "primary_hosted_zone" {
  name = "validated-relationships-service-${var.environment}.national.nhs.uk"
}

data "aws_dynamodb_table" "pds_response_cache" {
  name = "${local.workspace}-${var.project}-pds-response-cache"
}

data "aws_kms_key" "dynamodb_kms_key" {
  key_id = "alias/${local.common_stack_workspace}-${var.project}-dynamodb-key"
}
