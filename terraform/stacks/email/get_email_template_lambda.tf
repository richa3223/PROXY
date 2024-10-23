module "get_email_template" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "get_email_template"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration
  memory_size               = var.get_email_template_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    "EMAIL_TEMPLATE_BUCKET" = module.email_template_bucket.bucket_name
  }

  depends_on = [module.email_template_bucket]
}

data "aws_iam_policy_document" "get_email_template_s3_download_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = [module.email_template_bucket.bucket_arn, "${module.email_template_bucket.bucket_arn}/*"]
  }
}

resource "aws_iam_policy" "get_email_template_s3_download_policy" {
  name        = "${local.workspace}-get_email_template_s3_download_policy"
  description = "A policy for downloading email templates from S3"
  policy      = data.aws_iam_policy_document.get_email_template_s3_download_policy_document.json
}

resource "aws_iam_role_policy_attachment" "get_email_template_s3_download_policy_attachment" {
  role       = module.get_email_template.iam_role_name
  policy_arn = aws_iam_policy.get_email_template_s3_download_policy.arn
}

data "aws_iam_policy_document" "get_email_template_kms_policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*"
    ]
    resources = [module.email_template_bucket.kms_key_arn]
  }
}

resource "aws_iam_policy" "get_email_template_kms_policy" {
  name        = "${local.workspace}-get_email_template_kms_policy"
  description = "A policy for decrypting email templates from S3"
  policy      = data.aws_iam_policy_document.get_email_template_kms_policy_document.json
}

resource "aws_iam_role_policy_attachment" "get_email_template_kms_policy_attachment" {
  role       = module.get_email_template.iam_role_name
  policy_arn = aws_iam_policy.get_email_template_kms_policy.arn
}
