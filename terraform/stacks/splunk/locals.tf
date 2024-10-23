locals {
  workspace              = lower(terraform.workspace)
  common_stack_workspace = var.use_shared_common_stack ? var.main_workspace : lower(terraform.workspace)
  aws_region             = "eu-west-2"

  tags = {
    TagVersion  = "1"
    Programme   = "NPA"
    Project     = "Proxy"
    Environment = var.environment
    Tool        = "Terraform"
    Stack       = "splunk"
  }
}
