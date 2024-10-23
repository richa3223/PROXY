# Internal

resource "aws_route53_zone" "internal" {
  #checkov:skip=CKV2_AWS_39: Ensure Domain Name System (DNS) query logging is enabled for Amazon Route 53 hosted zones
  #checkov:skip=CKV2_AWS_38: Ensure Domain Name System Security Extensions (DNSSEC) signing is enabled for Amazon Route 53 public hosted zones
  name = "${local.common_stack_workspace}.internal"
  vpc {
    vpc_id = data.aws_vpc.proxy_vpc.id
  }

  tags = local.tags
}

resource "aws_route53_record" "master" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "master.${local.common_stack_workspace}.internal"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.load_testing_master_instance.private_ip]
}

resource "aws_route53_record" "worker" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "worker.${local.common_stack_workspace}.internal"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.load_testing_worker_instance.private_ip]
}

# Public

resource "aws_route53_record" "api_gateway" {
  zone_id = data.aws_route53_zone.primary_hosted_zone.zone_id
  name    = "mock.${data.aws_route53_zone.primary_hosted_zone.name}"
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.api_gateway_primary_domain_name.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api_gateway_primary_domain_name.regional_zone_id
    evaluate_target_health = false
  }
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
  zone_id         = data.aws_route53_zone.primary_hosted_zone.zone_id
}
