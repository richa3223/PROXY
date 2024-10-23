terraform {
  required_version = ">= 1.4.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.54.1"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5.1"
    }
  }
  backend "s3" {
    region = local.aws_region
  }
}
