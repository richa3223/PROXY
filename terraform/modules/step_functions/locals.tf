locals {
  step_functions_require_lambdas        = length(var.lambda_arn_list) > 0 ? true : false
  step_functions_require_state_machines = length(var.state_machine_arn_list) > 0 ? true : false
}
