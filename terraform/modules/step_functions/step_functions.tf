resource "aws_sfn_state_machine" "sfn_state_machine" {
  #checkov:skip=CKV_AWS_285: Ensure State Machine has execution history logging enabled #reason: Chekov requires include_execution_data=true to satisfy the validation. We don't want to include data into logging in the prod environments to avoid potential legal issues
  name     = "${var.workspace}-${var.step_functions_name}-state-machine"
  role_arn = aws_iam_role.iam_for_sfn.arn
  type     = var.state_machine_type

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.log_group_for_sfn.arn}:*"
    include_execution_data = var.environment == "prod" ? false : true
    level                  = var.environment == "prod" ? "ERROR" : "ALL"
  }

  tracing_configuration {
    enabled = true
  }

  definition = var.state_machine_definition

  lifecycle {
    create_before_destroy = true
  }
}
