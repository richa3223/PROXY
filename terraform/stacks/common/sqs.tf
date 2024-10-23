
resource "aws_sqs_queue" "event_bus_dlq" {
  name              = "${local.workspace}-event-bus-dlq"
  kms_master_key_id = aws_kms_alias.sqs_key_alias.arn
  tags = {
    Name = "${local.workspace}-event-bus-dlq"
  }
}

data "aws_iam_policy_document" "event_bus_dlq_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = [
      aws_sqs_queue.event_bus_dlq.arn
    ]

    actions = ["sqs:SendMessage"]
  }
}

resource "aws_sqs_queue_policy" "event_bus_dlq_policy_attachment" {
  queue_url = aws_sqs_queue.event_bus_dlq.id
  policy    = data.aws_iam_policy_document.event_bus_dlq_policy.json
}
