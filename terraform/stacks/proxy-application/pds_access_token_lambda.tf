module "pds_access_token" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "pds_access_token"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = 14
  memory_size               = var.pds_access_token_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    REGION          = local.aws_region
    PDS_CREDENTIALS = aws_secretsmanager_secret.pds_credentials.name
    PDS_AUTH_URL    = var.pds_auth_url
  }
}

data "aws_iam_policy_document" "pds_access_token_policy_document" {
  statement {
    sid     = "AllowSecretsAccess"
    effect  = "Allow"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.pds_credentials.arn
    ]
  }
  statement {
    sid    = "AllowKMSAccess" # KMS access for decrypting secrets
    effect = "Allow"
    actions = [
      "kms:Decrypt*",
      "kms:Describe*"
    ]
    resources = [aws_kms_key.pds_credentials_secrets_manager_key.arn]
  }
}

resource "aws_iam_policy" "pds_access_token_policy" {
  name   = "${local.workspace}-pds_access_token_policy"
  policy = data.aws_iam_policy_document.pds_access_token_policy_document.json
}

resource "aws_iam_role_policy_attachment" "pds_access_token_policy_attachment" {
  role       = module.pds_access_token.iam_role_name
  policy_arn = aws_iam_policy.pds_access_token_policy.arn
}
