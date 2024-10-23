
# Below endpoints are needed to run the RUN command without routing the request via Internet
resource "aws_security_group" "endpoints" {
  # The reason for this false positive is that the security group used in module
  # There is an open issue https://github.com/bridgecrewio/checkov/issues/3010
  #checkov:skip=CKV2_AWS_5: SG is attached to VPC endpoints
  name        = "proxy-app-vpc-endpoint-sg"
  description = "security group for vpc-endpoints"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_security_group_rule" "allow_egress_from_vpc_endpoints" {
  # TODO: implement
  #checkov:skip=CKV_AWS_23: Ensure every security groups rule has a description
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.endpoints.id
}


resource "aws_security_group_rule" "allow_ingress_from_vpc_endpoints" {
  # TODO: implement
  #checkov:skip=CKV_AWS_23: Ensure every security groups rule has a description
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = [module.vpc.vpc_cidr_block]
  security_group_id = aws_security_group.endpoints.id
}

# Create an interface endpoints
module "vpc-interfaces-endpoints" {
  for_each                   = toset(local.interface_endpoint_services)
  source                     = "../../modules/vpc/endpoint-interface"
  aws_region                 = var.region
  vpc_id                     = module.vpc.vpc_id
  type_of_service            = "aws"
  endpoint_service_name      = each.value
  private_dns_enabled        = true
  list_of_security_group_ids = [aws_security_group.endpoints.id]
  list_of_endpoint_subnets   = module.vpc.private_subnets
  workspace                  = local.workspace
  global_tags                = var.global_tags
}
