module "process_validation_result" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "process_validation_result"
  aws_region           = local.aws_region
  workspace            = local.workspace

  kms_key_deletion_duration = 14
  memory_size               = var.process_validation_result_lambda_memory_size

  security_group_ids = data.aws_security_groups.private_lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids
}
