variable "project" {
  type        = string
  description = "The short-name assigned to the project"
  default     = "pvrs"
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "region" {
  description = "aws region"
  default     = "eu-west-2"
  type        = string
}

variable "main_workspace" {
  description = "The main workspace"
  type        = string
}

variable "use_shared_common_stack" {
  type        = bool
  description = "Should this stack use the resources in the shared common stack, or has the common stack been deployed to a new workspace."
}

variable "SPLUNK_HEC_TOKEN" {
  description = "Splunk HEC Token"
  type        = string
  sensitive   = true
}

variable "force_destroy_bucket" {
  description = "Force destroy the bucket"
  type        = bool
  default     = false
}
