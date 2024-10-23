data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
# endpoint policy for S3
# ref: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-endpoints-access.html
data "aws_iam_policy_document" "s3_iam_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = var.allowed_s3_actions
    resources = var.allowed_s3_buckets
  }
}
