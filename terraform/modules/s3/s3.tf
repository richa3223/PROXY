resource "aws_s3_bucket" "bucket" {
  #checkov:skip=CKV2_AWS_62: Ensure S3 buckets should have event notifications enabled #reason: No reason to have this enabled when we are not using event notifications for all buckets, safe to skip.
  #checkov:skip=CKV_AWS_144: Ensure that S3 bucket has cross-region replication enabled
  #checkov:skip=CKV_AWS_21: Ensure all data stored in the S3 bucket have versioning enabled
  bucket        = var.bucket_name
  force_destroy = var.force_destroy
  tags          = var.tags
}

resource "aws_s3_bucket_public_access_block" "bucket" {
  bucket                  = aws_s3_bucket.bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership" {
  bucket = aws_s3_bucket.bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bucket" {
  bucket = aws_s3_bucket.bucket.bucket

  rule {
    bucket_key_enabled = false
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_bucket_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "bucket" {
  bucket = aws_s3_bucket.bucket.id

  versioning_configuration {
    status = var.enable_bucket_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_policy" "ssl_enforced_bucket" {
  bucket = aws_s3_bucket.bucket.id
  policy = coalesce(
    var.s3_iam_policy_document,
    data.aws_iam_policy_document.bucket_policy.json
  )
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle_configuration" {
  bucket = aws_s3_bucket.bucket.id
  rule {
    status = "Enabled"
    id     = "retention_period_rule"
    expiration {
      days = var.retention_days
    }
  }
  rule {
    status = "Enabled"
    id     = "abort_multipart_upload_timeout"
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

resource "aws_s3_bucket_logging" "bucket" {
  bucket = aws_s3_bucket.bucket.id

  target_bucket = var.audit_bucket_id
  target_prefix = "log/${aws_s3_bucket.bucket.id}"
}
