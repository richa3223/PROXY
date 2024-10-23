variable "project" {
  default     = "pvrs"
  description = "Project Name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "PDS_CREDENTIALS" {
  type        = string
  description = "PDS credentials to access the API"
  sensitive   = true
}

variable "process_validation_result_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "pds_get_patient_details_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "validate_eligibility_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "verify_parameters_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "validate_relationship_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "relationship_lookup_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "pds_access_token_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "create_access_request_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "get_candidate_relationships_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "raise_certificate_alert_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "slack_alerts_alert_lambda_memory_size" {
  type        = number
  description = "Amount of memory in MB your Lambda Function can use at runtime"
}

variable "pds_auth_url" {
  type        = string
  description = "PDS URL for requesting auth token"
}

variable "pds_base_url" {
  type        = string
  description = "PDS URL for making regular requests"
}

variable "use_shared_common_stack" {
  type        = bool
  description = "Should this stack use the resources in the shared common stack, or has the common stack been deployed to a new workspace."
}

variable "main_workspace" {
  type        = string
  description = "The name of the main workspace"
}

variable "MTLS_CERTIFICATE" {
  type        = string
  description = "MTLS Certificate for API Gateway"
  sensitive   = true
}

variable "SEND_NHS_MAIL_CREDENTIALS" {
  type        = string
  description = "Send NHS Mail credentials to access the API"
  sensitive   = true
}

variable "SLACK_WEBHOOK" {
  type        = string
  description = "Slack credentials for alerts"
  sensitive   = true
}

variable "TEAM_EMAIL" {
  type        = string
  description = "Team email"
  sensitive   = true
}

variable "dynamodb_ttl" {
  type        = number
  description = "Dynamo DB record Time To Live in seconds"
}
