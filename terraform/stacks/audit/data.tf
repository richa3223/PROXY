data "aws_iam_account_alias" "current" {}

data "aws_caller_identity" "current" {}
# Retrieve VPC Attributes
data "aws_vpc" "proxy_vpc" {
  tags = {
    Name = "${local.common_stack_workspace}-vpc"
  }
}


# Retrieve S3 private endpoint
data "aws_vpc_endpoint" "s3" {
  vpc_id       = data.aws_vpc.proxy_vpc.id
  service_name = "com.amazonaws.${local.aws_region}.s3"
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

data "aws_sqs_queue" "event_bus_dlq" {
  name = "${local.common_stack_workspace}-event-bus-dlq"
}

#Sensitive Bucket Permissions
data "aws_iam_policy_document" "lambda_sensitive_start_crawler_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "glue:StartCrawler"
    ]

    resources = [
      local.sensitive_audit_kinesis_firehose_destination.bucket_arn,
      "${local.sensitive_audit_kinesis_firehose_destination.bucket_arn}/*",
      module.sensitive_glue_crawler.crawler_arn

    ]
  }
}

#Standard Bucket Permissions
data "aws_iam_policy_document" "lambda_standard_start_crawler_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "glue:StartCrawler"
    ]

    resources = [
      local.standard_audit_kinesis_firehose_destination.bucket_arn,
      "${local.standard_audit_kinesis_firehose_destination.bucket_arn}/*",
      module.standard_glue_crawler.crawler_arn

    ]
  }
}