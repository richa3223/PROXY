data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "glue_assume_role_policy_document" {

  statement {
    sid     = "AllowGlueToAssumeRole"
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "glue_log_access_policy_document" {
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  statement {
    sid = "AllowGlueToLogToCloudWatch"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:CreateLogGroup",
      "logs:AssociateKmsKey",
    ]
    resources = [
      "arn:aws:logs:*:*:log-group:/aws-glue/crawlers:*",
      "arn:aws:logs:*:*:log-group:/aws-glue/crawlers-role/*:*"
    ]
    effect = "Allow"
  }

  statement {
    sid       = "GluePushMetricsToCloudWatch"
    actions   = ["cloudwatch:PutMetricData"]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.glue_key.arn]
    effect    = "Allow"
  }
}

data "aws_iam_policy_document" "glue_resource_access_policy_document" {
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    resources = [
      var.bucket_arn,
      "${var.bucket_arn}/*"
    ]
    effect = "Allow"
  }

  statement {
    actions = ["glue:*"]
    resources = [
      "arn:aws:glue:*:*:catalog",
      "arn:aws:glue:*:*:database/*",
      "arn:aws:glue:*:*:table/*/*",
      "arn:aws:glue:*:*:crawler/*"
    ]
    effect = "Allow"
  }
  statement {
    actions = [
      "glue:GetSecurityConfiguration",
      "glue:GetSecurityConfigurations",
    ]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.glue_key.arn, var.bucket_kms_key_arn]
    effect    = "Allow"
  }
}
