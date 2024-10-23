module "process_access_request_step_function" {
  source                    = "../../modules/step_functions"
  workspace                 = local.workspace
  environment               = var.environment
  step_functions_name       = "process-access-request"
  aws_region                = local.aws_region
  kms_key_deletion_duration = local.kms_key_deletion_duration
  state_machine_type        = "STANDARD"

  lambda_arn_list = [
    module.pds_access_token.arn,
    module.pds_get_patient_details.arn
  ]

  state_machine_arn_list = [
    module.validate_relationships_step_functions.step_function_arn
  ]

  state_machine_definition = jsonencode(
    {
      "Comment" : "Implements the process access request logic.",
      "StartAt" : "DynamoDB GetItem",
      "States" : {
        "Ascertain if relationship in allowed list" : {
          "Next" : "Check is in relationship allowed list",
          "Type" : "Pass",
          "ResultPath" : "$.pass_state",
          "Parameters" : {
            "IsInRelationshipList.$" : "States.ArrayContains($.pds_lookup.RelationshipList, $.relationshipCode)"
          }
        },
        "DynamoDB GetItem" : {
          "Next" : "Successfully retrieved data from Dynamo DB?",
          "Parameters" : {
            "Key" : {
              "ReferenceCode" : {
                "S.$" : "$.detail.referenceCode"
              }
            },
            "TableName" : data.aws_dynamodb_table.patient_relationship.name
          },
          "Resource" : "arn:aws:states:::dynamodb:getItem",
          "ResultPath" : "$.data",
          "Type" : "Task"
        },
        "Extract Core Data" : {
          "Comment" : "Extracts the data required for the rest of the step function, removing noise.",
          "Next" : "Get access token",
          "Parameters" : {
            "eventId.$" : "$.detail.eventId",
            "patientNhsNumber.$" : "$.data.Item.PatientNHSNumber.S",
            "proxyNhsNumber.$" : "$.data.Item.ProxyNHSNumber.S",
            "referenceCode.$" : "$.detail.referenceCode",
            "relationshipCode.$" : "States.ArrayGetItem($.data.Item.QuestionnaireData.M.item.L[?(@.M.linkId.S == 'proxy_details')].M.item.L[?(@.M.linkId.S == 'relationship')].M.answer.L[?(@.M.valueCoding.M.system.S == 'http://terminology.hl7.org/CodeSystem/v3-RoleCode')].M.valueCoding.M.code.S, 0)"
          },
          "Type" : "Pass"
        },
        "Fail" : {
          "CausePath" : "$.body.issue[0].diagnostics",
          "Comment" : "Signals failure state and outputs diagnostics messages.",
          "ErrorPath" : "$.body.issue[0].details.coding[0].display",
          "Type" : "Fail"
        },
        "Get PDS data" : {
          "Branches" : [
            {
              "StartAt" : "Get pds record - proxy",
              "States" : {
                "Get pds record - proxy" : {
                  "End" : true,
                  "Parameters" : {
                    "FunctionName" : module.pds_get_patient_details.arn,
                    "Payload" : {
                      "authToken.$" : "$.pds_access_token.result.body.token.access_token",
                      "nhsNumber.$" : "$.proxyNhsNumber"
                    }
                  },
                  "Resource" : "arn:aws:states:::lambda:invoke",
                  "ResultSelector" : {
                    "proxy.$" : "$.Payload"
                  },
                  "Retry" : [
                    {
                      "BackoffRate" : 2,
                      "ErrorEquals" : [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                      ],
                      "IntervalSeconds" : 1,
                      "MaxAttempts" : 3
                    }
                  ],
                  "Type" : "Task"
                }
              }
            },
            {
              "StartAt" : "Get pds record - patient",
              "States" : {
                "Get pds record - patient" : {
                  "End" : true,
                  "Parameters" : {
                    "FunctionName" : module.pds_get_patient_details.arn,
                    "Payload" : {
                      "authToken.$" : "$.pds_access_token.result.body.token.access_token",
                      "nhsNumber.$" : "$.patientNhsNumber"
                    }
                  },
                  "Resource" : "arn:aws:states:::lambda:invoke",
                  "ResultSelector" : {
                    "patient.$" : "$.Payload"
                  },
                  "Retry" : [
                    {
                      "BackoffRate" : 2,
                      "ErrorEquals" : [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                      ],
                      "IntervalSeconds" : 1,
                      "MaxAttempts" : 3
                    }
                  ],
                  "Type" : "Task"
                }
              }
            }
          ],
          "Next" : "Was get pds data successful for both?",
          "ResultPath" : "$.pds_lookup",
          "ResultSelector" : {
            "patient.$" : "$.[1].patient",
            "proxy.$" : "$.[0].proxy",
            "RelationshipList" : []
          },
          "Type" : "Parallel"
        },
        "Get PDS failed" : {
          "Next" : "Fail",
          "Result" : {
            "body" : {
              "issue" : [
                {
                  "code" : "invalid",
                  "details" : {
                    "coding" : [
                      {
                        "code" : "SERVER_ERROR",
                        "display" : "The request could not be processed.",
                        "system" : "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                        "version" : "1"
                      }
                    ]
                  },
                  "diagnostics" : "Failed to successfully retrieve patient information.",
                  "severity" : "error"
                }
              ],
              "resourceType" : "OperationOutcome"
            },
            "statusCode" : 500
          },
          "Type" : "Pass"
        },
        "Get access token" : {
          "Next" : "Was get token successful?",
          "Parameters" : {
            "FunctionName" : module.pds_access_token.arn,
            "Payload.$" : "$"
          },
          "Resource" : "arn:aws:states:::lambda:invoke",
          "ResultPath" : "$.pds_access_token",
          "ResultSelector" : {
            "result.$" : "$.Payload"
          },
          "Retry" : [
            {
              "BackoffRate" : 2,
              "ErrorEquals" : [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
              ],
              "IntervalSeconds" : 1,
              "MaxAttempts" : 3
            }
          ],
          "Type" : "Task"
        },
        "Get access token failed" : {
          "Next" : "Fail",
          "Result" : {
            "body" : {
              "issue" : [
                {
                  "code" : "invalid",
                  "details" : {
                    "coding" : [
                      {
                        "code" : "SERVER_ERROR",
                        "display" : "The request could not be processed.",
                        "system" : "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                        "version" : "1"
                      }
                    ]
                  },
                  "diagnostics" : "Failed to successfully retrieve PDS token.",
                  "severity" : "error"
                }
              ],
              "resourceType" : "OperationOutcome"
            },
            "statusCode" : 500
          },
          "Type" : "Pass"
        },
        "Check is in relationship allowed list" : {
          "Choices" : [
            {
              "Variable" : "$.pass_state.IsInRelationshipList",
              "BooleanEquals" : true,
              "Comment" : "Yes",
              "Next" : "Validate Relationship Step Function"
            }
          ],
          "Default" : "Update request status",
          "Type" : "Choice"
        },
        "Request Failed" : {
          "Next" : "Fail",
          "Result" : {
            "body" : {
              "issue" : [
                {
                  "code" : "invalid",
                  "details" : {
                    "coding" : [
                      {
                        "code" : "SERVER_ERROR",
                        "display" : "The request could not be processed.",
                        "system" : "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                        "version" : "1"
                      }
                    ]
                  },
                  "diagnostics" : "Failed to retrieve record from dynamodb.",
                  "severity" : "error"
                }
              ],
              "resourceType" : "OperationOutcome"
            },
            "statusCode" : 500
          },
          "Type" : "Pass"
        },
        "Success" : {
          "Type" : "Succeed"
        },
        "Successfully retrieved data from Dynamo DB?" : {
          "Choices" : [
            {
              "And" : [
                {
                  "IsPresent" : true,
                  "Variable" : "$.data.Item.PatientNHSNumber.S"
                },
                {
                  "IsPresent" : true,
                  "Variable" : "$.data.Item.ProxyNHSNumber.S"
                },
                {
                  "IsPresent" : true,
                  "Variable" : "$.data.Item.QuestionnaireData"
                }
              ],
              "Comment" : "Yes",
              "Next" : "Extract Core Data"
            }
          ],
          "Default" : "Request Failed",
          "Type" : "Choice"
        },
        "Update Relationship and request status" : {
          "Next" : "Was db update successful?",
          "Parameters" : {
            "ExpressionAttributeValues" : {
              ":ApplicationStatus" : {
                "S" : "ACCESS_REQUEST_READY_FOR_AUTHORISATION"
              },
              ":OdsCode" : {
                "S.$" : "$.pds_lookup.patient.body.pdsPatientRecord.generalPractitioner[0].identifier.value"
              },
              ":validatedRelationshipResp" : {
                "S.$" : "States.JsonToString($.validate_relationship.Output)"
              }
            },
            "Key" : {
              "ReferenceCode" : {
                "S.$" : "$.referenceCode"
              }
            },
            "TableName" : data.aws_dynamodb_table.patient_relationship.name,
            "UpdateExpression" : "SET ApplicationStatus = :ApplicationStatus, OdsCode = :OdsCode, ValidatedRelationshipResponse = :validatedRelationshipResp"
          },
          "Resource" : "arn:aws:states:::dynamodb:updateItem",
          "Type" : "Task"
        },
        "Update failed" : {
          "Next" : "Fail",
          "Result" : {
            "body" : {
              "issue" : [
                {
                  "code" : "invalid",
                  "details" : {
                    "coding" : [
                      {
                        "code" : "SERVER_ERROR",
                        "display" : "Failed to update DynamoDb.",
                        "system" : "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                        "version" : "1"
                      }
                    ]
                  },
                  "diagnostics" : "UpdatedItem did not return 200 - OK",
                  "severity" : "error"
                }
              ],
              "resourceType" : "OperationOutcome"
            },
            "statusCode" : 500
          },
          "Type" : "Pass"
        },
        "Update request status" : {
          "Next" : "Was db update successful?",
          "Parameters" : {
            "ExpressionAttributeValues" : {
              ":ApplicationStatus" : {
                "S" : "ACCESS_REQUEST_READY_FOR_AUTHORISATION"
              },
              ":OdsCode" : {
                "S.$" : "$.pds_lookup.patient.body.pdsPatientRecord.generalPractitioner[0].identifier.value"
              }
            },
            "Key" : {
              "ReferenceCode" : {
                "S.$" : "$.referenceCode"
              }
            },
            "TableName" : data.aws_dynamodb_table.patient_relationship.name,
            "UpdateExpression" : "SET ApplicationStatus = :ApplicationStatus, OdsCode = :OdsCode"
          },
          "Resource" : "arn:aws:states:::dynamodb:updateItem",
          "Type" : "Task"
        },
        "Validate Relationship Step Function" : {
          "Next" : "Update Relationship and request status",
          "Parameters" : {
            "Input" : {
              "AWS_STEP_FUNCTIONS_STARTED_BY_EXECUTION_ID.$" : "$$.Execution.Id",
              "_include" : "RelatedPerson:patient",
              "originalRequestUrl" : "http://someurl.com",
              "patientNhsNumber.$" : "$.patientNhsNumber",
              "proxyNhsNumber.$" : "$.proxyNhsNumber",
              "requestId.$" : "$.eventId"
            },
            "StateMachineArn" : module.validate_relationships_step_functions.step_function_arn
          },
          "Resource" : "arn:aws:states:::states:startExecution.sync:2",
          "ResultPath" : "$.validate_relationship",
          "Type" : "Task"
        },
        "Was db update successful?" : {
          "Choices" : [
            {
              "Comment" : "Yes",
              "Next" : "Success",
              "NumericEquals" : 200,
              "Variable" : "$.SdkHttpMetadata.HttpStatusCode"
            }
          ],
          "Default" : "Update failed",
          "Type" : "Choice"
        },
        "Was get pds data successful for both?" : {
          "Choices" : [
            {
              "And" : [
                {
                  "NumericEquals" : 200,
                  "Variable" : "$.pds_lookup.proxy.statusCode"
                },
                {
                  "NumericEquals" : 200,
                  "Variable" : "$.pds_lookup.patient.statusCode"
                },
                {
                  "IsPresent" : true,
                  "Variable" : "$.pds_lookup.patient.body.pdsPatientRecord.generalPractitioner[0]"
                }
              ],
              "Comment" : "Yes",
              "Next" : "Ascertain if relationship in allowed list"
            }
          ],
          "Default" : "Get PDS failed",
          "Type" : "Choice"
        },
        "Was get token successful?" : {
          "Choices" : [
            {
              "Comment" : "Yes",
              "Next" : "Get PDS data",
              "NumericEquals" : 200,
              "Variable" : "$.pds_access_token.result.statusCode"
            }
          ],
          "Default" : "Get access token failed",
          "Type" : "Choice"
        }
      }
    }
  )
}


data "aws_iam_policy_document" "process_access_request_step_function_dynamodb_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
    ]
    resources = [data.aws_dynamodb_table.patient_relationship.arn]
  }
}

resource "aws_iam_policy" "process_access_request_step_function_dynamodb_policy" {
  name        = "${local.workspace}-process-access-request-dynamodb-permissions"
  description = "A policy for putting and updating items in the patient relationship table"
  policy      = data.aws_iam_policy_document.process_access_request_step_function_dynamodb_policy_document.json
}

resource "aws_iam_role_policy_attachment" "process_access_request_step_function_dynamodb_attachment" {
  role       = module.process_access_request_step_function.iam_role_name
  policy_arn = aws_iam_policy.process_access_request_step_function_dynamodb_policy.arn
}

data "aws_iam_policy_document" "process_access_request_step_function_kms_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
    ]
    resources = [data.aws_kms_key.dynamodb_kms_key.arn]
  }
}

resource "aws_iam_policy" "process_access_request_step_function_kms_policy" {
  name        = "${local.workspace}-process-access-request-kms-permissions"
  description = "A policy for decrypting data keys for the process access request lambda"
  policy      = data.aws_iam_policy_document.process_access_request_step_function_kms_policy_document.json
}

resource "aws_iam_role_policy_attachment" "process_access_request_step_function_kms_attachment" {
  role       = module.process_access_request_step_function.iam_role_name
  policy_arn = aws_iam_policy.process_access_request_step_function_kms_policy.arn
}
