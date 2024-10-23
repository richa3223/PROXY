resource "aws_acm_certificate" "tls_certificate" {
  domain_name               = aws_route53_zone.primary_hosted_zone.name
  subject_alternative_names = [aws_route53_zone.primary_hosted_zone.name]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Will hang until NS records are mapped by the DNS team
# Can be commented out to create Hosting Zone with NS records
resource "aws_acm_certificate_validation" "tls_cert_validation" {
  count                   = var.environment == "poc" ? 0 : 1
  certificate_arn         = aws_acm_certificate.tls_certificate.arn
  validation_record_fqdns = [for record in aws_route53_record.acm_verification_record : record.fqdn]
}
