# subnet module outputs #

output "public_subnet_ids" {
  value = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  value = [for subnet in aws_subnet.private : subnet.id]
}

output "public_subnet_cidrs" {
  value = [for subnet in aws_subnet.public : subnet.cidr_block]
}

output "private_subnet_cidrs" {
  value = [for subnet in aws_subnet.private : subnet.cidr_block]
}

output "public_nacl_id" {
  value = element([for nacl in aws_network_acl.public : nacl.id], 0)
}

output "private_nacl_id" {
  value = element([for nacl in aws_network_acl.private : nacl.id], 0)
}

output "private_route_table" {
  value = [for table in aws_route_table.private : table.id]
}

output "public_route_table" {
  value = [for table in aws_route_table.public : table.id]
}

output "public_az" {
  value = [for subnet in aws_subnet.public : subnet.availability_zone]
}

output "private_az" {
  value = [for subnet in aws_subnet.private : subnet.availability_zone]
}
