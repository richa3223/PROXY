module "eventbridge" {
  # checkov:skip=CKV_TF_1: Ensure Terraform module sources use a commit hash #reason: Intentional for readability
  #checkov:skip=CKV_TF_2: Ensure Terraform module sources use a tag with a version number
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "3.5.0"

  # Use the event bus defined in the common stack
  create_bus = false

  bus_name  = "${local.common_stack_workspace}-event-bus"
  role_name = "${local.workspace}-event-bus-audit-iam-role"

  attach_kinesis_firehose_policy = true
  kinesis_firehose_target_arns = [
    module.standard_audit_kinesis_firehose.firehose_arn,
    module.sensitive_audit_kinesis_firehose.firehose_arn
  ]

  attach_sqs_policy = true
  sqs_target_arns   = [data.aws_sqs_queue.event_bus_dlq.arn]

  rules = {
    "${local.workspace}-audit" = {
      description   = "Audit Validation Events put on the event bus"
      event_pattern = local.match_validation_result_pattern
      enabled       = true
    }
  }

  targets = {
    "${local.workspace}-audit" = [
      {
        name            = "send-events-to-standard-firehose"
        arn             = module.standard_audit_kinesis_firehose.firehose_arn
        dead_letter_arn = data.aws_sqs_queue.event_bus_dlq.arn
        attach_role_arn = true
      },
      {
        name            = "send-events-to-sensitive-firehose"
        arn             = module.sensitive_audit_kinesis_firehose.firehose_arn
        dead_letter_arn = data.aws_sqs_queue.event_bus_dlq.arn
        attach_role_arn = true
      }
    ]
  }
}
