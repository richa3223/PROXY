################################################################################
# Required Datasource for OIDC configuration
################################################################################

data "aws_partition" "current" {}
data "tls_certificate" "oidc_tls_cert" { url = var.url }

################################################################################
# General Datasources
################################################################################

data "aws_iam_account_alias" "current" {}
data "aws_caller_identity" "current" {}
