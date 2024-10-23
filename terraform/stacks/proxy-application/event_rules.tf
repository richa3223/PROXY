module "eventbridge" {
  # checkov:skip=CKV_TF_1: Ensure Terraform module sources use a commit hash #reason: Intentional for readability
  #checkov:skip=CKV_TF_2: Ensure Terraform module sources use a tag with a version number
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "3.5.0"

  # Use the event bus defined in the common stack
  create_bus = false

  bus_name  = "${local.common_stack_workspace}-event-bus"
  role_name = "${local.workspace}-event-bus-proxy-application-iam-role"

  attach_sfn_policy = true
  sfn_target_arns = [
    module.process_access_request_step_function.step_function_arn
  ]

  attach_sqs_policy = true
  sqs_target_arns   = [data.aws_sqs_queue.event_bus_dlq.arn]

  rules = {
    "${local.workspace}-dynamo_db_consume_access_request" = {
      description   = "Consume dynamodb events for process_access_request"
      event_pattern = local.match_dynamo_db_stream_result_pattern
      enabled       = true
    }
  }

  targets = {
    "${local.workspace}-dynamo_db_consume_access_request" = [
      {
        name            = "send-events-to-process-access-request"
        arn             = module.process_access_request_step_function.step_function_arn
        dead_letter_arn = data.aws_sqs_queue.event_bus_dlq.arn
        attach_role_arn = true
      }
    ]
  }
}
