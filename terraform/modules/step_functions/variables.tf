variable "workspace" {
  type        = string
  description = "The workspace name is used to prefix resources"
}

variable "environment" {
  type        = string
  description = "The environment name is used to prefix resources"
}

variable "step_functions_name" {
  type        = string
  description = "The name of the step function"
}

variable "aws_region" {
  type        = string
  description = "The AWS region that resources are being created in"
}

variable "kms_key_deletion_duration" {
  type        = number
  description = "The number of days after which the key is deleted"
}

variable "state_machine_definition" {
  type        = string
  description = "The state machine definition (JSON string)"
}

variable "state_machine_type" {
  type        = string
  description = "The type of the state machine"
  default     = "EXPRESS"
}

variable "lambda_arn_list" {
  type        = list(string)
  description = "The list of lambda arns to be used in the step function"
  default     = []
}

variable "state_machine_arn_list" {
  type        = list(string)
  description = "The list of state machine arns to be used in the step function"
  default     = []
}
