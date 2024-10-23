# create public subnets
resource "aws_subnet" "public" {
  count                   = var.number_of_public_subnets
  vpc_id                  = var.vpc_id
  cidr_block              = element(var.list_of_cidr_block_for_public_subnets, count.index)
  availability_zone       = element(var.list_of_aws_az, count.index)
  map_public_ip_on_launch = var.public_ip_on_launch
  tags                    = merge({ "Name" = "public-${var.workspace}" }, var.other_public_subnet_tags, local.global_tags)

  lifecycle {
    ignore_changes = [cidr_block]
  }
}

#create route table for private subnets
resource "aws_route_table" "public" {
  count  = var.number_of_public_subnets
  vpc_id = var.vpc_id
  tags   = merge({ "Name" = "public-${var.workspace}" }, local.global_tags)
}

#associate public subnets with public route table which has access through intrnet gateway
resource "aws_route_table_association" "public" {
  count          = var.number_of_public_subnets
  route_table_id = aws_route_table.public[count.index].id
  subnet_id      = aws_subnet.public[count.index].id
}

# grant the VPC internet access on its public route table
resource "aws_route" "internet_access" {
  count                  = var.number_of_public_subnets
  route_table_id         = aws_route_table.public[count.index].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = var.internet_gateway_id
}

#Create NACL
resource "aws_network_acl" "public" {
  count      = var.number_of_public_subnets > 0 ? var.create_nacl_for_public_subnets : 0
  vpc_id     = var.vpc_id
  subnet_ids = [for subnet in aws_subnet.public : subnet.id]
  tags       = merge({ "Name" = "public-subnets-${var.workspace}" }, local.global_tags)
}
