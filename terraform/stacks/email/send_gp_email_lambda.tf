module "send_gp_email" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "send_gp_email"
  aws_region           = local.aws_region
  workspace            = local.workspace

  environment_variables = {
    SEND_NHS_MAIL_API_CREDENTIALS = aws_secretsmanager_secret.send_gp_email__send_nhs_mail_credentials.arn,
    DYNAMODB_TABLE_NAME           = data.aws_dynamodb_table.patient_relationship.name,
    HYDRATED_EMAIL_BUCKET         = module.hydrated_email_temporary_storage_bucket.bucket_name
  }

  kms_key_deletion_duration = 14
  memory_size               = var.send_gp_email_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids
}

data "aws_iam_policy_document" "send_gp_email_policy_document" {
  statement {
    sid     = "AllowSecretsAccess"
    effect  = "Allow"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.send_gp_email__send_nhs_mail_credentials.arn
    ]
  }
  statement {
    sid    = "AllowKMSAccess" # KMS access for decrypting secrets
    effect = "Allow"
    actions = [
      "kms:Decrypt*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.send_gp_email__send_nhs_mail_credentials_secrets_manager_key.arn]
  }
}

resource "aws_iam_policy" "send_gp_email_policy" {
  name   = "${local.workspace}-send_gp_email_policy"
  policy = data.aws_iam_policy_document.send_gp_email_policy_document.json
}

resource "aws_iam_role_policy_attachment" "send_gp_email_policy_attachment" {
  role       = module.send_gp_email.iam_role_name
  policy_arn = aws_iam_policy.send_gp_email_policy.arn
}

resource "aws_lambda_permission" "allow_eventbridge_to_invoke_send_gp_email_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.send_gp_email.function_name
  principal     = "events.amazonaws.com"
  source_arn    = module.eventbridge.eventbridge_rule_arns["${local.workspace}-send_gp_email"]
}

data "aws_iam_policy_document" "send_gp_email_s3_download_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = [module.hydrated_email_temporary_storage_bucket.bucket_arn, "${module.hydrated_email_temporary_storage_bucket.bucket_arn}/*"]
  }
}

resource "aws_iam_policy" "send_gp_email_s3_download_policy" {
  name        = "${local.workspace}-send_gp_email_s3_download_policy"
  description = "A policy for downloading email templates from S3"
  policy      = data.aws_iam_policy_document.send_gp_email_s3_download_policy_document.json
}

resource "aws_iam_role_policy_attachment" "send_gp_email_s3_download_policy_attachment" {
  role       = module.send_gp_email.iam_role_name
  policy_arn = aws_iam_policy.send_gp_email_s3_download_policy.arn
}

data "aws_iam_policy_document" "send_gp_email_dynamodb_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
    ]
    resources = [data.aws_dynamodb_table.patient_relationship.arn]
  }
}

resource "aws_iam_policy" "send_gp_email_dynamodb_policy" {
  name        = "${local.workspace}-send-gp-email-dynamodb-permissions"
  description = "A policy for putting and updating items in the patient relationship table"
  policy      = data.aws_iam_policy_document.send_gp_email_dynamodb_policy_document.json
}

resource "aws_iam_role_policy_attachment" "send_gp_email_dynamodb_attachment" {
  role       = module.send_gp_email.iam_role_name
  policy_arn = aws_iam_policy.send_gp_email_dynamodb_policy.arn
}

data "aws_iam_policy_document" "send_gp_email_kms_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
    ]
    resources = [data.aws_kms_key.dynamodb_kms_key.arn, module.hydrated_email_temporary_storage_bucket.kms_key_arn]
  }
}

resource "aws_iam_policy" "send_gp_email_kms_policy" {
  name        = "${local.workspace}-${module.send_gp_email.function_name}-kms-permissions"
  description = "A policy for decrypting data keys for the send gp email lambda"
  policy      = data.aws_iam_policy_document.send_gp_email_kms_policy_document.json
}

resource "aws_iam_role_policy_attachment" "send_gp_email_kms_attachment" {
  role       = module.send_gp_email.iam_role_name
  policy_arn = aws_iam_policy.send_gp_email_kms_policy.arn
}
