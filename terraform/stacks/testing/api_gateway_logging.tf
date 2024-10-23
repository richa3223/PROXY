resource "aws_cloudwatch_log_group" "mock_api_gateway_default_log_group" {
  #TODO: Discuss appropriate retain period
  #checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year
  name              = "${local.workspace}-Mock-API-Gateway-Execution-Logs/default"
  retention_in_days = 7
  kms_key_id        = aws_kms_key.mock_api_logging_cloudwatch_log_key.arn

  depends_on = [
    aws_kms_key.mock_api_logging_cloudwatch_log_key,
    aws_kms_key_policy.load_testing_key_pair_secrets_manager_key_policy_attach
  ]
}

## API Gateway Account Settings
resource "aws_iam_role" "mock_api_gateway_service_role" {

  name               = "${local.workspace}-mock-api-gateway-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "mock_api_gateway_role_cloudwatch_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
  role       = aws_iam_role.mock_api_gateway_service_role.name
}

data "aws_iam_policy_document" "mock_api_gateway_x_ray_policy" {
  statement {
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
      "xray:GetSamplingTargets",
      "xray:GetSamplingRules",
    ]
    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_policy" "mock_api_gateway_x_ray_policy" {
  name        = "${local.workspace}-mock-api-gateway-x-ray-policy"
  path        = "/"
  description = "IAM policy for mock api gw to access x-ray"

  policy = data.aws_iam_policy_document.mock_api_gateway_x_ray_policy.json
}

resource "aws_iam_role_policy_attachment" "mock_api_gateway_role_x_ray_policy" {
  policy_arn = aws_iam_policy.mock_api_gateway_x_ray_policy.arn
  role       = aws_iam_role.mock_api_gateway_service_role.name
}

resource "aws_api_gateway_account" "mock_api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.mock_api_gateway_service_role.arn
}

# Mock API Logging Cloudwatch Log Group KMS Encryption Key

resource "aws_kms_key" "mock_api_logging_cloudwatch_log_key" {
  description             = "${local.workspace} - KMS Key for Mock API Logging Cloudwatch Logs"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Mock API Logging Cloudwatch Logs"
  }
}

resource "aws_kms_key_policy" "mock_api_logging_cloudwatch_log_key_policy_attach" {
  key_id = aws_kms_key.mock_api_logging_cloudwatch_log_key.id
  policy = data.aws_iam_policy_document.mock_proxy_api_logging_cloudwatch_kms_policy.json
}

data "aws_iam_policy_document" "mock_proxy_api_logging_cloudwatch_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.mock_api_logging_cloudwatch_log_key.arn]
  }

  statement {
    sid    = "Allow Mock API Logging Cloudwatch Log Group to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${local.aws_region}.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.mock_api_logging_cloudwatch_log_key.arn]
  }
}
