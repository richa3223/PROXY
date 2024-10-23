# Send NHS Mail Credentials Secrets Manager KMS Encryption Key
resource "aws_kms_key" "send_gp_email__send_nhs_mail_credentials_secrets_manager_key" {
  description             = "${local.workspace} - KMS Key for Send GP Email - Send NHS Mail Credentials Secrets Manager"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Send GP Email - Send NHS Mail Credentials Secrets Manager"
  }
}

resource "aws_kms_key_policy" "send_gp_email__send_nhs_mail_credentials_secrets_manager_key_policy_attach" {
  key_id = aws_kms_key.send_gp_email__send_nhs_mail_credentials_secrets_manager_key.id
  policy = data.aws_iam_policy_document.send_gp_email__send_nhs_mail_credentials_secrets_manager_kms_policy.json
}

data "aws_iam_policy_document" "send_gp_email__send_nhs_mail_credentials_secrets_manager_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.send_gp_email__send_nhs_mail_credentials_secrets_manager_key.arn]
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
    resources = [aws_kms_key.send_gp_email__send_nhs_mail_credentials_secrets_manager_key.arn]
  }
}


# ODS lookup credentials secrets manager KMS encryption key
resource "aws_kms_key" "ods_lookup_credentials_secrets_manager_key" {
  description             = "${local.workspace} - KMS Key for ODS lookup Credentials Secrets Manager"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for ODS lookup Credentials Secrets Manager"
  }
}

resource "aws_kms_key_policy" "ods_lookup_credentials_secrets_manager_key_policy_attach" {
  key_id = aws_kms_key.ods_lookup_credentials_secrets_manager_key.id
  policy = data.aws_iam_policy_document.ods_lookup_credentials_secrets_manager_kms_policy.json
}

data "aws_iam_policy_document" "ods_lookup_credentials_secrets_manager_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.ods_lookup_credentials_secrets_manager_key.arn]
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
    resources = [aws_kms_key.ods_lookup_credentials_secrets_manager_key.arn]
  }
}
