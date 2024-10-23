resource "aws_s3_bucket" "audit" {
  # TODO: implement
  #checkov:skip=CKV_AWS_18: Ensure the S3 bucket has access logging enabled
  #checkov:skip=CKV_AWS_144: Ensure that S3 bucket has cross-region replication enabled
  #checkov:skip=CKV2_AWS_62: Ensure S3 buckets should have event notifications enabled
  bucket        = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  force_destroy = "false"

  tags = {
    Name = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  }
}

resource "aws_s3_bucket_public_access_block" "audit" {
  bucket = aws_s3_bucket.audit.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "audit_acl_ownership" {
  #checkov:skip=CKV2_AWS_65: Ensure access control lists for S3 buckets are disabled
  bucket = aws_s3_bucket.audit.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "audit" {
  depends_on = [
    aws_s3_bucket_ownership_controls.audit_acl_ownership,
    aws_s3_bucket_server_side_encryption_configuration.audit,
    aws_s3_bucket_policy.audit
  ]

  bucket = aws_s3_bucket.audit.id
  acl    = "log-delivery-write"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit" {
  bucket = aws_s3_bucket.audit.bucket

  rule {
    bucket_key_enabled = false
    apply_server_side_encryption_by_default {
      #checkov:skip=CKV2_AWS_67: Ensure AWS S3 bucket encrypted with Customer Managed Key (CMK) has regular rotation #reason: key has enable_key_rotation set to true
      kms_master_key_id = aws_kms_alias.bootstrap_s3_audit_bucket_key_alias.target_key_id
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "audit" {
  bucket = aws_s3_bucket.audit.id
  versioning_configuration {
    status = "Enabled"
    #mfa_delete = "Enabled" # requires access with MFA enabled and is not possible as we work via SSO
  }
}

resource "aws_s3_bucket_policy" "audit" {
  bucket = aws_s3_bucket.audit.id
  policy = data.aws_iam_policy_document.audit.json

  depends_on = [
    aws_s3_bucket_public_access_block.audit,
  ]
}

resource "aws_s3_bucket_lifecycle_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id

  rule {
    status = "Enabled"
    id     = "abort_multipart_upload_timeout"
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }

  rule {
    id = "transfer-to-lower-storage-tiers"

    filter {
      prefix = ""
    }

    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "GLACIER"
    }
  }
}
