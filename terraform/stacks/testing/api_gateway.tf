resource "aws_iam_role" "apigateway_role" {
  name               = "${local.workspace}-mock-rest-apigw"
  assume_role_policy = data.aws_iam_policy_document.apigw_assume.json
}

data "aws_iam_policy_document" "apigw_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}

# Mock API Gateway REST API
resource "aws_api_gateway_rest_api" "api_gateway" {
  name                         = "${local.workspace}-mock-rest-api"
  description                  = "Mock API Gateway for ${local.workspace}-api"
  disable_execute_api_endpoint = true

  lifecycle {
    create_before_destroy = true
  }

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_stage" "default" {
  #checkov:skip=CKV2_AWS_4: Ensure API Gateway stage have logging level defined as appropriate
  #checkov:skip=CKV_AWS_76: Ensure API Gateway has Access Logging enabled
  #checkov:skip=CKV2_AWS_51: Ensure AWS API Gateway endpoints uses client certificate authentication
  #checkov:skip=CKV_AWS_120: Ensure API Gateway caching is enabled
  #checkov:skip=CKV2_AWS_29: Ensure public API gateway are protected by WAF

  stage_name           = "default"
  rest_api_id          = aws_api_gateway_rest_api.api_gateway.id
  deployment_id        = aws_api_gateway_deployment.api_deployment.id
  xray_tracing_enabled = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.mock_api_gateway_default_log_group.arn
    format          = "$context.identity.sourceIp $context.identity.caller $context.identity.user [$context.requestTime] \"$context.httpMethod $context.resourcePath $context.protocol\" $context.status $context.responseLength $context.requestId"
  }
  depends_on = [aws_cloudwatch_log_group.mock_api_gateway_default_log_group]
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  lifecycle {
    create_before_destroy = true
  }

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.cache_pds_response,
      aws_api_gateway_method.cache_pds_response,
      aws_api_gateway_integration.cache_pds_response,
    ]))
  }

  depends_on = [
    aws_api_gateway_resource.cache_pds_response,
    aws_api_gateway_method.cache_pds_response,
    aws_api_gateway_integration.cache_pds_response,
  ]

}

resource "aws_api_gateway_base_path_mapping" "api_gateway_primary_domain_name_mapping" {
  api_id      = aws_api_gateway_rest_api.api_gateway.id
  stage_name  = aws_api_gateway_stage.default.stage_name
  domain_name = aws_api_gateway_domain_name.api_gateway_primary_domain_name.domain_name
}

resource "aws_api_gateway_domain_name" "api_gateway_primary_domain_name" {
  regional_certificate_arn = aws_acm_certificate.tls_certificate.arn
  domain_name              = "mock.${data.aws_route53_zone.primary_hosted_zone.name}"
  security_policy          = "TLS_1_2"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_acm_certificate_validation" "tls_cert_validation" {
  certificate_arn         = aws_acm_certificate.tls_certificate.arn
  validation_record_fqdns = [for record in aws_route53_record.acm_verification_record : record.fqdn]
}

resource "aws_acm_certificate" "tls_certificate" {
  domain_name               = "mock.${data.aws_route53_zone.primary_hosted_zone.name}"
  subject_alternative_names = ["mock.${data.aws_route53_zone.primary_hosted_zone.name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_resource" "cache_pds_response" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "cache_pds_response" {
  #checkov:skip=CKV2_AWS_53: Ensure AWS API gateway request is validated #reason: validation done by API target
  #checkov:skip=CKV_AWS_59: Ensure there is no open access to back-end resources through API #reason: validation done by API target 
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.cache_pds_response.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cache_pds_response" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_method.cache_pds_response.resource_id
  http_method = aws_api_gateway_method.cache_pds_response.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.cache_pds_response.invoke_arn
}

resource "aws_lambda_permission" "cache_pds_response" {
  statement_id  = "cache_pds_response"
  action        = "lambda:InvokeFunction"
  function_name = module.cache_pds_response.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}
