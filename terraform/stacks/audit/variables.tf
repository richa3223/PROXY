variable "environment" {
  description = "Environment"
  type        = string
}

variable "project" {
  type        = string
  description = "The name of the Project that was used to run bootstrap"
  default     = "pvrs"
}

variable "use_shared_common_stack" {
  type        = bool
  description = "Should this stack use the resources in the shared common stack, or has the common stack been deployed to a new workspace."
}

variable "main_workspace" {
  type        = string
  description = "The name of the main workspace"
}

variable "redact_sensitive_data_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}
variable "legal_direction" {
  type        = bool
  description = "Whether we have legal directtion to hold sensitive data, True if we do, False if we don't"
}
