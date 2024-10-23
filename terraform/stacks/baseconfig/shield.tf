# Creates AWS Shield Advanced subscription (DDOS protection)
# https://docs.aws.amazon.com/cli/latest/reference/shield/create-subscription.html
# Note: This is a one-time operation and should not be run again if the subscription is already active.
# Shield Advanced can not be removed once it is created. To remove it you must contact AWS support.
resource "null_resource" "aws_shield_create_subscription" {
  provisioner "local-exec" {
    interpreter = ["bash", "-x", "-c"]
    command     = <<EOF
if [ "$(aws shield get-subscription-state --query SubscriptionState --output text)" == INACTIVE ]; then
  echo Creating AWS Shield Advanced subscription ...
  aws shield create-subscription
  echo Done.
else
  echo AWS Shield Advanced subscription is already active.
fi
EOF
  }
}

# Shield Advanced DDOS protection for the Route53 primary hosted zone
resource "aws_shield_protection" "primary_hosted_zone_protection" {
  depends_on   = [null_resource.aws_shield_create_subscription]
  name         = "primary-hosted-zone-protection"
  resource_arn = aws_route53_zone.primary_hosted_zone.arn
}
