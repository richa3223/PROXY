
module "splunk_log_and_metric_formatter" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "splunk_log_and_metric_formatter"
  aws_region           = var.region
  workspace            = local.workspace

  kms_key_deletion_duration = 14

  security_group_ids = data.aws_security_groups.private_lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    SPLUNK_CLOUDWATCH_SOURCETYPE = "aws:cloudwatch:metric"
    METRICS_OUTPUT_FORMAT        = "json"
  }
}
