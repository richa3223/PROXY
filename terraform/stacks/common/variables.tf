variable "project" {
  type        = string
  description = "The short-name assigned to the project"
  default     = "pvrs"
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "global_tags" {
  description = "Tags to apply to all taggable resources"
  type        = map(any)
  default     = {}
}

variable "region" {
  description = "aws region"
  default     = "eu-west-2"
  type        = string
}

variable "vpc_cidr" {
  description = "cidr block for aws vpc"
  default     = "10.5.0.0/16"
  type        = string
}

variable "aws_azs" {
  description = "avavilability zones associated with subnets"
  type        = list(string)
  default     = ["eu-west-2a", "eu-west-2b", "eu-west-2c"]
}

variable "internet_gateway_enabled" {
  description = "enable internet gateway"
  type        = number
  default     = 1
}

variable "number_of_additional_public_subnets" {
  description = "additional public subnets needed"
  type        = number
  default     = 0
}

variable "number_of_additional_private_subnets" {
  description = "additional private subnets needed"
  type        = number
  default     = 0
}

variable "enable_kms_encryption" {
  description = "enable kms encryption"
  type        = bool
  default     = true
}
