data "aws_iam_policy_document" "firehose_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "firehose_policy_document" {
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
      "${var.bucket_arn}/*",
    ]

    effect = "Allow"
  }

  statement {
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.firehose_key.arn, var.bucket_kms_key_arn]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "firehose_iam_policy" {
  name   = "${var.firehose_name}-policy"
  policy = data.aws_iam_policy_document.firehose_policy_document.json
}

resource "aws_iam_role_policy_attachment" "firehose_role_attachment" {
  role       = aws_iam_role.firehose_iam_role.name
  policy_arn = aws_iam_policy.firehose_iam_policy.arn
}

resource "aws_iam_role" "firehose_iam_role" {
  name               = "${var.firehose_name}-iam-role"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume_role.json
}
