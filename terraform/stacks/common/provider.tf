provider "aws" {
  region = var.region
  default_tags {
    tags = {
      TagVersion  = "1"
      Programme   = "NPA"
      Project     = "Proxy"
      Environment = var.environment
      Tool        = "Terraform"
      Stack       = "common"
      Workspace   = terraform.workspace
    }
  }
}
