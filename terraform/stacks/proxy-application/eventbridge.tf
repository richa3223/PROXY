module "default_eventbridge" {
  #checkov:skip=CKV_TF_1: Ensure Terraform module sources use a commit hash #reason: Intentional for readability
  #checkov:skip=CKV_TF_2: Ensure Terraform module sources use a tag with a version number
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "3.5.0"

  # Use the event bus defined in the common stack
  create_bus = false

  bus_name  = "default"
  role_name = "${local.workspace}-default-event-bus-iam-role"

  attach_lambda_policy = true
  lambda_target_arns   = [module.raise_certificate_alert.arn]

  attach_sqs_policy = true
  sqs_target_arns   = [data.aws_sqs_queue.event_bus_dlq.arn]

  rules = {
    "${local.workspace}-daily_check_certificate_expiry" = {
      description         = "Check certificate expiry daily"
      schedule_expression = "cron(0 0 * * ? *)"
      enabled             = true
    }
  }

  targets = {
    "${local.workspace}-daily_check_certificate_expiry" = [
      {
        name            = "raise-certificate-alert"
        arn             = module.raise_certificate_alert.arn
        dead_letter_arn = data.aws_sqs_queue.event_bus_dlq.arn
      }
    ]
  }

  depends_on = [module.raise_certificate_alert]
}
