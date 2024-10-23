module "ods_lookup" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "ods_lookup"
  aws_region           = local.aws_region
  workspace            = local.workspace

  kms_key_deletion_duration = 14
  memory_size               = var.ods_lookup_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    ODS_LOOKUP_BASE_URL    = var.ods_lookup_base_url
    REGION                 = local.aws_region
    ODS_LOOKUP_CREDENTIALS = aws_secretsmanager_secret.ods_lookup_credentials.name
    ENVIRONMENT            = var.environment
  }
}

data "aws_iam_policy_document" "ods_lookup_policy_document" {
  statement {
    sid     = "AllowSecretsAccess"
    effect  = "Allow"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.ods_lookup_credentials.arn
    ]
  }
  statement {
    sid    = "AllowKMSAccess" # KMS access for decrypting secrets
    effect = "Allow"
    actions = [
      "kms:Decrypt*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.ods_lookup_credentials_secrets_manager_key.arn]
  }
}

resource "aws_iam_policy" "ods_lookup_policy" {
  name   = "${local.workspace}-ods_lookup_policy"
  policy = data.aws_iam_policy_document.ods_lookup_policy_document.json
}

resource "aws_iam_role_policy_attachment" "ods_lookup_policy_attachment" {
  role       = module.ods_lookup.iam_role_name
  policy_arn = aws_iam_policy.ods_lookup_policy.arn
}
