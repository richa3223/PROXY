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

variable "project" {
  type        = string
  description = "The name of the Project that was used to run bootstrap"
  default     = "pvrs"
}

variable "cidr_block_list" {
  type        = string
  description = "Comma separated list of CIDR blocks used to ssh on to the EC2 instances e.g. 31.94.28.248/32,31.94.64.160/32"
}
