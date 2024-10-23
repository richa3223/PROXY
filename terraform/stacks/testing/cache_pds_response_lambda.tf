module "cache_pds_response" {
  source = "../../modules/lambda_handler"

  lambda_function_name      = "cache_pds_response"
  aws_region                = local.aws_region
  workspace                 = local.workspace
  kms_key_deletion_duration = local.kms_key_deletion_duration
  memory_size               = local.lambda_memory_size_mb

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    "DYNAMODB_TABLE_NAME" = data.aws_dynamodb_table.pds_response_cache.name
  }

}

# DynamoDB

data "aws_iam_policy_document" "cache_pds_response_dynamodb" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
    ]
    resources = [data.aws_dynamodb_table.pds_response_cache.arn]
  }
}

resource "aws_iam_policy" "cache_pds_response_dynamodb" {
  name   = "${local.workspace}-${module.cache_pds_response.function_name}-dynamodb"
  policy = data.aws_iam_policy_document.cache_pds_response_dynamodb.json
}

resource "aws_iam_role_policy_attachment" "cache_pds_response_dynamodb" {
  role       = module.cache_pds_response.iam_role_name
  policy_arn = aws_iam_policy.cache_pds_response_dynamodb.arn
}

#KMS

data "aws_iam_policy_document" "cache_pds_response_kms" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
    ]
    resources = [data.aws_kms_key.dynamodb_kms_key.arn]
  }
}

resource "aws_iam_policy" "cache_pds_response_kms" {
  name        = "${local.workspace}-${module.cache_pds_response.function_name}-kms"
  description = "A policy for decrypting data keys for pds cache response lambda"
  policy      = data.aws_iam_policy_document.cache_pds_response_kms.json
}

resource "aws_iam_role_policy_attachment" "cache_pds_response_kms" {
  role       = module.cache_pds_response.iam_role_name
  policy_arn = aws_iam_policy.cache_pds_response_kms.arn
}
