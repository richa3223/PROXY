resource "random_string" "random" {
  length  = 16
  special = false
}

resource "aws_secretsmanager_secret" "send_gp_email__send_nhs_mail_credentials" {
  #checkov:skip=CKV2_AWS_57: Ensure Secrets Manager secrets should have automatic rotation enabled
  name       = "/${local.workspace}/send-gp-email-send-nhs-mail-credentials-${random_string.random.result}"
  kms_key_id = aws_kms_key.send_gp_email__send_nhs_mail_credentials_secrets_manager_key.arn

  depends_on = [
    aws_kms_key.send_gp_email__send_nhs_mail_credentials_secrets_manager_key,
    aws_kms_key_policy.send_gp_email__send_nhs_mail_credentials_secrets_manager_key_policy_attach
  ]
}

resource "aws_secretsmanager_secret_version" "send_gp_email__send_nhs_mail_credentials" {
  secret_id     = aws_secretsmanager_secret.send_gp_email__send_nhs_mail_credentials.id
  secret_string = var.SEND_NHS_MAIL_CREDENTIALS
}

resource "aws_secretsmanager_secret" "ods_lookup_credentials" {
  #checkov:skip=CKV2_AWS_57: Ensure Secrets Manager secrets should have automatic rotation enabled
  name       = "/${local.workspace}/ods-lookup-credentials-${random_string.random.result}"
  kms_key_id = aws_kms_key.ods_lookup_credentials_secrets_manager_key.arn

  depends_on = [
    aws_kms_key.ods_lookup_credentials_secrets_manager_key,
    aws_kms_key_policy.ods_lookup_credentials_secrets_manager_key_policy_attach
  ]
}

resource "aws_secretsmanager_secret_version" "ods_lookup_credentials" {
  secret_id     = aws_secretsmanager_secret.ods_lookup_credentials.id
  secret_string = var.ODS_LOOKUP_CREDENTIALS
}
