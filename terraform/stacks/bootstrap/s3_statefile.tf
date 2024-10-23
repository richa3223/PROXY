resource "aws_s3_bucket" "statefile" {
  # TODO: implement
  #checkov:skip=CKV_AWS_18: Ensure the S3 bucket has access logging enabled
  #checkov:skip=CKV2_AWS_62: Ensure S3 buckets should have event notifications enabled
  #checkov:skip=CKV_AWS_144: Ensure that S3 bucket has cross-region replication enabled
  bucket        = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-tfstate"
  force_destroy = "false"

  tags = {
    Name = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-tfstate"
  }
}

resource "aws_s3_bucket_public_access_block" "statefile" {
  bucket = aws_s3_bucket.statefile.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "statefile" {
  #checkov:skip=CKV2_AWS_65: Ensure access control lists for S3 buckets are disabled
  bucket = aws_s3_bucket.statefile.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "statefile" {
  depends_on = [
    aws_s3_bucket_ownership_controls.statefile,
    aws_s3_bucket_server_side_encryption_configuration.statefile,
    aws_s3_bucket_policy.statefile
  ]

  bucket = aws_s3_bucket.statefile.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "statefile" {
  bucket = aws_s3_bucket.statefile.id

  rule {
    bucket_key_enabled = false
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.bootstrap_s3_statefile_bucket_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "statefile" {
  bucket = aws_s3_bucket.statefile.id
  versioning_configuration {
    status = "Enabled"
    #mfa_delete = "Enabled" requires access with MFA enabled and is not possible as we work via SSO
  }
}

resource "aws_s3_bucket_policy" "statefile" {
  bucket = aws_s3_bucket.statefile.id
  policy = data.aws_iam_policy_document.statefile.json

  depends_on = [
    aws_s3_bucket_public_access_block.statefile,
  ]
}

resource "aws_s3_bucket_logging" "statefile" {
  bucket = aws_s3_bucket.statefile.id

  target_bucket = aws_s3_bucket.audit.id
  target_prefix = "log/${aws_s3_bucket.statefile.id}"
}

resource "aws_s3_bucket_lifecycle_configuration" "statefile" {
  bucket = aws_s3_bucket.statefile.id

  rule {
    status = "Enabled"
    id     = "abort_multipart_upload_timeout"
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }

  rule {
    id = "transfer-to-IA"

    filter {
      prefix = ""
    }

    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }
  }
}
