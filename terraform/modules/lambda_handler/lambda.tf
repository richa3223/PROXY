# TODO:
# Generate Lambda Layer for the function
data "archive_file" "lambda_dependencies" {
  type        = "zip"
  source_dir  = "../../../build/${var.lambda_function_name}/dependencies"
  output_path = "../../../build/${var.lambda_function_name}_dependencies.zip"
}

resource "aws_lambda_layer_version" "python_dependencies_layer" {
  filename            = data.archive_file.lambda_dependencies.output_path
  layer_name          = "${var.workspace}-${var.lambda_function_name}-layer"
  compatible_runtimes = ["python3.9"]
  description         = "Lambda python dependencies"
  source_code_hash    = data.archive_file.lambda_dependencies.output_base64sha256
  lifecycle {
    create_before_destroy = true
  }
}

# Generate the Lambda function
data "archive_file" "lambda_function" {
  type        = "zip"
  source_dir  = "../../../build/${var.lambda_function_name}/function"
  output_path = "../../../build/${var.lambda_function_name}_function.zip"
}

resource "aws_lambda_function" "lambda_function" {
  # TODO: implement
  #checkov:skip=CKV_AWS_115: Ensure that AWS Lambda function is configured for function-level concurrent execution limit
  #checkov:skip=CKV_AWS_116: Ensure that AWS Lambda function is configured for a Dead Letter Queue(DLQ)
  #checkov:skip=CKV_AWS_173: Check encryption settings for Lambda environmental variable
  #checkov:skip=CKV_AWS_272: Ensure AWS Lambda function is configured to validate code-signing
  function_name    = "${var.workspace}-${var.lambda_function_name}"
  filename         = data.archive_file.lambda_function.output_path
  source_code_hash = data.archive_file.lambda_function.output_base64sha256
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "lambdas.${var.lambda_function_name}.main.lambda_handler"
  runtime          = "python3.9"
  timeout          = var.timeout
  memory_size      = var.memory_size

  layers = [aws_lambda_layer_version.python_dependencies_layer.arn]

  environment {
    variables = var.environment_variables
  }

  tracing_config {
    mode = "Active"
  }
  dynamic "vpc_config" {
    for_each = local.vpc_config_enabled ? ["1"] : []
    content {
      security_group_ids = var.security_group_ids
      subnet_ids         = var.subnet_ids
    }
  }

  # Hacky solution to ensure the lambda role has permission to run inside vpc
  depends_on = [aws_iam_role_policy_attachment.function_logging_policy_attachment]
}

locals {

  vpc_config_enabled = length(var.security_group_ids) != 0 ? length(var.subnet_ids) != 0 ? true : false : false

}
