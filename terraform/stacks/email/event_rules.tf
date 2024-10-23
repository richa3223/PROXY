module "eventbridge" {
  # checkov:skip=CKV_TF_1: Ensure Terraform module sources use a commit hash #reason: Intentional for readability
  # checkov:skip=CKV_TF_2: Ensure Terraform module sources use a tag with a version number
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "3.5.0"

  # Use the event bus defined in the common stack
  create_bus = false

  bus_name  = "${local.common_stack_workspace}-event-bus"
  role_name = "${local.workspace}-event-bus-email-iam-role"

  attach_sfn_policy = true
  sfn_target_arns = [
    module.hydrate_gp_email_template_step_function.step_function_arn
  ]

  attach_lambda_policy = true
  lambda_target_arns = [
    module.send_gp_email.arn
  ]

  attach_sqs_policy = true
  sqs_target_arns   = [data.aws_sqs_queue.event_bus_dlq.arn]

  rules = {
    "${local.workspace}-hydrate_gp_email_template" = {
      description   = "Hydrate GP Email once validation is complete"
      event_pattern = jsonencode({ "detail.eventType" : ["ACCESS_REQUEST_READY_FOR_AUTHORISATION"] })
      enabled       = true
    },
    "${local.workspace}-send_gp_email" = {
      description   = "Handle send gp email requests"
      event_pattern = jsonencode({ "detail.eventType" : ["GP_AUTHORISATION_REQUEST_CREATED"] })
      enabled       = true
    }
  }

  targets = {
    "${local.workspace}-hydrate_gp_email_template" = [
      {
        name            = "send-events-to-hydrate_gp_email_emplate"
        arn             = module.hydrate_gp_email_template_step_function.step_function_arn
        dead_letter_arn = data.aws_sqs_queue.event_bus_dlq.arn
        attach_role_arn = true
      }
    ],
    "${local.workspace}-send_gp_email" = [
      {
        name            = "send-events-to-send-gp-email"
        arn             = module.send_gp_email.arn
        dead_letter_arn = data.aws_sqs_queue.event_bus_dlq.arn
      }
    ]
  }
}
