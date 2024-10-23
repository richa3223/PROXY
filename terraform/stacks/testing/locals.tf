locals {
  workspace                 = lower(terraform.workspace)
  common_stack_workspace    = var.use_shared_common_stack ? var.main_workspace : lower(terraform.workspace)
  aws_region                = "eu-west-2"
  kms_key_deletion_duration = 14

  tags = {
    TagVersion  = "1"
    Programme   = "NPA"
    Project     = "Proxy"
    Environment = var.environment
    Tool        = "Terraform"
    Stack       = "testing"
    Workspace   = terraform.workspace
  }

  cidr_block_list = split(",", var.cidr_block_list)

  lambda_memory_size_mb = 128
}
