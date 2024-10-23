# Lambda Assume Role Policy Document
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    sid    = "LambdaAssumePolicy"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Function Logging Policy Document
data "aws_iam_policy_document" "function_logging_policy_document" {
  statement {
    sid    = "AllowCloudWatchLogging"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [aws_cloudwatch_log_group.function_log_group.arn, "${aws_cloudwatch_log_group.function_log_group.arn}:*"]
  }
  statement {
    sid       = "AllowXRayLogging"
    effect    = "Allow"
    actions   = ["xray:PutTraceSegments", "xray:PutTelemetryRecords"]
    resources = ["*"]
  }
  # This is because the Lambda is inside the VPC and thus needs to create / destroy NIC's to access internal resources.
  dynamic "statement" {
    for_each = local.vpc_config_enabled ? ["1"] : []
    content {
      sid    = "NICCreateAndDestroyAccess"
      effect = "Allow"
      actions = [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ]
      resources = ["*"]
    }
  }
}

# Function Logging Policy
resource "aws_iam_policy" "function_logging_policy" {
  name        = "${var.workspace}-${var.lambda_function_name}-function-logging-policy"
  description = "A logging function document"
  policy      = data.aws_iam_policy_document.function_logging_policy_document.json

  tags = {
    Name = "${var.workspace}-${var.lambda_function_name}-function-logging-policy"
  }
}

# Function Logging Policy Attachment
resource "aws_iam_role_policy_attachment" "function_logging_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.function_logging_policy.arn
}

# Lambda Execution Role
resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.workspace}-${substr(var.lambda_function_name, 0, 40)}-iam-for-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Name = "${var.workspace}-${substr(var.lambda_function_name, 0, 40)}-iam-for-lambda"
  }
}
