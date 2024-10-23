module "redact_eventbridge_events_and_log_to_cloudwatch" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "redact_eventbridge_events_and_log_to_cloudwatch"
  aws_region                = var.region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration
  memory_size               = 1024

  security_group_ids = [aws_security_group.lambda_base_private_access.id]
  subnet_ids         = local.list_of_cidr_block_for_additional_subnet_private_subnets

  environment_variables = {
    "CLOUDWATCH_LOG_GROUP_NAME"  = aws_cloudwatch_log_group.event_bus_logs.name
    "CLOUDWATCH_LOG_STREAM_NAME" = aws_cloudwatch_log_stream.event_bus_logs.name
  }
}

data "aws_iam_policy_document" "redact_eventbridge_events_and_log_to_cloudwatch_event_bus_events_for_lambda_policy_document" {
  statement {
    effect  = "Allow"
    actions = ["logs:PutLogEvents"]
    resources = var.environment == "dev" ? [
      "${aws_cloudwatch_log_group.event_bus_logs.arn}:log-stream:${aws_cloudwatch_log_stream.event_bus_logs.name}",
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:eventbridge-log-redaction-infrastructure-test*"
      ] : [
      "${aws_cloudwatch_log_group.event_bus_logs.arn}:log-stream:${aws_cloudwatch_log_stream.event_bus_logs.name}",
    ]
  }
}

resource "aws_iam_policy" "redact_eventbridge_events_and_log_to_cloudwatch_event_bus_events_for_lambda_policy" {
  name        = "${local.workspace}-${module.redact_eventbridge_events_and_log_to_cloudwatch.function_name}-cloudwatch-logs-permissions"
  description = "A policy for publishing events to event bus"
  policy      = data.aws_iam_policy_document.redact_eventbridge_events_and_log_to_cloudwatch_event_bus_events_for_lambda_policy_document.json
}

resource "aws_iam_role_policy_attachment" "redact_eventbridge_events_and_log_to_cloudwatch_event_bus_events_for_lambda_attachment" {
  role       = module.redact_eventbridge_events_and_log_to_cloudwatch.iam_role_name
  policy_arn = aws_iam_policy.redact_eventbridge_events_and_log_to_cloudwatch_event_bus_events_for_lambda_policy.arn
}

resource "aws_lambda_permission" "allow_eventbridge_to_invoke_redact_eventbridge_events_and_log_to_cloudwatch_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.redact_eventbridge_events_and_log_to_cloudwatch.function_name
  principal     = "events.amazonaws.com"
  source_arn    = module.eventbridge.eventbridge_rule_arns["redact_eventbridge_events_and_log_to_cloudwatch"]
}
