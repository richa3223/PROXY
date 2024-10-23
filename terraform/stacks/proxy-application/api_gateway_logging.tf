resource "aws_cloudwatch_log_group" "api_gateway_default_log_group" {
  #TODO: Discuss appropriate retain period
  #checkov:skip=CKV_AWS_338: Ensure CloudWatch log groups retains logs for at least 1 year
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.api.id}/default"
  retention_in_days = local.api_gateway_cloudwatch_log_retention_days
  kms_key_id        = aws_kms_key.proxy_api_logging_cloudwatch_log_key.arn

  depends_on = [aws_kms_key.proxy_api_logging_cloudwatch_log_key, aws_kms_key_policy.proxy_api_logging_cloudwatch_log_key_policy_attach]
}

## API Gateway Account Settings
resource "aws_iam_role" "api_gateway_service_role" {

  name               = "${local.workspace}-api-gateway-role"
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

resource "aws_iam_role_policy_attachment" "api_gateway_role_cloudwatch_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
  role       = aws_iam_role.api_gateway_service_role.name
}

data "aws_iam_policy_document" "api_gateway_x_ray_policy" {
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

resource "aws_iam_policy" "api_gateway_x_ray_policy" {
  name        = "${local.workspace}-api-gateway-x-ray-policy"
  path        = "/"
  description = "IAM policy for api gw to access x-ray"

  policy = data.aws_iam_policy_document.api_gateway_x_ray_policy.json
}

resource "aws_iam_role_policy_attachment" "api_gateway_role_x_ray_policy" {
  policy_arn = aws_iam_policy.api_gateway_x_ray_policy.arn
  role       = aws_iam_role.api_gateway_service_role.name
}

resource "aws_api_gateway_account" "api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_service_role.arn
}
