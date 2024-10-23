locals {
  workspace                 = lower(terraform.workspace)
  number_of_public_subnets  = element(var.aws_azs, 0) == "" ? length(data.aws_availability_zones.azs.names) * var.internet_gateway_enabled : length(var.aws_azs) * var.internet_gateway_enabled
  number_of_private_subnets = element(var.aws_azs, 0) == "" ? length(data.aws_availability_zones.azs.names) : length(var.aws_azs)
  list_of_aws_az = split(
    ",",
    element(var.aws_azs, 0) == "" ? join(",", data.aws_availability_zones.azs.names) : join(",", var.aws_azs),
  )
  list_of_cidr_block_for_public_subnets = [
    for subnet in null_resource.public-cidr-helper : subnet.triggers.list_of_cidr_block_for_public_subnets
  ]
  list_of_cidr_block_for_private_subnets = [
    for subnet in null_resource.private-cidr-helper : subnet.triggers.list_of_cidr_block_for_private_subnets
  ]

  #   # for additional subnet
  current_subnet_length = (1 * var.internet_gateway_enabled + 1) * length(var.aws_azs)
  list_of_cidr_block_for_additional_subnet_public_subnets = [
    for subnet in null_resource.public-cidr-additional-subnet-helper :
    subnet.triggers.list_of_cidr_block_for_public_subnets
  ]
  list_of_cidr_block_for_additional_subnet_private_subnets = [
    for subnet in null_resource.private-cidr-additional-subnet-helper :
    subnet.triggers.list_of_cidr_block_for_private_subnets
  ]


  #nacl
  private_inbound_acl_rules = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_block  = var.vpc_cidr
    },
    {
      rule_number = 110
      rule_action = "allow"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_block  = var.vpc_cidr
    },
    {
      rule_number = 120
      rule_action = "allow"
      from_port   = 1024
      # Allows inbound return traffic from the NAT device in the public subnet for requests originating in the private subnet
      to_port    = 65535 #Ephemeral Port range is different for different OS
      protocol   = "tcp"
      cidr_block = "0.0.0.0/0"
    },
  ]
  private_outbound_acl_rules = [
    {
      rule_number = 130
      rule_action = "allow"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
    {
      rule_number = 140
      rule_action = "allow"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
    {
      rule_number = 150
      rule_action = "allow"
      from_port   = 1024
      to_port     = 65535
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
  ]
  public_inbound_acl_rules = [
    {
      rule_number = 100
      rule_action = "allow"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
    {
      rule_number = 110
      rule_action = "allow"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
    {
      rule_number = 120
      rule_action = "allow"
      from_port   = 1024
      # Allows inbound return traffic from the NAT device in the public subnet for requests originating in the private subnet
      to_port    = 65535 #Ephemeral Port range is different for different OS
      protocol   = "tcp"
      cidr_block = "0.0.0.0/0"
    },
  ]
  public_outbound_acl_rules = [
    {
      rule_number = 130
      rule_action = "allow"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
    {
      rule_number = 140
      rule_action = "allow"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
    {
      rule_number = 150
      rule_action = "allow"
      from_port   = 1024
      to_port     = 65535
      protocol    = "tcp"
      cidr_block  = "0.0.0.0/0"
    },
  ]

  ###########################################
  # KMS locals
  ###########################################
  kms_key_deletion_duration = 14

  tags = {
    Environment = var.environment
    Programme   = "NPA"
    Project     = "Proxy"
    TagVersion  = "1"
    Tool        = "Terraform"
    Workspace   = terraform.workspace
    Stack       = "common"
  }

  ###########################################
  # Event Bridge locals
  ###########################################
  event_schema_directory   = "${path.module}/../../../events/"
  event_schema_file_names  = fileset(local.event_schema_directory, "*.json")
  match_all_events_pattern = jsonencode({ "source" : [{ "prefix" : "" }] })

  interface_endpoint_services = ["events", "secretsmanager", "logs", "kms", "ssm", "lambda", "sts", "states"]
}
