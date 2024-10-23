locals {
  common_tags = {
    TagVersion  = "1"
    Programme   = "NPA"
    Project     = "Proxy"
    Environment = var.environment
    Tool        = "Terraform"
  }
}
