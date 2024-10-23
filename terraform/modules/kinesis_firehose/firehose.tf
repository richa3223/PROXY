resource "aws_kinesis_firehose_delivery_stream" "kinesis_firehose" {
  name        = var.firehose_name
  destination = var.firehose_destination

  server_side_encryption {
    enabled  = true
    key_type = "CUSTOMER_MANAGED_CMK"
    key_arn  = aws_kms_key.firehose_key.arn
  }
  dynamic "extended_s3_configuration" {
    for_each = var.firehose_destination == "extended_s3" ? [1] : []
    content {
      role_arn           = aws_iam_role.firehose_iam_role.arn
      bucket_arn         = var.bucket_arn
      buffering_interval = var.buffer_interval
      buffering_size     = var.buffer_size

      dynamic_partitioning_configuration {
        enabled = var.dynamic_partitioning_enabled
      }

      prefix              = var.prefix
      error_output_prefix = "errors/"

      processing_configuration {
        enabled = "true"

        processors {
          type = "MetadataExtraction"
          parameters {
            parameter_name  = "MetadataExtractionQuery"
            parameter_value = "{detailType:.[\"detail-type\"]}"
          }
          parameters {
            parameter_name  = "JsonParsingEngine"
            parameter_value = "JQ-1.6"
          }

        }
        dynamic "processors" {
          for_each = local.enable_lambda_processor ? [1] : []
          content {
            type = "Lambda"
            parameters {
              parameter_name  = "LambdaArn"
              parameter_value = var.lambda_processor_arn
            }

          }
        }
      }

      cloudwatch_logging_options {
        enabled         = true
        log_group_name  = aws_cloudwatch_log_group.firehose_logs.name
        log_stream_name = aws_cloudwatch_log_stream.firehose_log_stream.name
      }
    }
  }

  tags = merge(var.tags, local.common_tags)
}

resource "aws_cloudwatch_log_group" "firehose_logs" {
  #checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year TODO: Define log retention period
  name              = "/aws/kinesisfirehose/${var.firehose_name}-logs"
  retention_in_days = var.log_retention_in_days
  kms_key_id        = aws_kms_key.proxy_firehose_cloudwatch_log_key.arn

  depends_on = [aws_kms_key.proxy_firehose_cloudwatch_log_key]

  tags = {
    "Name" = "/aws/kinesisfirehose/${var.firehose_name}-logs"
  }
}

resource "aws_cloudwatch_log_stream" "firehose_log_stream" {
  name           = "${var.firehose_name}-log-stream"
  log_group_name = aws_cloudwatch_log_group.firehose_logs.name
}
