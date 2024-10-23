terraform {
  required_version = ">= 1.4.5"
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.3"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 3.0"
    }
  }
}
