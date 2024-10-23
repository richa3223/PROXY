output "private_subnet" {
  value = local.list_of_cidr_block_for_private_subnets
}

output "public_subnet" {
  value = local.list_of_cidr_block_for_public_subnets
}

output "additional_private_subnet" {
  value = local.list_of_cidr_block_for_additional_subnet_private_subnets
}

output "additional_public_subnet" {
  value = local.list_of_cidr_block_for_additional_subnet_public_subnets
}
