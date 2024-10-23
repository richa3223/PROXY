resource "aws_kinesis_firehose_delivery_stream" "splunk_metrics_firehose" {
  name        = "${local.workspace}-splunk-metrics-firehose"
  destination = "splunk"

  server_side_encryption {
    enabled  = true
    key_type = "CUSTOMER_MANAGED_CMK"
    key_arn  = module.splunk_firehose_backup_bucket.kms_key_arn
  }

  splunk_configuration {
    hec_endpoint               = "https://hec.splunk.aws.digital.nhs.uk/services/collector/event"
    hec_token                  = var.SPLUNK_HEC_TOKEN
    hec_acknowledgment_timeout = 600
    hec_endpoint_type          = "Event"
    s3_backup_mode             = "FailedEventsOnly"

    s3_configuration {
      role_arn           = aws_iam_role.splunk_firehose_role.arn
      bucket_arn         = module.splunk_firehose_backup_bucket.bucket_arn
      buffering_size     = 10
      buffering_interval = 400
      compression_format = "GZIP"
    }

    processing_configuration {
      enabled = true
      processors {
        type = "Lambda"
        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${module.splunk_log_and_metric_formatter.arn}:$LATEST"
        }
        parameters {
          parameter_name  = "RoleArn"
          parameter_value = aws_iam_role.splunk_firehose_role.arn
        }
        parameters {
          parameter_name  = "BufferSizeInMBs"
          parameter_value = "0.256"
        }
        parameters {
          parameter_name  = "BufferIntervalInSeconds"
          parameter_value = "60"
        }
      }
    }
    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.splunk_firehose_logs.name
      log_stream_name = aws_cloudwatch_log_stream.splunk_firehose_logs.name
    }
  }
}

data "aws_iam_policy_document" "firehose_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "splunk_firehose_role" {
  name               = "${local.workspace}-splunk-firehose-role"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume_role.json
}

data "aws_iam_policy_document" "splunk_firehose_role_access_policy" {
  statement {
    sid    = "AllowFirehoseToAccessS3"
    effect = "Allow"
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    resources = [
      module.splunk_firehose_backup_bucket.bucket_arn,
      "${module.splunk_firehose_backup_bucket.bucket_arn}/*",
    ]
  }
  statement {
    sid       = "AllowFirehoseToInvokeLambda"
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = ["${module.splunk_log_and_metric_formatter.arn}:$LATEST"]
  }
  statement {
    sid    = "AllowFirehoseToLogToCloudWatch"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      aws_cloudwatch_log_group.splunk_firehose_logs.arn,
      aws_cloudwatch_log_stream.splunk_firehose_logs.arn,
    ]
  }
  statement {
    sid    = "AllowFirehoseToEncryptData"
    effect = "Allow"
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = [module.splunk_firehose_backup_bucket.kms_key_arn]
  }
}

resource "aws_iam_role_policy" "firehose_role_access_policy" {
  name   = "firehose_role_access_policy"
  role   = aws_iam_role.splunk_firehose_role.id
  policy = data.aws_iam_policy_document.splunk_firehose_role_access_policy.json
}
