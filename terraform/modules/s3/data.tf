data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    sid     = "DenyInsecureCommunications"
    actions = ["s3:*"]
    effect  = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.bucket.id}",
      "arn:aws:s3:::${aws_s3_bucket.bucket.id}/*",
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
    condition {
      test     = "StringNotEquals"
      variable = "aws:sourceVpce"
      values   = [var.vpc_endpoint_id]
    }
  }
}