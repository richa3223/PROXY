# Scoutsuite S3 Bucket
module "scoutsuite_bucket" {
  source = "../../modules/s3"

  workspace                = local.workspace
  enable_bucket_versioning = true
  bucket_name              = "${var.environment}-scoutsuite-bucket"
  audit_bucket_id          = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  vpc_endpoint_id          = data.aws_vpc.proxy_vpc.id
  force_destroy            = "false"
}
