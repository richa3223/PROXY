resource "aws_kms_key" "s3_bucket_key" {
  description             = "${var.workspace} - KMS Key for S3 Bucket"
  deletion_window_in_days = 14
  enable_key_rotation     = true

  tags = {
    "Description" = "${var.workspace} - ${var.bucket_name} - KMS Key for S3 Bucket"
  }
}

resource "aws_kms_key_policy" "s3_bucket_key_policy_attach" {
  key_id = aws_kms_key.s3_bucket_key.id
  policy = data.aws_iam_policy_document.s3_bucket_kms_policy.json
}

data "aws_iam_policy_document" "s3_bucket_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.s3_bucket_key.arn]
  }

  statement {
    sid    = "Allow S3 Service to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.s3_bucket_key.arn]
  }
}
