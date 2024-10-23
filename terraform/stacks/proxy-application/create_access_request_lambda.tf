module "create_access_request" {
  source = "../../modules/lambda_handler"

  lambda_function_name = "create_access_request"
  aws_region           = local.aws_region
  workspace            = local.workspace

  kms_key_deletion_duration = 14
  memory_size               = var.create_access_request_lambda_memory_size

  security_group_ids = data.aws_security_groups.lambda_security_groups.ids
  subnet_ids         = data.aws_subnets.lambda_subnets.ids

  environment_variables = {
    "DYNAMODB_TABLE_NAME" = data.aws_dynamodb_table.patient_relationship.name
    "DYNAMODB_TTL"        = var.dynamodb_ttl
  }
}

data "aws_iam_policy_document" "create_access_request_dynamodb_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
    ]
    resources = [data.aws_dynamodb_table.patient_relationship.arn]
  }
}

resource "aws_iam_policy" "create_access_request_dynamodb_policy" {
  name        = "${local.workspace}-${module.create_access_request.function_name}-dynamodb-permissions"
  description = "A policy for putting and updating items in the patient relationship table"
  policy      = data.aws_iam_policy_document.create_access_request_dynamodb_policy_document.json
}

resource "aws_iam_role_policy_attachment" "create_access_request_dynamodb_attachment" {
  role       = module.create_access_request.iam_role_name
  policy_arn = aws_iam_policy.create_access_request_dynamodb_policy.arn
}

data "aws_iam_policy_document" "create_access_request_kms_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
    ]
    resources = [data.aws_kms_key.dynamodb_kms_key.arn]
  }
}

resource "aws_iam_policy" "create_access_request_kms_policy" {
  name        = "${local.workspace}-${module.create_access_request.function_name}-kms-permissions"
  description = "A policy for decrypting data keys for the create access request lambda"
  policy      = data.aws_iam_policy_document.create_access_request_kms_policy_document.json
}

resource "aws_iam_role_policy_attachment" "create_access_request_kms_attachment" {
  role       = module.create_access_request.iam_role_name
  policy_arn = aws_iam_policy.create_access_request_kms_policy.arn
}
