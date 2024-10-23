module "standard_s3_buckets" {
  source = "../../modules/s3"

  for_each                 = toset([for k, v in local.standard_s3_bucket_names : v])
  workspace                = local.workspace
  enable_bucket_versioning = true
  bucket_name              = "${local.workspace}-${var.environment}-${each.key}-bucket"
  audit_bucket_id          = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  vpc_endpoint_id          = data.aws_vpc_endpoint.s3.id
  tags = {
    "Service" = "Audit"
    "Name"    = "${local.workspace}-iac-s3-bucket"
  }
}

# TODO : Create sensitive s3 policy for sensitive buckets pending TRG decision if PII should be moved outside our environment, using default policy atm -     NPA-1886
module "sensitive_s3_buckets" {
  source = "../../modules/s3"

  for_each                 = toset([for k, v in local.sensitive_s3_bucket_names : v])
  workspace                = local.workspace
  enable_bucket_versioning = true
  bucket_name              = "${local.workspace}-${var.environment}-${each.key}-bucket"
  audit_bucket_id          = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  vpc_endpoint_id          = data.aws_vpc_endpoint.s3.id
  tags = {
    "Service" = "Audit"
    "Name"    = "${local.workspace}-iac-s3-bucket"
  }
}