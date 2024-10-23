module "create_merged_email" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "create_merged_email"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration
  memory_size               = var.create_merged_email_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    "HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET" = module.hydrated_email_temporary_storage_bucket.bucket_name
  }

  depends_on = [module.email_template_bucket]
}

data "aws_iam_policy_document" "create_merged_email_s3_download_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = [module.hydrated_email_temporary_storage_bucket.bucket_arn, "${module.hydrated_email_temporary_storage_bucket.bucket_arn}/*"]
  }
}

resource "aws_iam_policy" "create_merged_email_s3_download_policy" {
  name        = "${local.workspace}-create_merged_email_s3_download_policy"
  description = "A policy for downloading email templates from S3"
  policy      = data.aws_iam_policy_document.create_merged_email_s3_download_policy_document.json
}

resource "aws_iam_role_policy_attachment" "create_merged_email_s3_download_policy_attachment" {
  role       = module.create_merged_email.iam_role_name
  policy_arn = aws_iam_policy.create_merged_email_s3_download_policy.arn
}

data "aws_iam_policy_document" "create_merged_email_kms_policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey"
    ]
    resources = [module.hydrated_email_temporary_storage_bucket.kms_key_arn]
  }
}

resource "aws_iam_policy" "create_merged_email_kms_policy" {
  name        = "${local.workspace}-create_merged_email_kms_policy"
  description = "A policy for decrypting email templates from S3"
  policy      = data.aws_iam_policy_document.create_merged_email_kms_policy_document.json
}

resource "aws_iam_role_policy_attachment" "create_merged_email_kms_policy_attachment" {
  role       = module.create_merged_email.iam_role_name
  policy_arn = aws_iam_policy.create_merged_email_kms_policy.arn
}
