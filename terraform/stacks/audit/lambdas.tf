module "redact_sensitive_data" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "redact_sensitive_data"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration
  memory_size               = var.redact_sensitive_data_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids
}

module "start_sensitive_audit_data_crawler" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "start_sensitive_audit_data_crawler"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids
  environment_variables = {
    CRAWLER_NAME = module.sensitive_glue_crawler.crawler_name
  }
}

module "start_standard_audit_data_crawler" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "start_standard_audit_data_crawler"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids
  environment_variables = {
    CRAWLER_NAME = module.standard_glue_crawler.crawler_name
  }
}

#lambdas that start a crawler will need some extra permission to actually start a crawler and to receive events from s3

resource "aws_iam_policy" "lambda_sensitive_start_crawler_policy" {
  name        = "${local.workspace}-lambda_sensitive_start_crawler_policy"
  description = "A policy for automatically starting glue crawlers when new event types get added"
  policy      = data.aws_iam_policy_document.lambda_sensitive_start_crawler_policy_document.json
}

resource "aws_iam_role_policy_attachment" "start_sensitive_crawler_role_attachment" {
  role       = module.start_sensitive_audit_data_crawler.iam_role_name
  policy_arn = aws_iam_policy.lambda_sensitive_start_crawler_policy.arn
}


#lambdas that start a crawler will need some extra premission to actually start a crawler and to recieve events from s3
resource "aws_iam_policy" "lambda_standard_start_crawler_policy" {
  name        = "${local.workspace}-lambda_standard_start_crawler_policy"
  description = "A policy for automatically starting glue crawlers when new event types get added"
  policy      = data.aws_iam_policy_document.lambda_standard_start_crawler_policy_document.json
}

resource "aws_iam_role_policy_attachment" "start_standard_crawler_role_attachment" {
  role       = module.start_standard_audit_data_crawler.iam_role_name
  policy_arn = aws_iam_policy.lambda_standard_start_crawler_policy.arn
}