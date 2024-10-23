module "validate_relationship" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "validate_relationship"
  aws_region           = local.aws_region
  workspace            = local.workspace
  #cloudwatch_to_firehose_trust_role_arn = module.kinesis_firehose_splunk.cloudwatch_to_firehose_trust_role_arn
  #splunk_kinesis_firehose_arn           = module.kinesis_firehose_splunk.fh_to_fh_delivery_stream_arn
  kms_key_deletion_duration = 14
  memory_size               = var.validate_relationship_lambda_memory_size

  security_group_ids = data.aws_security_groups.private_lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids


  environment_variables = {
    EVENT_BUS_NAME = data.aws_cloudwatch_event_bus.event_bus.name
  }
}


data "aws_iam_policy_document" "validate_relationship_event_bus_events_for_lambda_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "events:PutEvents"
    ]
    resources = [
      data.aws_cloudwatch_event_bus.event_bus.arn
    ]
  }
}

resource "aws_iam_policy" "validate_relationship_event_bus_events_for_lambda_policy" {
  name        = "${local.workspace}-${module.validate_relationship.function_name}-event-bus-permissions"
  description = "A policy for publishing events to event bus"
  policy      = data.aws_iam_policy_document.validate_relationship_event_bus_events_for_lambda_policy_document.json
}

resource "aws_iam_role_policy_attachment" "validate_relationship_event_bus_events_for_lambda_attachment" {
  role       = module.validate_relationship.iam_role_name
  policy_arn = aws_iam_policy.validate_relationship_event_bus_events_for_lambda_policy.arn
}
