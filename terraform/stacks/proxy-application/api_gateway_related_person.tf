resource "aws_api_gateway_resource" "vrs_api__related_person" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.vrs_api__R4.id
  path_part   = "RelatedPerson"
  depends_on  = [aws_api_gateway_resource.vrs_api__R4]
}

# ---------
# GET /RelatedPerson
# ---------

resource "aws_api_gateway_method" "vrs_related_person_get" {
  # TODO: ensure protection is enabled as part of APIM integration
  #checkov:skip=CKV2_AWS_53: Ensure AWS API gateway request is validated
  #checkov:skip=CKV_AWS_59: Ensure there is no open access to back-end resources through API
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.vrs_api__related_person.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "related_person_get_candidate_relationships_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__related_person.id
  credentials = aws_iam_role.apigateway_role.arn

  http_method             = "GET"
  integration_http_method = "POST"
  type                    = "AWS"

  uri              = module.get_candidate_relationships.invoke_arn
  content_handling = null

  request_templates = {
    "application/json" = jsonencode(
      {
        "proxyNhsNumber" : "$input.params('identifier')",
        "patientNhsNumber" : "$input.params('patient:identifier')",
        "_include" : "$input.params('_include')",
        "accesstoken.auth_level" : "$input.params().header.get('accesstoken.auth_level')",
        "accesstoken.auth_user_id" : "$input.params().header.get('accesstoken.auth_user_id')",
        "correlationId" : "$input.params().header.get('X-Correlation-ID')",
        "originalRequestUrl" : "$input.params().header.get('Proxy-URL')",
        "requestId" : "$input.params().header.get('X-Request-ID')",
      }
    )
  }
}

# Here we override API response accordingly
# https://docs.aws.amazon.com/lambda/latest/api/API_Invoke.html
resource "aws_api_gateway_integration_response" "vrs_related_person_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__related_person.id
  http_method = aws_api_gateway_method.vrs_related_person_get.http_method
  status_code = aws_api_gateway_method_response.vrs_related_person_response_200.status_code

  # Only set the response template for a 200 status code, we mirror the request headers in the response
  # Always return the body from the lambda function
  # Override the status code to the one returned from the lambda function as a 400 bad request is a 200 lambda response
  response_templates = {
    "application/json" = <<EOF
#set ($status = $input.path('$.status_code'))
#set($context.responseOverride.status = $status)

#if($status == 200)
    #set($headerObject = $input.params().header)
    #if($headerObject.containsKey('X-Correlation-ID'))
        #set($correlationIdHeader = $headerObject.get('X-Correlation-ID'))
        #set($context.responseOverride.header.X-Correlation-ID = $correlationIdHeader)
    #end

    #if(($headerObject.containsKey('X-Request-ID')) && ($headerObject.get('X-Request-ID') != ""))
        #set($requestIdHeader = $headerObject.get('X-Request-ID'))
        #set($context.responseOverride.header.X-Request-ID = $requestIdHeader)
    #end
#end
$input.json('$.body')
EOF
  }

  depends_on = [
    aws_api_gateway_integration.related_person_get_candidate_relationships_integration
  ]
}

resource "aws_api_gateway_method_response" "vrs_related_person_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__related_person.id
  http_method = aws_api_gateway_method.vrs_related_person_get.http_method
  status_code = "200"
}

# ---------
# ANY /RelatedPerson
# ---------

resource "aws_api_gateway_method" "vrs_related_person_any" {
  #checkov:skip=CKV2_AWS_53: Ensure AWS API gateway request is validated
  #checkov:skip=CKV_AWS_59: Ensure there is no open access to back-end resources through API
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.vrs_api__related_person.id
  http_method      = "ANY"
  authorization    = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "vrs_related_person_any" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__related_person.id
  credentials = aws_iam_role.apigateway_role.arn

  http_method             = "ANY"
  integration_http_method = "ANY"
  type                    = "MOCK"

  # Request template with a status code is the minimum requirement from an integration
  # This is required to allow the integration response to run.
  # Failure to include this results in an internal server error.
  request_templates = {
    "application/json" = <<EOF
{
  "statusCode" : 405
}
EOF
  }
  depends_on = [aws_api_gateway_resource.vrs_api__related_person, aws_api_gateway_method.vrs_related_person_any]
  lifecycle {
    ignore_changes = [integration_http_method] # Stops Terraform always trying to update the integration
  }
}

resource "aws_api_gateway_method_response" "vrs_related_person_response_any_405" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__related_person.id
  http_method = aws_api_gateway_method.vrs_related_person_any.http_method
  status_code = "405"
  response_parameters = {
    "method.response.header.allow" = true
  }
  depends_on = [aws_api_gateway_method.vrs_related_person_any]
}

resource "aws_api_gateway_integration_response" "vrs_related_person_response_any_405" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__related_person.id
  http_method = aws_api_gateway_method.vrs_related_person_any.http_method
  status_code = "405"

  # Comma separated list of methods allowed
  response_parameters = {
    "method.response.header.allow" = "'GET'"
  }

  # The error response is defaulted to 405 for all non-required responses.
  response_templates = {
    "application/json" = <<EOF
{
  "issue": [
    {
      "code": "not-supported",
      "details": {
        "coding": [
          {
            "code": "METHOD_NOT_ALLOWED",
            "display": "The method is not allowed.",
            "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
            "version": "1"
          }
        ]
      },
      "diagnostics": "The method is not allowed for the requested resource.",
      "severity": "error"
    }
  ],
  "resourceType": "OperationOutcome"
}
EOF
  }

  depends_on = [
    aws_api_gateway_integration.vrs_related_person_any,
    aws_api_gateway_method_response.vrs_related_person_response_200,
    aws_api_gateway_method_response.vrs_related_person_response_any_405
  ]
}
