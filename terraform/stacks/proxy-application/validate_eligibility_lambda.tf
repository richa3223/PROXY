module "validate_eligibility" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "validate_eligibility"
  aws_region           = local.aws_region
  workspace            = local.workspace

  kms_key_deletion_duration = 14
  memory_size               = var.validate_eligibility_lambda_memory_size

  security_group_ids = data.aws_security_groups.private_lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    EVENT_BUS_NAME = data.aws_cloudwatch_event_bus.event_bus.name
  }
}


data "aws_iam_policy_document" "validate_eligibility_event_bus_events_for_lambda_policy_document" {
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

resource "aws_iam_policy" "validate_eligibility_event_bus_events_for_lambda_policy" {
  name        = "${local.workspace}-${module.validate_eligibility.function_name}-event-bus-permissions"
  description = "A policy for publishing events to event bus"
  policy      = data.aws_iam_policy_document.validate_eligibility_event_bus_events_for_lambda_policy_document.json
}

resource "aws_iam_role_policy_attachment" "validate_eligibility_event_bus_events_for_lambda_attachment" {
  role       = module.validate_eligibility.iam_role_name
  policy_arn = aws_iam_policy.validate_eligibility_event_bus_events_for_lambda_policy.arn
}
