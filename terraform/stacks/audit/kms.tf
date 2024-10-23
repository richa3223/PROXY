# Proxy Sensitive Audit Athena S3 Bucket KMS Encryption Key

resource "aws_kms_key" "athena_sensitive_s3_bucket_key" {
  description             = "${local.workspace} - KMS Key for Sensitive S3 Athena Bucket"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Sensitive S3 Athena Bucket"
  }
}

resource "aws_kms_key_policy" "athena_sensitive_s3_bucket_key_policy_attach" {
  key_id = aws_kms_key.athena_sensitive_s3_bucket_key.id
  policy = data.aws_iam_policy_document.athena_sensitive_s3_bucket_kms_policy.json
}

data "aws_iam_policy_document" "athena_sensitive_s3_bucket_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.athena_sensitive_s3_bucket_key.arn]
  }

  statement {
    sid    = "Allow Athena Sensitive S3 Service to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.athena_sensitive_s3_bucket_key.arn]
  }
}

# Proxy Standard Audit Athena S3 Bucket KMS Encryption Key

resource "aws_kms_key" "athena_standard_s3_bucket_key" {
  description             = "${local.workspace} - KMS Key for Standard S3 Athena Bucket"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Standard S3 Athena Bucket"
  }
}

resource "aws_kms_key_policy" "athena_standard_s3_bucket_key_policy_attach" {
  key_id = aws_kms_key.athena_standard_s3_bucket_key.id
  policy = data.aws_iam_policy_document.athena_standard_s3_bucket_kms_policy.json
}

data "aws_iam_policy_document" "athena_standard_s3_bucket_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.athena_standard_s3_bucket_key.arn]
  }

  statement {
    sid    = "Allow Athena Standard S3 Service to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.athena_standard_s3_bucket_key.arn]
  }
}