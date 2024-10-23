resource "null_resource" "public-cidr-helper" {
  count = local.number_of_public_subnets

  triggers = {
    list_of_cidr_block_for_public_subnets = cidrsubnet(var.vpc_cidr, 4, count.index)
  }
}

resource "null_resource" "private-cidr-helper" {
  count = local.number_of_private_subnets

  triggers = {
    list_of_cidr_block_for_private_subnets = cidrsubnet(var.vpc_cidr, 4, count.index + local.number_of_public_subnets)
  }
}

module "vpc" {
  source = "../../modules/vpc"

  name = "${local.workspace}-vpc"
  cidr = var.vpc_cidr

  azs                        = local.list_of_aws_az
  private_subnets            = local.list_of_cidr_block_for_private_subnets
  private_inbound_acl_rules  = local.private_inbound_acl_rules
  private_outbound_acl_rules = local.private_outbound_acl_rules
  public_subnets             = local.list_of_cidr_block_for_public_subnets
  public_inbound_acl_rules   = local.public_inbound_acl_rules
  public_outbound_acl_rules  = local.public_outbound_acl_rules

  associate_s3_endpoint_with_private_route_table = 1
  associate_s3_endpoint_with_public_route_table  = 1
  enable_s3_endpoint                             = 1

  enable_dns_hostnames    = true
  enable_nat_gateway      = true
  map_public_ip_on_launch = false
  single_nat_gateway      = true
  create_igw              = var.internet_gateway_enabled == 1 ? true : false

  enable_flow_log                                 = true
  create_flow_log_cloudwatch_log_group            = true
  create_flow_log_cloudwatch_iam_role             = true
  flow_log_cloudwatch_log_group_retention_in_days = 7
  flow_log_cloudwatch_log_group_kms_key_id        = var.enable_kms_encryption ? aws_kms_key.cloudwatch_log_key.arn : null
  global_tags                                     = var.global_tags
}

##### Additional Subnet

resource "null_resource" "public-cidr-additional-subnet-helper" {
  count = var.number_of_additional_public_subnets

  triggers = {
    list_of_cidr_block_for_public_subnets = cidrsubnet(var.vpc_cidr, 4, count.index + local.current_subnet_length)
  }
}

resource "null_resource" "private-cidr-additional-subnet-helper" {
  count = var.number_of_additional_private_subnets

  triggers = {
    list_of_cidr_block_for_private_subnets = cidrsubnet(
      var.vpc_cidr,
      4,
      count.index + var.number_of_additional_public_subnets + local.current_subnet_length,
    )
  }
}

module "additional_subnet" {
  # kept for testing vpc endpoint creation
  count = 0

  source                                         = "../../modules/vpc/additional-subnet"
  vpc_id                                         = module.vpc.vpc_id
  associate_nat_gateway_with_private_route_table = 1
  vpc_nat_gateway_ids                            = module.vpc.natgw_ids
  create_nacl_for_private_subnets                = 1
  internet_gateway_id                            = module.vpc.igw_id
  number_of_public_subnets                       = var.number_of_additional_public_subnets
  number_of_private_subnets                      = var.number_of_additional_private_subnets
  list_of_aws_az                                 = local.list_of_aws_az
  list_of_cidr_block_for_public_subnets          = local.list_of_cidr_block_for_additional_subnet_public_subnets
  list_of_cidr_block_for_private_subnets         = local.list_of_cidr_block_for_additional_subnet_private_subnets
  public_ip_on_launch                            = true
  workspace                                      = local.workspace
}
