resource "local_file" "truststore" {
  depends_on = [module.mutual_tls_truststore_bucket]
  filename   = "truststore.pem"
  content    = var.MTLS_CERTIFICATE
  provisioner "local-exec" {
    command = "aws s3 cp truststore.pem s3://${module.mutual_tls_truststore_bucket.bucket_name}"
  }
}

module "mutual_tls_truststore_bucket" {
  source = "../../modules/s3"

  workspace                = local.workspace
  enable_bucket_versioning = true
  bucket_name              = "${local.workspace}-${var.environment}-truststore-bucket"
  audit_bucket_id          = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  vpc_endpoint_id          = data.aws_vpc_endpoint.s3.id
  force_destroy            = var.environment == "prod" ? false : true
  tags = {
    "Name" = "${local.workspace}-${var.environment}-truststore-bucket"
  }
}
