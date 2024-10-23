terraform {
  required_version = ">= 1.4.5"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "6.2.1"
    }
  }
  backend "s3" {
    region = local.aws_region
  }
}

provider "github" {
  owner = "NHSDigital"
}
