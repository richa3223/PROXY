data "aws_caller_identity" "current" {}
data "aws_iam_account_alias" "current" {}

# Retrieve S3 private endpoint
data "aws_vpc_endpoint" "s3" {
  vpc_id       = data.aws_vpc.proxy_vpc.id
  service_name = "com.amazonaws.${local.aws_region}.s3"
}

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


# Retrieve lambda Security Groups
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

data "aws_dynamodb_table" "patient_relationship" {
  name = "${local.common_stack_workspace}-${var.project}-patient-relationship"
}

data "aws_kms_key" "dynamodb_kms_key" {
  key_id = "alias/${local.common_stack_workspace}-${var.project}-dynamodb-key"
}

data "aws_sqs_queue" "event_bus_dlq" {
  name = "${local.common_stack_workspace}-event-bus-dlq"
}
