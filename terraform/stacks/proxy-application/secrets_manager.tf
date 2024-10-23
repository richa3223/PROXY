resource "random_string" "random" {
  length  = 16
  special = false
}

resource "aws_secretsmanager_secret" "pds_credentials" {
  #checkov:skip=CKV2_AWS_57: Ensure Secrets Manager secrets should have automatic rotation enabled
  name       = "/${local.workspace}/pds-credentials-${random_string.random.result}"
  kms_key_id = aws_kms_key.pds_credentials_secrets_manager_key.arn

  depends_on = [
    aws_kms_key.pds_credentials_secrets_manager_key,
    aws_kms_key_policy.pds_credentials_secrets_manager_key_policy_attach
  ]
}

resource "aws_secretsmanager_secret_version" "pds_credentials" {
  secret_id     = aws_secretsmanager_secret.pds_credentials.id
  secret_string = var.PDS_CREDENTIALS
}

resource "aws_secretsmanager_secret" "raise_certificate_alert__send_nhs_mail_credentials" {
  #checkov:skip=CKV2_AWS_57: Ensure Secrets Manager secrets should have automatic rotation enabled
  name       = "/${local.workspace}/raise-certificate-alert-send-nhs-mail-credentials-${random_string.random.result}"
  kms_key_id = aws_kms_key.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key.arn

  depends_on = [
    aws_kms_key.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key,
    aws_kms_key_policy.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key_policy_attach
  ]
}

resource "aws_secretsmanager_secret_version" "raise_certificate_alert__send_nhs_mail_credentials" {
  secret_id     = aws_secretsmanager_secret.raise_certificate_alert__send_nhs_mail_credentials.id
  secret_string = var.SEND_NHS_MAIL_CREDENTIALS
}
