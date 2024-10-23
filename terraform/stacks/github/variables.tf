# tflint-ignore: terraform_unused_declarations # reason: required by makefile
variable "environment" {
  description = "Environment"
  type        = string
}

# tflint-ignore: terraform_unused_declarations # reason: required by makefile
variable "use_shared_common_stack" {
  type        = bool
  description = "Should this stack use the resources in the shared common stack, or has the common stack been deployed to a new workspace."
}

# tflint-ignore: terraform_unused_declarations # reason: required by makefile
variable "main_workspace" {
  type        = string
  description = "The name of the main workspace"
}
