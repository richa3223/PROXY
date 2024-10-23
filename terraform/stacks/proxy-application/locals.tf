locals {
  # tflint-ignore: terraform_unused_declarations
  workspace                                 = lower(terraform.workspace)
  common_stack_workspace                    = var.use_shared_common_stack ? var.main_workspace : lower(terraform.workspace)
  is_main_workspace                         = var.main_workspace == lower(terraform.workspace)
  aws_region                                = "eu-west-2"
  aws_global_region                         = "us-east-1"
  api_gateway_cloudwatch_log_retention_days = 7
  # tflint-ignore: terraform_unused_declarations

  ###########################################
  # KMS locals
  ###########################################
  kms_key_deletion_duration = 14

  tags = {
    Environment = var.environment
    Programme   = "NPA"
    Project     = "Proxy"
    TagVersion  = "1"
    Tool        = "Terraform"
    Workspace   = terraform.workspace
    Stack       = "proxy-application"
  }

  match_dynamo_db_stream_result_pattern = jsonencode({ "detail.eventType" : ["ACCESS_REQUEST_CREATED"] })
}
