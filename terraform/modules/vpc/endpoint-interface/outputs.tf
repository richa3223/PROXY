output "id" {
  value = aws_vpc_endpoint.interface.id
}

output "state" {
  value = aws_vpc_endpoint.interface.state
}

output "network_interface_ids" {
  value = aws_vpc_endpoint.interface.network_interface_ids
}

output "dns_entry" {
  value = aws_vpc_endpoint.interface.dns_entry
}

output "primary_dns_name" {
  value = aws_vpc_endpoint.interface.dns_entry[0]["dns_name"]
}

output "primary_dns_zone_id" {
  value = aws_vpc_endpoint.interface.dns_entry[0]["hosted_zone_id"]
}
