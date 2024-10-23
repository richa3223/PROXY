locals {
  service_name = var.type_of_service == "aws" ? "com.amazonaws.${var.aws_region}.${var.endpoint_service_name}" : var.endpoint_service_name
}

resource "aws_vpc_endpoint" "interface" {
  vpc_id              = var.vpc_id
  service_name        = local.service_name
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.list_of_security_group_ids
  private_dns_enabled = var.private_dns_enabled
  subnet_ids          = var.list_of_endpoint_subnets
  tags                = merge({ "Name" = "${var.endpoint_service_name}-${var.workspace}" }, local.global_tags)
}
