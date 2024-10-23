resource "aws_iam_role" "apigateway_role" {
  name               = "${local.workspace}-rest-apigw-sfn"
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

#API Gateway REST API
resource "aws_api_gateway_rest_api" "api" {
  name                         = "${local.workspace}-rest-api"
  description                  = "API Gateway for ${local.workspace}-api"
  disable_execute_api_endpoint = true

  lifecycle {
    create_before_destroy = true
  }

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.vrs_api__FHIR,
      aws_api_gateway_resource.vrs_api__R4,
      aws_api_gateway_resource.vrs_api__related_person,
      aws_api_gateway_method.vrs_related_person_get,
      aws_api_gateway_method.vrs_related_person_any,
      aws_api_gateway_integration.related_person_get_candidate_relationships_integration,
      aws_api_gateway_integration_response.vrs_related_person_response_200,
      aws_api_gateway_integration_response.vrs_related_person_response_any_405,
      aws_api_gateway_resource.vrs_api__questionnaire_response,
      aws_api_gateway_method.vrs_questionnaire_response_get,
      aws_api_gateway_method.vrs_questionnaire_response_any,
      aws_api_gateway_integration.questionnaire_response_integration,
      aws_api_gateway_integration_response.vrs_questionnaire_response_response_200,
      aws_api_gateway_integration_response.vrs_questionnaire_response_response_any_405,
      aws_api_gateway_gateway_response.gateway_response_400,
      aws_api_gateway_gateway_response.gateway_response_500
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_resource.vrs_api__FHIR,
    aws_api_gateway_resource.vrs_api__R4,
    aws_api_gateway_resource.vrs_api__related_person,
    aws_api_gateway_method.vrs_related_person_get,
    aws_api_gateway_method.vrs_related_person_any,
    aws_api_gateway_integration.related_person_get_candidate_relationships_integration,
    aws_api_gateway_integration_response.vrs_related_person_response_200,
    aws_api_gateway_integration_response.vrs_related_person_response_any_405,
    aws_api_gateway_resource.vrs_api__questionnaire_response,
    aws_api_gateway_method.vrs_questionnaire_response_get,
    aws_api_gateway_method.vrs_questionnaire_response_any,
    aws_api_gateway_integration.questionnaire_response_integration,
    aws_api_gateway_integration_response.vrs_questionnaire_response_response_200,
    aws_api_gateway_integration_response.vrs_questionnaire_response_response_any_405,
    aws_api_gateway_gateway_response.gateway_response_400,
    aws_api_gateway_gateway_response.gateway_response_500
  ]
}

resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.default.stage_name
  method_path = "*/*"
  settings {
    metrics_enabled      = true
    logging_level        = "INFO"
    caching_enabled      = true
    cache_data_encrypted = true
    #throttling_burst_limit = 500
    #throttling_rate_limit  = 100
  }

  depends_on = [
    aws_cloudwatch_log_group.api_gateway_default_log_group,
    aws_api_gateway_account.api_gateway_account,
    aws_iam_role_policy_attachment.api_gateway_role_cloudwatch_policy_attachment,
    aws_iam_role_policy_attachment.api_gateway_role_x_ray_policy
  ]
}

resource "aws_api_gateway_stage" "default" {
  # TODO: ensure certificate is added as part of the hardening
  #checkov:skip=CKV2_AWS_51: Ensure AWS API Gateway endpoints uses client certificate authentication
  # TODO: consider caching for better performance /takes longer to deploy /
  #checkov:skip=CKV_AWS_120: Ensure API Gateway caching is enabled
  #checkov:skip=CKV2_AWS_29: Ensure public API gateway are protected by WAF
  stage_name           = "default"
  rest_api_id          = aws_api_gateway_rest_api.api.id
  deployment_id        = aws_api_gateway_deployment.api_deployment.id
  xray_tracing_enabled = true
  #cache_cluster_enabled = true
  #cache_cluster_size    = "0.5"
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_default_log_group.arn
    format          = "$context.identity.sourceIp $context.identity.caller $context.identity.user [$context.requestTime] \"$context.httpMethod $context.resourcePath $context.protocol\" $context.status $context.responseLength $context.requestId"
  }
  depends_on = [aws_cloudwatch_log_group.api_gateway_default_log_group]
}

resource "aws_route53_record" "api_gateway" {
  count   = local.is_main_workspace ? 1 : 0
  zone_id = data.aws_route53_zone.primary_hosted_zone[0].zone_id
  name    = data.aws_route53_zone.primary_hosted_zone[0].name
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.api_gateway_primary_domain_name[0].regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api_gateway_primary_domain_name[0].regional_zone_id
    evaluate_target_health = false
  }
}

resource "aws_api_gateway_domain_name" "api_gateway_primary_domain_name" {
  count                    = local.is_main_workspace ? 1 : 0
  regional_certificate_arn = data.aws_acm_certificate.tls_certificate[0].arn
  domain_name              = data.aws_route53_zone.primary_hosted_zone[0].name
  security_policy          = "TLS_1_2"
  mutual_tls_authentication {
    truststore_uri = "s3://${module.mutual_tls_truststore_bucket.bucket_name}/truststore.pem"
  }

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_base_path_mapping" "api_gateway_primary_domain_name_mapping" {
  count       = local.is_main_workspace ? 1 : 0
  api_id      = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.default.stage_name
  domain_name = aws_api_gateway_domain_name.api_gateway_primary_domain_name[0].domain_name
}

data "aws_iam_policy_document" "policy_invoke_sfn_and_lambda" {
  statement {
    actions   = ["lambda:InvokeFunction"]
    effect    = "Allow"
    resources = [module.get_candidate_relationships.arn, module.create_access_request.arn]
  }
}

resource "aws_iam_policy" "api_gateway_invoke_sfn_and_lambda_policy" {
  name        = "${local.workspace}-api-gateway-invoke-sfn-and-lambda-policy"
  path        = "/"
  description = "IAM policy for api gateway to invoke Step Functions and Lambda"

  policy = data.aws_iam_policy_document.policy_invoke_sfn_and_lambda.json

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_role_policy_attachment" "api_gateway_role_invoke_sfn_and_lambda_policy" {
  policy_arn = aws_iam_policy.api_gateway_invoke_sfn_and_lambda_policy.arn
  role       = aws_iam_role.apigateway_role.name
}

resource "aws_api_gateway_resource" "vrs_api__FHIR" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "FHIR"
}

resource "aws_api_gateway_resource" "vrs_api__R4" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.vrs_api__FHIR.id
  path_part   = "R4"
  depends_on  = [aws_api_gateway_resource.vrs_api__FHIR]
}

resource "aws_api_gateway_gateway_response" "gateway_response_400" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  status_code   = "400"
  response_type = "DEFAULT_4XX"

  response_templates = {
    "application/json" = jsonencode({
      "issue" : [
        {
          "code" : "invalid",
          "details" : {
            "coding" : [
              {
                "code" : "BAD_REQUEST",
                "display" : "The request could not be processed.",
                "system" : "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                "version" : "1"
              }
            ]
          },
          "diagnostics" : "The supplied input is not a valid FHIR QuestionnaireResponse.",
          "severity" : "error"
        }
      ],
      "resourceType" : "OperationOutcome"
    })
  }
}

resource "aws_api_gateway_gateway_response" "gateway_response_500" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  status_code   = "500"
  response_type = "DEFAULT_5XX"

  response_templates = {
    "application/json" = jsonencode({
      "issue" : [
        {
          "code" : "invalid",
          "details" : {
            "coding" : [
              {
                "code" : "SERVER_ERROR",
                "display" : "Failed to generate response",
                "system" : "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                "version" : "1"
              }
            ]
          },
          "diagnostics" : "Internal Server Error - Failed to generate response",
          "severity" : "error"
        }
      ],
      "resourceType" : "OperationOutcome"
    })
  }
}
