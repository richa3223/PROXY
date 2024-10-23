module "relationship_lookup" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "relationship_lookup"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = 14
  memory_size               = var.relationship_lookup_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    PDS_BASE_URL = var.pds_base_url
  }
}
