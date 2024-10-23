# Proxy Bootstrap S3 Audit Bucket KMS Encryption Key

resource "aws_kms_key" "bootstrap_s3_audit_bucket_key" {
  #checkov:skip=CKV2_AWS_64: Ensure KMS key Policy is defined
  description             = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-audit"
  deletion_window_in_days = 14
  enable_key_rotation     = true

  tags = {
    Name = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-audit"
  }
}

resource "aws_kms_key_policy" "bootstrap_s3_audit_bucket_key_policy_attach" {
  key_id = aws_kms_key.bootstrap_s3_audit_bucket_key.id
  policy = data.aws_iam_policy_document.bootstrap_s3_audit_bucket_kms_policy.json
}

resource "aws_kms_alias" "bootstrap_s3_audit_bucket_key_alias" {
  name          = "alias/${var.project}-${data.aws_iam_account_alias.current.account_alias}-audit"
  target_key_id = aws_kms_key.bootstrap_s3_audit_bucket_key.key_id
}

data "aws_iam_policy_document" "bootstrap_s3_audit_bucket_kms_policy" {
  statement {
    sid    = "Allow Bootstrap Audit S3 Service to use the KMS key"
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
    resources = [aws_kms_key.bootstrap_s3_audit_bucket_key.arn]
  }
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]

    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.bootstrap_s3_audit_bucket_key.arn]
  }
}

# Proxy Bootstrap S3 Statefile Bucket KMS Encryption Key

resource "aws_kms_key" "bootstrap_s3_statefile_bucket_key" {
  #checkov:skip=CKV2_AWS_64: Ensure KMS key Policy is defined
  description             = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-statefile"
  deletion_window_in_days = 14
  enable_key_rotation     = true

  tags = {
    Name = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-statefile"
  }
}

resource "aws_kms_key_policy" "bootstrap_s3_statefile_bucket_key_policy_attach" {
  key_id = aws_kms_key.bootstrap_s3_statefile_bucket_key.id
  policy = data.aws_iam_policy_document.bootstrap_s3_statefile_bucket_kms_policy.json
}

resource "aws_kms_alias" "bootstrap_s3_statefile_bucket_key_alias" {
  name          = "alias/${var.project}-${data.aws_iam_account_alias.current.account_alias}-statefile"
  target_key_id = aws_kms_key.bootstrap_s3_statefile_bucket_key.key_id
}

data "aws_iam_policy_document" "bootstrap_s3_statefile_bucket_kms_policy" {
  statement {
    sid    = "Allow Bootstrap Statefile S3 Service to use the KMS key"
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
    resources = [aws_kms_key.bootstrap_s3_statefile_bucket_key.arn]
  }
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]

    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.bootstrap_s3_statefile_bucket_key.arn]
  }
}

# DynamoDB KMS Key
resource "aws_kms_key" "dynamodb_kms_key" {
  description             = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-dynamodb"
  deletion_window_in_days = 14
  enable_key_rotation     = true

  tags = {
    Name = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-dynamodb"
  }
}

# DynamoDB KMS Key Policy
resource "aws_kms_key_policy" "dynamodb_kms_key_policy" {
  key_id = aws_kms_key.dynamodb_kms_key.id
  policy = data.aws_iam_policy_document.dynamodb_kms_policy.json
}

# DynamoDB KMS Key Alias
resource "aws_kms_alias" "dynamodb_kms_key_alias" {
  name          = "alias/${var.project}-${data.aws_iam_account_alias.current.account_alias}-dynamodb"
  target_key_id = aws_kms_key.dynamodb_kms_key.key_id
}

# DynamoDB KMS Key Policy Document
data "aws_iam_policy_document" "dynamodb_kms_policy" {
  statement {
    sid    = "Allow DynamoDB to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["dynamodb.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.dynamodb_kms_key.arn]
  }

  statement {
    sid    = "Enable IAM Root User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.dynamodb_kms_key.arn]
  }
}
