# Shield Advanced DDOS protection for the Route53 internal hosted zone
resource "aws_shield_protection" "internal_hosted_zone_protection" {
  name         = "${var.environment}-${local.workspace}-internal-hosted-zone-protection"
  resource_arn = aws_route53_zone.internal.arn
}
