variable "project" {
  default     = "pvrs"
  description = "Project Name"
  type        = string
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

variable "use_shared_common_stack" {
  type        = bool
  description = "Should this stack use the resources in the shared common stack, or has the common stack been deployed to a new workspace."
}

variable "main_workspace" {
  type        = string
  description = "The name of the main workspace"
}

variable "get_email_template_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "create_merged_email_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "send_gp_email_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "ods_lookup_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "SEND_NHS_MAIL_CREDENTIALS" {
  type        = string
  description = "Send NHS Mail credentials to access the API"
  sensitive   = true
}

variable "ODS_LOOKUP_CREDENTIALS" {
  type        = string
  description = "ODS Lookup credentials to access the API"
  sensitive   = true
}

variable "ods_lookup_base_url" {
  type        = string
  description = "ODS lookup URL for retrieving GP ODS information"
}
