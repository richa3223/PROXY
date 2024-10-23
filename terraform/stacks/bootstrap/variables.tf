variable "project" {
  type        = string
  description = "The name of the Project we are bootstrapping tfscaffold for"
  default     = "pvrs"
}

variable "region" {
  type        = string
  description = "The AWS Region into which we are bootstrapping tfscaffold"
  default     = "eu-west-2"
}
