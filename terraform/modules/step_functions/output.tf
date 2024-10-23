output "step_function_arn" {
  value = aws_sfn_state_machine.sfn_state_machine.arn
}

output "iam_role_name" {
  value = aws_iam_role.iam_for_sfn.name
}
