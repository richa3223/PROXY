resource "aws_cloudwatch_log_group" "function_log_group" {
  # TODO: implement
  #checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year
  name              = "/aws/lambda/${var.workspace}-${var.lambda_function_name}"
  retention_in_days = 7
  kms_key_id        = aws_kms_key.cloudwatch_log_key.arn

  depends_on = [aws_kms_key_policy.cloudwatch_kms_policy_attachment]

  lifecycle {
    prevent_destroy = false
  }
}
