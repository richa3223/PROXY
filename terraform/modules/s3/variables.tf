variable "bucket_name" {
  description = "name of the bucket"
  type        = string
}
variable "force_destroy" {
  description = "can bucket be destroyed if it contains files"
  type        = bool
  default     = false
}
variable "enable_bucket_versioning" {
  description = "enable versioning of files in s3"
  type        = bool
  default     = false
}
variable "tags" {
  description = "Tags passed into the module at point of creation"
  type        = map(string)
  default     = {}
}
variable "retention_days" {
  description = "The number of days from object creation till aws queues an object for removal and removes it asynchronously, permanently removing the object."
  type        = number
  default     = 1825 #5 years
}
variable "s3_iam_policy_document" {
  description = "The policy document applied to a specific bucket, if empty the default policy specified in data.tf will be applied"
  type        = string
  default     = null
}
variable "audit_bucket_id" {
  description = "audit bucket id"
  type        = string
}
variable "vpc_endpoint_id" {
  description = "vpc endpoint that this bucket should allow traffic from"
  type        = string
}
variable "workspace" {
  type        = string
  description = "The workspace name is used to prefix environments "
}