variable "aws_region" {
  description = "AWS region create resources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "The VPC id for the endpoint to associate with"
  type        = string
}

variable "type_of_service" {
  description = "Type of endpoint interface service. 'aws' or 'custom'"
  type        = string
  default     = "aws"
}

variable "endpoint_service_name" {
  description = "Endpoint interface service name. if aws, one of 'kms','ec2','ec2messages','elasticloadbalancing','kinesis-streams','servicecatalog','sns' and 'ssm' OR Custom service name"
  type        = string
}

variable "private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC"
  type        = bool
  default     = false
}

variable "list_of_security_group_ids" {
  description = "list of security groups to allow access to endpoint"
  type        = list(string)
}

variable "list_of_endpoint_subnets" {
  description = "List of subnets to associate with the endpoints"
  type        = list(string)
}

variable "workspace" {
  description = "unique tag/name identifier for the resources created"
  type        = string
}

################################################################################
# Tags
################################################################################

variable "tag_version" {
  description = "tag versions"
  type        = string
  default     = "v1.0.0"
}

variable "developer_dl" {
  description = "developer team DL"
  type        = string
  default     = ""
}

variable "tech_ops" {
  description = "tech ops team DL"
  type        = string
  default     = ""
}

variable "global_tags" {
  description = "Tags to apply to all taggable resources"
  type        = map(any)
  default = {
    "terraform" = "true"
  }
}
