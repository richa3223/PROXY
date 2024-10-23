variable "firehose_name" {
  description = "A name for the Kenisis Firehose."
  type        = string
}

variable "firehose_destination" {
  description = "The destination to where the data is delivered."
  type        = string
}

variable "bucket_arn" {
  description = "The ARN of the destination S3 bucket."
  type        = string
}

variable "bucket_kms_key_arn" {
  description = "The ARN of the KMS key used to encrypt the S3 bucket."
  type        = string
}

variable "prefix" {
  description = "The s3 destination bucket prefix"
  type        = string
}

variable "buffer_interval" {
  description = "Buffer incoming data for the specified period of time, in seconds between 60 to 900, before delivering it to the destination."
  type        = number
  default     = 60
}

variable "buffer_size" {
  description = "Buffer incoming data to the specified size, in MBs, before delivering it to the destination."
  type        = number
  default     = 128
}

variable "dynamic_partitioning_enabled" {
  description = "Enables or disables dynamic partitioning."
  type        = bool
}

variable "log_retention_in_days" {
  description = "The number of days to retain log events in the log group."
  type        = number
}

variable "tags" {
  description = "A map of tags to assign to the resource."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "The name of the environment that the resources are to be deployed to."
  type        = string
}

variable "workspace" {
  description = "The name of the stack you are deploying the firehose to."
  type        = string
}

variable "kms_key_deletion_window_in_days" {
  type        = number
  description = "The firehose KMS key deletion window in days/"
}

variable "aws_region" {
  type        = string
  description = "The aws region."
}

variable "lambda_processor_arn" {
  description = "Optional Processor to be applied if data needs to be transformed"
  type        = string
  default     = ""
}
