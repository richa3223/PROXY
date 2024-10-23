module "sensitive_audit_kinesis_firehose" {
  source                          = "../../modules/kinesis_firehose"
  firehose_name                   = "${local.workspace}-sensitive-audit-kinesis-firehose"
  firehose_destination            = "extended_s3"
  aws_region                      = local.aws_region
  kms_key_deletion_window_in_days = local.kms_key_deletion_duration
  bucket_arn                      = local.sensitive_audit_kinesis_firehose_destination.bucket_arn
  bucket_kms_key_arn              = local.sensitive_audit_kinesis_firehose_destination.kms_key_arn
  prefix                          = local.audit_bucket_prefix
  dynamic_partitioning_enabled    = true
  log_retention_in_days           = local.firehose_log_retention_in_days
  environment                     = var.environment
  workspace                       = local.workspace
  lambda_processor_arn            = var.legal_direction ? "" : module.redact_sensitive_data.arn # Only remove the lambda processor if the legal direction is always true
  depends_on                      = [module.redact_sensitive_data]
}

module "standard_audit_kinesis_firehose" {
  source                          = "../../modules/kinesis_firehose"
  firehose_name                   = "${local.workspace}-standard-audit-kinesis-firehose"
  firehose_destination            = "extended_s3"
  aws_region                      = local.aws_region
  kms_key_deletion_window_in_days = local.kms_key_deletion_duration
  bucket_arn                      = local.standard_audit_kinesis_firehose_destination.bucket_arn
  bucket_kms_key_arn              = local.standard_audit_kinesis_firehose_destination.kms_key_arn
  prefix                          = local.audit_bucket_prefix
  dynamic_partitioning_enabled    = true
  log_retention_in_days           = local.firehose_log_retention_in_days
  environment                     = var.environment
  workspace                       = local.workspace
  lambda_processor_arn            = module.redact_sensitive_data.arn
  depends_on                      = [module.redact_sensitive_data]
}


data "aws_iam_policy_document" "firehose_lambda_policy_document" {
  statement {
    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      module.redact_sensitive_data.arn
    ]
    effect = "Allow"
  }
}

resource "aws_iam_policy" "firehose_lambda_policy" {
  name   = "${module.standard_audit_kinesis_firehose.firehose_name}-lambda-policy"
  policy = data.aws_iam_policy_document.firehose_lambda_policy_document.json
}

resource "aws_iam_role_policy_attachment" "standard_audit_firehose_lambda_execution_role_attachment" {
  role       = module.standard_audit_kinesis_firehose.iam_role_name
  policy_arn = aws_iam_policy.firehose_lambda_policy.arn
}

resource "aws_iam_role_policy_attachment" "sensitive_audit_firehose_lambda_execution_role_attachment" {
  count      = var.legal_direction ? 0 : 1
  role       = module.sensitive_audit_kinesis_firehose.iam_role_name
  policy_arn = aws_iam_policy.firehose_lambda_policy.arn
}
