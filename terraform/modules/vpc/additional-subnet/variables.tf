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

variable "list_of_aws_az" {
  description = "The AZ for the subnets"
  type        = list(string)
}

variable "vpc_id" {
  description = "The VPC id for the subnets to associate with"
  type        = string
}

variable "number_of_public_subnets" {
  description = "Number of public subnets to be created.Variable 'internet_gateway_id' must be provided"
  type        = number
  default     = 0
}

variable "internet_gateway_id" {
  description = "The id of the specific Internet Gateway to retrieve. Must when `number_of_public_subnets` > 0"
  type        = string
  default     = ""
}

variable "list_of_cidr_block_for_public_subnets" {
  description = "list of CIDR block for the public subnets"
  type        = list(string)
}

variable "public_ip_on_launch" {
  description = "Specify true to indicate that instances launched into the subnet should be assigned a public IP address"
  type        = bool
  default     = false
}

variable "create_nacl_for_public_subnets" {
  description = "create seperate NACL for the public subnets.If '0' , default NACL is assigned to the subnets"
  type        = number
  default     = 1
}

variable "number_of_private_subnets" {
  description = "Number of private subnets to be created"
  type        = number
  default     = 0
}

variable "list_of_cidr_block_for_private_subnets" {
  description = "list of CIDR block for the private subnets"
  type        = list(string)
}

variable "associate_nat_gateway_with_private_route_table" {
  description = "Specify 1 to indicate that instances launched into the private subnet should haveaccess to outbound internet"
  type        = number
  default     = 0
}

variable "vpc_nat_gateway_ids" {
  description = "list of NAT Gateway ids to associate with private subnets.Must when `associate_nat_gateway_with_private_route_table` is true"
  type        = list(string)
  default     = []
}

variable "create_nacl_for_private_subnets" {
  description = "create seperate NACL for the private subnets.If '0', default NACL is assigned to the subnets"
  type        = number
  default     = 1
}

variable "other_public_subnet_tags" {
  description = "Addtioanl public subnet tags to be applied to created resources"
  type        = map(string)
  default     = {}
}

variable "other_private_subnet_tags" {
  description = "Addtioanl private subnet tags to be applied to created resources"
  type        = map(string)
  default     = {}
}

variable "workspace" {
  description = "unique tag/name identifier for the resources created"
  type        = string
  default     = ""
}
