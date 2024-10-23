# Firehose KMS Encryption Key
resource "aws_kms_key" "firehose_key" {
  description             = "${local.workspace} - KMS Key for Firehose"
  deletion_window_in_days = 14
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Firehose"
  }
}

resource "aws_kms_alias" "firehose_key" {
  name          = "alias/${local.workspace}-firehose-key"
  target_key_id = aws_kms_key.firehose_key.key_id
}

resource "aws_kms_key_policy" "firehose_key_policy_attachment" {
  key_id = aws_kms_key.firehose_key.id
  policy = data.aws_iam_policy_document.firehose_kms_policy.json
}

data "aws_iam_policy_document" "firehose_kms_policy" {
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.firehose_key.arn]
  }
  statement {
    sid    = "LogsKMSAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${var.region}.amazonaws.com", "firehose.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.firehose_key.arn]
  }
}

# Cloudwatch Log Group KMS Encryption Key
resource "aws_kms_key" "cloudwatch_log_key" {
  description             = "${local.workspace} - KMS Key for Cloudwatch Logs"
  deletion_window_in_days = 14
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Cloudwatch Logs"
  }
}

resource "aws_kms_alias" "cloudwatch_log_key" {
  name          = "alias/${local.workspace}-firehose-cloudwatch-log-key"
  target_key_id = aws_kms_key.cloudwatch_log_key.key_id
}

resource "aws_kms_key_policy" "cloudwatch_kms_policy_attachment" {
  key_id = aws_kms_key.cloudwatch_log_key.id
  policy = data.aws_iam_policy_document.cloudwatch_kms_policy.json
}

data "aws_iam_policy_document" "cloudwatch_kms_policy" {
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.cloudwatch_log_key.arn]
  }
  statement {
    sid    = "KMSAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${var.region}.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.cloudwatch_log_key.arn]
  }
}
