module "slack_alerts" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "slack_alerts"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration
  memory_size               = var.slack_alerts_alert_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    SLACK_WEBHOOK_URL = var.SLACK_WEBHOOK
  }

}
