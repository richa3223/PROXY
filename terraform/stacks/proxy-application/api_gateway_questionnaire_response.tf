resource "aws_api_gateway_resource" "vrs_api__questionnaire_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.vrs_api__R4.id
  path_part   = "QuestionnaireResponse"
  depends_on  = [aws_api_gateway_resource.vrs_api__R4]
}

# ---------
# POST /QuestionnaireResponse
# ---------

resource "aws_api_gateway_method" "vrs_questionnaire_response_get" {
  # TODO: ensure protection is enabled as part of APIM integration
  #checkov:skip=CKV2_AWS_53: Ensure AWS API gateway request is validated
  #checkov:skip=CKV_AWS_59: Ensure there is no open access to back-end resources through API
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.vrs_api__questionnaire_response.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "questionnaire_response_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__questionnaire_response.id
  credentials = aws_iam_role.apigateway_role.arn

  http_method             = "POST"
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = module.create_access_request.invoke_arn
  content_handling        = null

  request_templates = {
    "application/json" = jsonencode(
      {
        "body" : "$util.escapeJavaScript($input.json('$'))",
        "headers" : {
          "accesstoken.auth_level" : "$input.params().header.get('accesstoken.auth_level')",
          "accesstoken.auth_user_id" : "$input.params().header.get('accesstoken.auth_user_id')",
          "correlationId" : "$input.params().header.get('X-Correlation-ID')",
          "originalRequestUrl" : "$input.params().header.get('Proxy-URL')",
          "requestId" : "$input.params().header.get('X-Request-ID')"
        }
      }
    )
  }
}


# A Step Function will return SUCCEEDED in the status field and 200 code even if underlying lambdas fail.
# Here we override API response accordingly
# https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartSyncExecution.html
resource "aws_api_gateway_integration_response" "vrs_questionnaire_response_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__questionnaire_response.id
  http_method = aws_api_gateway_method.vrs_questionnaire_response_get.http_method
  status_code = aws_api_gateway_method_response.vrs_questionnaire_response_response_200.status_code

  # When invoking the step function from API Gateway, the output is returned as a string format.
  # For the API to return a JSON object response transformation has to take place.
  # In this case the original output value is replaced with the parsed JSON output value, then accessed in the default JsonPath method
  # Also, the status code returned by the step function payload is used in the API response
  response_templates = {
    "application/json" = <<EOF
#set($inputRoot = $input.path('$'))
#set($statusCode = $inputRoot.statusCode)

#if($statusCode == 200)
  #set($context.responseOverride.status = 200)
  #set($parsedPayload = $util.parseJson($inputRoot.body))

  #set($headerObject = $input.params().header)

  #if($headerObject.containsKey('X-Correlation-ID'))
    #set($correlationIdHeader = $headerObject.get('X-Correlation-ID'))
    #set($context.responseOverride.header.X-Correlation-ID = $correlationIdHeader)
  #end

  #if(($headerObject.containsKey('X-Request-ID')) && ($headerObject.get('X-Request-ID') != ""))
    #set($requestIdHeader = $headerObject.get('X-Request-ID'))
    #set($context.responseOverride.header.X-Request-ID = $requestIdHeader)
  #end

  $input.json('$.body')
#elseif($statusCode == 400)
  #set($context.responseOverride.status = 400)
  {
    "issue": [
      {
        "code": "invalid",
        "details": {
          "coding": [
            {
              "code": "BAD_REQUEST",
              "display": "The request could not be processed.",
              "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
              "version": "1"
            }
          ]
        },
        "diagnostics": "The supplied input is not a valid FHIR QuestionnaireResponse.",
        "severity": "error"
      }
    ],
    "resourceType": "OperationOutcome"
  }
#else
  #set($context.responseOverride.status = 500)
  {
    "issue": [
      {
        "code": "invalid",
        "details": {
          "coding": [
            {
              "code": "SERVER_ERROR",
              "display": "Failed to generate response",
              "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
              "version": "1"
            }
          ]
        },
        "diagnostics": "Internal Server Error - Failed to generate response",
        "severity": "error"
      }
    ],
    "resourceType": "OperationOutcome"
  }
#end
EOF
  }

  depends_on = [
    aws_api_gateway_integration.questionnaire_response_integration
  ]
}


# ---------
# ANY /QuestionnaireResponse
# ---------

resource "aws_api_gateway_method" "vrs_questionnaire_response_any" {
  #checkov:skip=CKV2_AWS_53: Ensure AWS API gateway request is validated
  #checkov:skip=CKV_AWS_59: Ensure there is no open access to back-end resources through API
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.vrs_api__questionnaire_response.id
  http_method      = "ANY"
  authorization    = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "vrs_questionnaire_response_any" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__questionnaire_response.id
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

  depends_on = [
    aws_api_gateway_resource.vrs_api__questionnaire_response, aws_api_gateway_method.vrs_questionnaire_response_any
  ]
  lifecycle {
    ignore_changes = [integration_http_method] # Stops Terraform always trying to update the integration
  }
}

resource "aws_api_gateway_method_response" "vrs_questionnaire_response_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__questionnaire_response.id
  http_method = aws_api_gateway_method.vrs_questionnaire_response_get.http_method
  status_code = "200"
}

resource "aws_api_gateway_method_response" "vrs_questionnaire_response_response_any_405" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__questionnaire_response.id
  http_method = aws_api_gateway_method.vrs_questionnaire_response_any.http_method
  status_code = "405"
  response_parameters = {
    "method.response.header.allow" = true
  }
}

resource "aws_api_gateway_integration_response" "vrs_questionnaire_response_response_any_405" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.vrs_api__questionnaire_response.id
  http_method = aws_api_gateway_method.vrs_questionnaire_response_any.http_method
  status_code = aws_api_gateway_method_response.vrs_questionnaire_response_response_any_405.status_code

  # Comma separated list of methods allowed
  response_parameters = {
    "method.response.header.allow" = "'POST'"
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
    aws_api_gateway_integration.vrs_questionnaire_response_any,
    aws_api_gateway_method_response.vrs_questionnaire_response_response_any_405
  ]
}
