# Shield Advanced DDOS protection for the VPC Elastic IPs, currently only one is created
resource "aws_shield_protection" "vpc_elastic_ip_protection" {
  name         = "${var.name}-vpc-elastic-ip-protection"
  resource_arn = "arn:aws:ec2:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:eip-allocation/${aws_eip.nat[0].id}"
}
