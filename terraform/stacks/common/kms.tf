resource "aws_kms_key" "cloudwatch_log_key" {
  description             = "KMS Key for Cloudwatch Logs"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true
}

resource "aws_kms_key_policy" "cloudwatch_log_key_policy_attachment" {
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
    sid    = "CloudWatchKMSAccess"
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

resource "aws_kms_alias" "cloudwatch_logs_key_alias" {
  name          = "alias/${local.workspace}-${var.project}-cloudwatch-log-key"
  target_key_id = aws_kms_key.cloudwatch_log_key.key_id
}

resource "aws_kms_key" "sqs_key" {
  description             = "${local.workspace} - KMS Key for SQS"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for SQS"
  }
}

resource "aws_kms_alias" "sqs_key_alias" {
  name          = "alias/${local.workspace}-${var.project}-sqs-key"
  target_key_id = aws_kms_key.sqs_key.key_id
}

resource "aws_kms_key_policy" "sqs_key_policy_attachment" {
  key_id = aws_kms_key.sqs_key.id
  policy = data.aws_iam_policy_document.sqs_kms_policy.json
}

data "aws_iam_policy_document" "sqs_kms_policy" {
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
    resources = [aws_kms_key.sqs_key.arn]
  }
  statement {
    sid    = "LogsKMSAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${var.region}.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.sqs_key.arn]
  }

  statement {
    sid    = "EventBridgeKMSAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*"
    ]
    resources = [aws_kms_key.sqs_key.arn]
  }
}

resource "aws_kms_key" "dynamodb_key" {
  description             = "${local.workspace} - KMS Key for DynamoDB"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for DynamoDB"
  }
}

resource "aws_kms_alias" "dynamodb_key_alias" {
  name          = "alias/${local.workspace}-${var.project}-dynamodb-key"
  target_key_id = aws_kms_key.dynamodb_key.key_id
}

resource "aws_kms_key_policy" "dynamodb_key_policy_attachment" {
  key_id = aws_kms_key.dynamodb_key.id
  policy = data.aws_iam_policy_document.dynamodb_kms_policy.json
}

data "aws_iam_policy_document" "dynamodb_kms_policy" {
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*"
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.dynamodb_key.arn]
  }
  statement {
    sid    = "DynamoDBKMSAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["dynamodb.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.dynamodb_key.arn]
  }
  statement {
    sid    = "EventBridgePipeKMSAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["pipes.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.dynamodb_key.arn]
  }

}
