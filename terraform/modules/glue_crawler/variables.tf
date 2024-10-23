variable "database_name" {
  description = "The name of the database that the crawler should store indexing/schema results to"
  type        = string
}

variable "crawler_name" {
  description = "The name of the crawler"
  type        = string
}

variable "table_prefix" {
  description = "Prefix that should be added to a glue table"
  type        = string
}

variable "bucket_arn" {
  description = "The arn of the bucket to be crawled"
  type        = string
}

variable "bucket_name" {
  description = "The name of the bucket to be crawled"
  type        = string
}

variable "bucket_kms_key_arn" {
  description = "The ARN of the KMS key used to encrypt the S3 bucket."
  type        = string
}

variable "environment" {
  description = "The name of the environment that the resources are to be deployed to."
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the resource."
  type        = map(string)
  default     = {}
}

variable "aws_region" {
  type        = string
  description = "The aws region."
  default     = "eu-west-2"
}

variable "kms_key_deletion_window_in_days" {
  type        = number
  description = "The firehose KMS key deletion window in days/"
  default     = 14
}

variable "workspace" {
  description = "The name of the stack you are deploying the firehose to."
  type        = string
}
