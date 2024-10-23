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
