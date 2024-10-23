# Proxy Step Function Cloudwatch Log Group KMS Encryption Key

resource "aws_kms_key" "proxy_step_function_cloudwatch_log_key" {
  description             = "${var.workspace} - KMS Key for Proxy Step Function Cloudwatch Logs"
  deletion_window_in_days = var.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${var.workspace} - KMS Key for Proxy Step Function Cloudwatch Logs"
  }
}

resource "aws_kms_key_policy" "proxy_step_function_cloudwatch_log_key_policy_attach" {
  key_id = aws_kms_key.proxy_step_function_cloudwatch_log_key.id
  policy = data.aws_iam_policy_document.proxy_step_function_cloudwatch_kms_policy.json
}

data "aws_iam_policy_document" "proxy_step_function_cloudwatch_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.proxy_step_function_cloudwatch_log_key.arn]
  }

  statement {
    sid    = "Allow Step Function Cloudwatch Log Group to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${var.aws_region}.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.proxy_step_function_cloudwatch_log_key.arn]
  }
}
