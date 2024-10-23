# Sensitive Audit Workflow #
resource "aws_glue_catalog_database" "sensitive_catalog_database" {
  name = "${local.workspace}-sensitive-data-catalogue"
}

module "sensitive_glue_crawler" {
  source = "../../modules/glue_crawler"

  crawler_name       = "${local.workspace}-sensitive_data_glue_crawler"
  database_name      = aws_glue_catalog_database.sensitive_catalog_database.name
  table_prefix       = "${local.workspace}_audit_"
  bucket_arn         = local.sensitive_audit_kinesis_firehose_destination.bucket_arn
  bucket_name        = local.sensitive_audit_kinesis_firehose_destination.bucket_name
  bucket_kms_key_arn = local.sensitive_audit_kinesis_firehose_destination.kms_key_arn
  environment        = var.environment
  workspace          = local.workspace
}

resource "aws_s3_bucket_notification" "start_sensitive_crawler_on_event_notification" {
  bucket = local.sensitive_audit_kinesis_firehose_destination.bucket_name

  lambda_function {
    lambda_function_arn = module.start_sensitive_audit_data_crawler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = "/"
  }
  depends_on = [aws_lambda_permission.allow_sensitive_bucket_to_call_lambda]
}

resource "aws_lambda_permission" "allow_sensitive_bucket_to_call_lambda" {
  statement_id  = "AllowSensitiveExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.start_sensitive_audit_data_crawler.arn
  principal     = "s3.amazonaws.com"
  source_arn    = local.sensitive_audit_kinesis_firehose_destination.bucket_arn
}


# Standard Audit Workflow #
resource "aws_glue_catalog_database" "queryable_catalog_database" {
  name = "${local.workspace}-queryable-data-catalogue"
}

module "standard_glue_crawler" {
  source = "../../modules/glue_crawler"

  crawler_name       = "${local.workspace}-queryable_data_glue_crawler"
  database_name      = aws_glue_catalog_database.queryable_catalog_database.name
  table_prefix       = "${local.workspace}_audit_"
  bucket_arn         = local.standard_audit_kinesis_firehose_destination.bucket_arn
  bucket_name        = local.standard_audit_kinesis_firehose_destination.bucket_name
  bucket_kms_key_arn = local.standard_audit_kinesis_firehose_destination.kms_key_arn
  environment        = var.environment
  workspace          = local.workspace
}

# This will start a crawler every time a new folder is created in the s3 bucket
resource "aws_s3_bucket_notification" "start_standard_crawler_on_event_notification" {
  bucket = local.standard_audit_kinesis_firehose_destination.bucket_name

  lambda_function {
    lambda_function_arn = module.start_standard_audit_data_crawler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = "/"
  }
  depends_on = [aws_lambda_permission.allow_standard_bucket_to_call_lambda]
}

resource "aws_lambda_permission" "allow_standard_bucket_to_call_lambda" {
  statement_id  = "AllowStandardExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.start_standard_audit_data_crawler.arn
  principal     = "s3.amazonaws.com"
  source_arn    = local.standard_audit_kinesis_firehose_destination.bucket_arn
}
