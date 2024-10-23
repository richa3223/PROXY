variable "environment" {
  description = "Environment"
  type        = string
}

variable "primary_region" {
  type        = string
  description = "aws region for application deployment"
  default     = "eu-west-2"
}

variable "global_region" {
  type        = string
  description = "aws region for Global AWS Resources"
  default     = "us-east-1"
}

variable "project" {
  type        = string
  description = "The project name for the deployment"
  default     = "pvrs"
}

variable "data_classification" {
  type        = string
  description = "The type of data that this is project is consuming"
  default     = "1"
}

# TODO: This must be tied down more!!!!
variable "allowed_repos" {
  description = "Allowed Repos to use OIDC Provider"
  type        = set(string)
  default     = ["repo:NHSDigital/proxy-validated-relationships-service:*"] # allow any branch, pull request merge branch, or environment from the repo to assume the AWS role
}
variable "client_id_list" {
  description = "List of client IDs (also known as audiences) for the IAM OIDC provider. Defaults to STS service if not values are provided"
  type        = list(string)
  default     = []
}
variable "url" {
  description = "The URL of the identity provider. Corresponds to the iss claim"
  type        = string
  default     = "https://token.actions.githubusercontent.com"
}

variable "account_id" {
  type        = map(string)
  description = "The AWS account IDs"

  default = {
    nhsd-identities = "347250048819"
  }
}
