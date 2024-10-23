resource "aws_route53_zone" "primary_hosted_zone" {
  #TODO: NPA-2140, NPA-2141
  #checkov:skip=CKV2_AWS_38: Ensure Domain Name System Security Extensions (DNSSEC) signing is enabled for Amazon Route 53 public hosted zones
  #checkov:skip=CKV2_AWS_39: Ensure Domain Name System (DNS) query logging is enabled for Amazon Route 53 hosted zones
  name = "validated-relationships-service-${var.environment}.national.nhs.uk"
  tags = {
    Name = "primary-hosted-zone"
  }
}

output "rever_zone_name_servers" {
  description = "The Name Servers for the public hosted zones created by AWS"
  value       = aws_route53_zone.primary_hosted_zone.name_servers
}

resource "aws_route53_record" "acm_verification_record" {
  for_each = {
    for dvo in aws_acm_certificate.tls_certificate.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.primary_hosted_zone.zone_id
}
