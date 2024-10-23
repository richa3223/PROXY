module "eventbridge" {
  # checkov:skip=CKV_TF_1: Ensure Terraform module sources use a commit hash
  #checkov:skip=CKV_TF_2: Ensure Terraform module sources use a tag with a version number
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "3.5.0"

  bus_name  = "${local.workspace}-event-bus"
  role_name = "${local.workspace}-event-bus-common-iam-role"

  attach_lambda_policy = true
  lambda_target_arns   = [module.redact_eventbridge_events_and_log_to_cloudwatch.arn]

  attach_sqs_policy = true
  sqs_target_arns   = [aws_sqs_queue.event_bus_dlq.arn]

  rules = {
    redact_eventbridge_events_and_log_to_cloudwatch = {
      description   = "Log all events put on the event bus"
      event_pattern = local.match_all_events_pattern
      enabled       = true
    }
  }

  targets = {
    redact_eventbridge_events_and_log_to_cloudwatch = [
      {
        name            = "log-events-to-cloudwatch"
        arn             = module.redact_eventbridge_events_and_log_to_cloudwatch.arn
        dead_letter_arn = aws_sqs_queue.event_bus_dlq.arn
      }
    ]
  }

  pipes = {
    "${local.workspace}-DynamoDBStreamToEventBridge" = {
      source = aws_dynamodb_table.patient_relationship.stream_arn
      target = "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:event-bus/${local.workspace}-event-bus"

      source_parameters = {
        dynamodb_stream_parameters = {
          on_partial_batch_item_failure      = "AUTOMATIC_BISECT"
          maximum_batching_window_in_seconds = 60
          starting_position                  = "LATEST"
        }
      }

      target_parameters = {
        input_template = "{\"eventId\": <$.eventID>, \"eventType\": <$.dynamodb.NewImage.ApplicationStatus.S>, \"referenceCode\": <$.dynamodb.Keys.ReferenceCode.S> }"
      }

      log_configuration = {
        level = var.environment == "prod" || var.environment == "int" ? "ERROR" : "TRACE"
        cloudwatch_logs_log_destination = {
          log_group_arn = aws_cloudwatch_log_group.event_pipe_logs.arn
        }
      }
    }
  }
  depends_on = [module.redact_eventbridge_events_and_log_to_cloudwatch, aws_dynamodb_table.patient_relationship, aws_cloudwatch_log_group.event_pipe_logs]
}

# Adds all the schemas inside .json files in the "events" folder to the schema repository
resource "aws_schemas_schema" "event_schemas" {
  for_each      = local.event_schema_file_names
  name          = trimsuffix(each.value, ".json")
  registry_name = aws_schemas_registry.business_events_schema_registry.name
  type          = "JSONSchemaDraft4"
  description   = "Schema of a validation result event (successful, failed or errored)"
  content       = file("${local.event_schema_directory}${each.value}")
}
data "aws_iam_policy_document" "eventbridge_pipe_kms_policy_document" {
  statement {
    sid    = "DynamoDBKMSAccess"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*"
    ]
    resources = [aws_kms_key.dynamodb_key.arn]
  }
}

resource "aws_iam_policy" "eventbridge_pipe_kms_policy" {
  name        = "${local.workspace}-DynamoDBStreamToEventBridge-KMS-Access"
  description = "A policy for granting access to the KMS key for the DynamoDB stream for EventBridge pipe polling."
  policy      = data.aws_iam_policy_document.eventbridge_pipe_kms_policy_document.json
}

resource "aws_iam_role_policy_attachment" "eventbridge_pipe_kms_policy_attachment" {
  role       = module.eventbridge.eventbridge_pipe_role_names["${local.workspace}-DynamoDBStreamToEventBridge"]
  policy_arn = aws_iam_policy.eventbridge_pipe_kms_policy.arn
}
