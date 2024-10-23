module "get_candidate_relationships" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "get_candidate_relationships"
  aws_region           = local.aws_region
  workspace            = local.workspace

  kms_key_deletion_duration = 14
  memory_size               = var.get_candidate_relationships_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    "VALIDATE_RELATIONSHIPS_STATE_MACHINE_ARN" = module.validate_relationships_step_functions.step_function_arn
  }
}

data "aws_iam_policy_document" "get_candidate_relationships_step_functions_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["states:StartSyncExecution"]
    resources = [module.validate_relationships_step_functions.step_function_arn]
  }
}

resource "aws_iam_policy" "get_candidate_relationships_step_functions_policy" {
  name        = "${local.workspace}-verify-api-parameters-step-functions-policy"
  path        = "/"
  description = "IAM policy for get_candidate_relationships to invoke Step Functions"

  policy = data.aws_iam_policy_document.get_candidate_relationships_step_functions_policy_document.json
}

resource "aws_iam_role_policy_attachment" "get_candidate_relationships_step_functions_policy_attachment" {
  policy_arn = aws_iam_policy.get_candidate_relationships_step_functions_policy.arn
  role       = module.get_candidate_relationships.iam_role_name
}
