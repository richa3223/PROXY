resource "aws_cloudwatch_log_group" "event_bus_logs" {
  #checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year TODO: Discuss appropriate retention period
  name              = "/aws/events/${local.workspace}-event-bus-logs"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.cloudwatch_log_key.arn

  depends_on = [aws_kms_key.cloudwatch_log_key, aws_kms_key_policy.cloudwatch_log_key_policy_attachment]

  tags = merge({
    Name = "/aws/events/${local.workspace}-event-bus-logs"
  }, local.tags)
}

resource "aws_cloudwatch_log_stream" "event_bus_logs" {
  name           = "event-bus-logs"
  log_group_name = aws_cloudwatch_log_group.event_bus_logs.name
}

resource "aws_schemas_registry" "business_events_schema_registry" {
  name = "${local.workspace}-business_events_schema_registry"
}

resource "aws_cloudwatch_log_group" "event_pipe_logs" {
  #checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year TODO: Discuss appropriate retention period
  name              = "/aws/events/${local.workspace}-event-pipe-logs"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.cloudwatch_log_key.arn

  depends_on = [aws_kms_key.cloudwatch_log_key, aws_kms_key_policy.cloudwatch_log_key_policy_attachment]

  tags = merge({
    Name = "/aws/events/${local.workspace}-event-pipe-logs"
  }, local.tags)
}
