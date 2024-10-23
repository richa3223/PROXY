resource "aws_cloudwatch_log_group" "log_group_for_sfn" {
  # checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year TODO: Discuss appropriate retention period
  name              = "/aws/vendedlogs/${var.workspace}-${var.step_functions_name}-sfn-logs"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.proxy_step_function_cloudwatch_log_key.arn

  depends_on = [aws_kms_key.proxy_step_function_cloudwatch_log_key, aws_kms_key_policy.proxy_step_function_cloudwatch_log_key_policy_attach]
}
