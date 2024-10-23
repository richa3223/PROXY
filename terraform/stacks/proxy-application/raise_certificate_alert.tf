module "raise_certificate_alert" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "raise_certificate_alert"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration
  memory_size               = var.raise_certificate_alert_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    MTLS_CERTIFICATE_BUCKET_NAME      = module.mutual_tls_truststore_bucket.bucket_name
    SEND_NHS_MAIL_API_CREDENTIALS     = aws_secretsmanager_secret.raise_certificate_alert__send_nhs_mail_credentials.arn
    SLACK_ALERTS_LAMBDA_FUNCTION_NAME = module.slack_alerts.function_name
    ENVIRONMENT                       = var.environment
    WORKSPACE                         = terraform.workspace
    TEAM_EMAIL                        = var.TEAM_EMAIL
  }
}

resource "aws_lambda_permission" "allow_eventbridge_to_invoke_raise_certificate_alert_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.raise_certificate_alert.function_name
  principal     = "events.amazonaws.com"
  source_arn    = module.default_eventbridge.eventbridge_rule_arns["${local.workspace}-daily_check_certificate_expiry"]
}


data "aws_iam_policy_document" "raise_certificate_alert_policy_document" {
  statement {
    sid     = "AllowSecretsAccess"
    effect  = "Allow"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.raise_certificate_alert__send_nhs_mail_credentials.arn
    ]
  }
  statement {
    sid    = "AllowKMSAccess" # KMS access for decrypting secrets
    effect = "Allow"
    actions = [
      "kms:Decrypt*",
      "kms:Describe*"
    ]
    resources = [
      aws_kms_key.raise_certificate_alert__send_nhs_mail_credentials_secrets_manager_key.arn,
      module.mutual_tls_truststore_bucket.kms_key_arn
    ]
  }
  statement {
    sid       = "AllowLambdaAccess"
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [module.slack_alerts.arn]
  }
  statement {
    sid     = "AllowS3ListAccess"
    effect  = "Allow"
    actions = ["s3:ListBucket", "s3:GetObject"]
    resources = [
      module.mutual_tls_truststore_bucket.bucket_arn,
      "${module.mutual_tls_truststore_bucket.bucket_arn}/*"
    ]
  }
}

resource "aws_iam_policy" "raise_certificate_alert_policy" {
  name   = "${local.workspace}-raise_certificate_alert_policy"
  policy = data.aws_iam_policy_document.raise_certificate_alert_policy_document.json
}

resource "aws_iam_role_policy_attachment" "raise_certificate_alert_policy_attachment" {
  role       = module.raise_certificate_alert.iam_role_name
  policy_arn = aws_iam_policy.raise_certificate_alert_policy.arn
}
