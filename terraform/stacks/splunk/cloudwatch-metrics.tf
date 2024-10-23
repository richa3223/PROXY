resource "aws_cloudwatch_metric_stream" "splunk_metric_stream" {
  name          = "${local.workspace}-splunk-metric-stream"
  role_arn      = aws_iam_role.splunk_metric_stream_to_firehose.arn
  firehose_arn  = aws_kinesis_firehose_delivery_stream.splunk_metrics_firehose.arn
  output_format = "json"

  include_filter {
    metric_names = [
      "IngestionToInvocationStartLatency",
      "InvocationsFailedToBeSentToDlq",
      "PutEventsApproximateCallCount",
      "PutEventsApproximateFailedCount",
      "PutEventsFailedEntriesCount",
      "ThrottledRules",
    ]
    namespace = "AWS/Events"
  }

  include_filter {
    metric_names = [
      "NumberOfMessagesReceived",
    ]
    namespace = "AWS/SQS"
  }
}

# https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-metric-streams-trustpolicy.html
data "aws_iam_policy_document" "splunk_metric_streams_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["streams.metrics.cloudwatch.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "splunk_metric_stream_to_firehose" {
  name               = "${local.workspace}-splunk-metric-stream-role"
  assume_role_policy = data.aws_iam_policy_document.splunk_metric_streams_assume_role.json
}

# https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-metric-streams-trustpolicy.html
data "aws_iam_policy_document" "metric_stream_to_firehose" {
  statement {
    effect = "Allow"

    actions = [
      "firehose:DeleteDeliveryStream",
      "firehose:PutRecord",
      "firehose:PutRecordBatch",
      "firehose:UpdateDestination"
    ]
    resources = [aws_kinesis_firehose_delivery_stream.splunk_metrics_firehose.arn]
  }
}
resource "aws_iam_role_policy" "metric_stream_to_firehose" {
  role   = aws_iam_role.splunk_metric_stream_to_firehose.id
  policy = data.aws_iam_policy_document.metric_stream_to_firehose.json
}
