resource "aws_cloudwatch_log_group" "splunk_firehose_logs" {
  #checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year
  name              = "${local.workspace}-splunk-firehose-logs"
  kms_key_id        = aws_kms_key.cloudwatch_log_key.arn
  retention_in_days = 30
  depends_on        = [aws_kms_key.cloudwatch_log_key, aws_kms_alias.cloudwatch_log_key]
}
resource "aws_cloudwatch_log_stream" "splunk_firehose_logs" {
  name           = "${local.workspace}-splunk-firehose-log-stream"
  log_group_name = aws_cloudwatch_log_group.splunk_firehose_logs.name
}
