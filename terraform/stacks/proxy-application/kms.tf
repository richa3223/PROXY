# Proxy API Logging Cloudwatch Log Group KMS Encryption Key

resource "aws_kms_key" "proxy_api_logging_cloudwatch_log_key" {
  description             = "${local.workspace} - KMS Key for Proxy API Logging Cloudwatch Logs"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Proxy API Logging Cloudwatch Logs"
  }
}

resource "aws_kms_key_policy" "proxy_api_logging_cloudwatch_log_key_policy_attach" {
  key_id = aws_kms_key.proxy_api_logging_cloudwatch_log_key.id
  policy = data.aws_iam_policy_document.proxy_api_logging_cloudwatch_kms_policy.json
}

data "aws_iam_policy_document" "proxy_api_logging_cloudwatch_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.proxy_api_logging_cloudwatch_log_key.arn]
  }

  statement {
    sid    = "Allow API Logging Cloudwatch Log Group to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${local.aws_region}.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.proxy_api_logging_cloudwatch_log_key.arn]
  }
}


# PDS Credentials Secrets Manager KMS Encryption Key
resource "aws_kms_key" "pds_credentials_secrets_manager_key" {
  description             = "${local.workspace} - KMS Key for PDS Credentials Secrets Manager"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for PDS Credentials Secrets Manager"
  }
}

resource "aws_kms_key_policy" "pds_credentials_secrets_manager_key_policy_attach" {
  key_id = aws_kms_key.pds_credentials_secrets_manager_key.id
  policy = data.aws_iam_policy_document.pds_credentials_secrets_manager_kms_policy.json
}

data "aws_iam_policy_document" "pds_credentials_secrets_manager_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.pds_credentials_secrets_manager_key.arn]
  }

  statement {
    sid    = "Allow Secrets Manager to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["secretsmanager.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.pds_credentials_secrets_manager_key.arn]
  }
}

# Send NHS Mail Credentials Secrets Manager KMS Encryption Key
resource "aws_kms_key" "raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key" {
  description             = "${local.workspace} - KMS Key for Send GP Email - Send NHS Mail Credentials Secrets Manager"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Send GP Email - Send NHS Mail Credentials Secrets Manager"
  }
}

resource "aws_kms_key_policy" "raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key_policy_attach" {
  key_id = aws_kms_key.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key.id
  policy = data.aws_iam_policy_document.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_kms_policy.json
}

data "aws_iam_policy_document" "raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key.arn]
  }

  statement {
    sid    = "Allow Secrets Manager to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["secretsmanager.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key.arn]
  }
}

# Slack Alerts Webhook Secrets Manager KMS Encryption Key
resource "aws_kms_key" "slack_webhook_secrets_manager_key" {
  description             = "KMS key for secrets manager"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Slack Alerts Credentials Secrets Manager"
  }
}

resource "aws_kms_key_policy" "slack_webhook_secrets_manager_key_policy_attach" {
  key_id = aws_kms_key.slack_webhook_secrets_manager_key.id
  policy = data.aws_iam_policy_document.slack_webhook_secrets_manager_kms_policy.json
}

data "aws_iam_policy_document" "slack_webhook_secrets_manager_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.slack_webhook_secrets_manager_key.arn]
  }

  statement {
    sid    = "Allow Secrets Manager to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["secretsmanager.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.slack_webhook_secrets_manager_key.arn]
  }
}
