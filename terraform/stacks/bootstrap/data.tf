# General Data Sources
data "aws_caller_identity" "current" {}
data "aws_iam_account_alias" "current" {}

# StateFile bucket policy
data "aws_iam_policy_document" "statefile" {
  statement {
    sid    = "DontAllowNonSecureConnection"
    effect = "Deny"

    actions = [
      "s3:*",
    ]

    resources = [
      aws_s3_bucket.statefile.arn,
      "${aws_s3_bucket.statefile.arn}/*",
    ]

    principals {
      type = "AWS"

      identifiers = [
        "*",
      ]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"

      values = [
        "false",
      ]
    }
  }

  statement {
    sid    = "AllowLocalAccountsToList"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.statefile.arn,
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }

  statement {
    sid    = "AllowManagedAccountsToGet"
    effect = "Allow"

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${aws_s3_bucket.statefile.arn}/*",
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }
}

data "aws_iam_policy_document" "audit" {
  statement {
    sid     = "DenyInsecureCommunications"
    actions = ["s3:*"]
    effect  = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.audit.id}",
      "arn:aws:s3:::${aws_s3_bucket.audit.id}/*",
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}
