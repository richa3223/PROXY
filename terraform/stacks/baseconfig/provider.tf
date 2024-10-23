provider "aws" {
  region = var.primary_region

  default_tags {
    tags = {
      DataClassification = var.data_classification
      Environment        = var.environment
      Programme          = "NPA"
      Project            = "Proxy"
      TagVersion         = "1"
      Tool               = "Terraform"
      Workspace          = terraform.workspace
    }
  }
}

provider "aws" {
  alias  = "us"
  region = var.global_region

  default_tags {
    tags = {
      DataClassification = var.data_classification
      Environment        = var.environment
      Programme          = "NPA"
      Project            = "Proxy"
      TagVersion         = "1"
      Tool               = "Terraform"
      Workspace          = terraform.workspace
    }
  }
}
