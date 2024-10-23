output "firehose_name" {
  value = aws_kinesis_firehose_delivery_stream.kinesis_firehose.name
}

output "firehose_arn" {
  value = aws_kinesis_firehose_delivery_stream.kinesis_firehose.arn
}

output "iam_role_name" {
  value = aws_iam_role.firehose_iam_role.name
}

output "iam_role_arn" {
  value = aws_iam_role.firehose_iam_role.arn
}

output "log_group_arn" {
  value = aws_cloudwatch_log_group.firehose_logs.arn
}

output "log_stream_arn" {
  value = aws_cloudwatch_log_stream.firehose_log_stream.arn
}
