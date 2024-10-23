output "arn" {
  value       = aws_lambda_function.lambda_function.arn
  description = "The ARN of the Lambda function"
}
output "iam_role_name" {
  value       = aws_iam_role.iam_for_lambda.name
  description = "The name of the IAM role used by the Lambda function"
}

output "invoke_arn" {
  value       = aws_lambda_function.lambda_function.invoke_arn
  description = "The ARN to be used for invoking the Lambda function"
}

output "function_name" {
  value       = aws_lambda_function.lambda_function.function_name
  description = "The name of the Lambda function"
}

output "iam_role_arn" {
  value       = aws_iam_role.iam_for_lambda.arn
  description = "The ARN of the IAM role used by the Lambda function"
}

output "log_group_arn" {
  value       = aws_cloudwatch_log_group.function_log_group.arn
  description = "The ARN of the CloudWatch Log Group for the Lambda function"
}
