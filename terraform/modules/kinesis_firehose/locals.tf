locals {
  enable_lambda_processor = var.lambda_processor_arn != "" ? true : false
}
