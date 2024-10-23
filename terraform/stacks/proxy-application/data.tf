################################################################################
# General Datasources
################################################################################

data "aws_caller_identity" "current" {}

################################################################################
# VPC Resource specific Datasources
################################################################################
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

data "aws_cloudwatch_event_bus" "event_bus" {
  name = "${local.common_stack_workspace}-event-bus"
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

data "aws_route53_zone" "primary_hosted_zone" {
  count = local.is_main_workspace ? 1 : 0
  name  = "validated-relationships-service-${var.environment}.national.nhs.uk"
}

data "aws_acm_certificate" "tls_certificate" {
  count       = local.is_main_workspace ? 1 : 0
  domain      = data.aws_route53_zone.primary_hosted_zone[0].name
  most_recent = true
}

data "aws_vpc_endpoint" "s3" {
  vpc_id       = data.aws_vpc.proxy_vpc.id
  service_name = "com.amazonaws.${local.aws_region}.s3"
}

data "aws_dynamodb_table" "patient_relationship" {
  name = "${local.common_stack_workspace}-${var.project}-patient-relationship"
}

data "aws_kms_key" "dynamodb_kms_key" {
  key_id = "alias/${local.common_stack_workspace}-${var.project}-dynamodb-key"
}

data "aws_sqs_queue" "event_bus_dlq" {
  name = "${local.common_stack_workspace}-event-bus-dlq"
}
