module "validate_relationships_step_functions" {
  source                    = "../../modules/step_functions"
  workspace                 = local.workspace
  environment               = var.environment
  step_functions_name       = "validate-relationships"
  aws_region                = local.aws_region
  kms_key_deletion_duration = local.kms_key_deletion_duration
  state_machine_type        = "EXPRESS"

  lambda_arn_list = [
    module.verify_parameters.arn,
    module.pds_access_token.arn,
    module.pds_get_patient_details.arn,
    module.relationship_lookup.arn,
    module.validate_relationship.arn,
    module.validate_eligibility.arn,
    module.process_validation_result.arn,
  ]

  state_machine_definition = jsonencode(
    {
      "Comment" : "Implements main relationship validation business logic.",
      "StartAt" : "verify-parameters",
      "States" : {
        "verify-parameters" : {
          "Type" : "Task",
          "Resource" : "arn:aws:states:::lambda:invoke",
          "OutputPath" : "$.Payload",
          "Parameters" : {
            "Payload.$" : "$",
            "FunctionName" : module.verify_parameters.arn
          },
          "Retry" : [
            {
              "ErrorEquals" : [
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
              ],
              "IntervalSeconds" : 1,
              "MaxAttempts" : 3,
              "BackoffRate" : 2
            }
          ],
          "Next" : "verify-parameters-choice"
        },
        "verify-parameters-choice" : {
          "Type" : "Choice",
          "Choices" : [
            {
              "Variable" : "$.error",
              "IsPresent" : false,
              "Next" : "pds-jwt-auth",
              "Comment" : "On Success"
            }
          ],
          "Default" : "process-validation-result_error"
        },
        "error-state-outcome" : {
          "Comment" : "Error message return for when PDS JWT authentication token is not present in the function.",
          "Next" : "process-validation-result_error",
          "Type" : "Pass",
          "Result" : {
            "error" : {
              "http_status" : 500,
              "response_code" : "SERVER_ERROR",
              "audit_msg" : "Internal Server Error - Failed to generate response",
              "system" : "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
              "version" : "1",
              "display" : "Failed to generate response",
              "severity" : "error",
              "issue_code" : "invalid",
              "expression" : null
            }
          }
        },
        "is-eligible" : {
          "Choices" : [
            {
              "And" : [
                {
                  "Variable" : "$.eligibility.body.eligibility",
                  "BooleanEquals" : true
                },
                {
                  "Variable" : "$.eligibility.body.relationshipArr",
                  "IsNull" : false
                }
              ],
              "Next" : "relationship-map",
              "Comment" : "Check if proxy is eligible and has 1 or more relationships"
            }
          ],
          "Comment" : "Checks the Proxy eligibility status, if eligible continues into the loop.",
          "Type" : "Choice",
          "Default" : "proxy-not-eligible"
        },
        "parallel-array-to-object" : {
          "Comment" : "Transforms the parallel array results into a single object.",
          "Next" : "validate-eligibility",
          "Parameters" : {
            "auth.$" : "$[0].auth",
            "patientNhsNumber.$" : "$[0].patientNhsNumber",
            "pdsDetailsProxy.$" : "$[1]",
            "pdsRelationshipLookup.$" : "$[2]",
            "proxyNhsNumber.$" : "$[0].proxyNhsNumber",
            "correlationId.$" : "$[0].correlationId",
            "originalRequestUrl.$" : "$[0].originalRequestUrl",
            "_include.$" : "$[0]._include",
            "requestId.$" : "$[0].requestId"
          },
          "Type" : "Pass"
        },
        "pds-jwt-auth" : {
          "Comment" : "Invoke the Lambda function to obtain a PDS JWT authentication token.",
          "Next" : "pds-jwt-auth-error-check",
          "Parameters" : {
            "FunctionName" : module.pds_access_token.arn,
            "Payload.$" : "$"
          },
          "Resource" : "arn:aws:states:::lambda:invoke",
          "ResultPath" : "$.auth",
          "ResultSelector" : {
            "body.$" : "$.Payload.body",
            "statusCode.$" : "$.Payload.statusCode"
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
        "pds-jwt-auth-error-check" : {
          "Choices" : [
            {
              "Variable" : "$.auth.body.token.access_token"
              "IsPresent" : true,
              "Next" : "pds-parallel-calls",
              "Comment" : "Access token request successul"
            }
          ],
          "Comment" : "Check if the PDS JWT authentication token is present in the Lambda response, as all other stages would fail after if not present.",
          "Default" : "error-state-outcome",
          "Type" : "Choice"
        },
        "pds-parallel-calls" : {
          "Branches" : [
            {
              "StartAt" : "existing-payload-passthrough",
              "States" : {
                "existing-payload-passthrough" : {
                  "Comment" : "Passes Parent state through to the parallel returned array.",
                  "End" : true,
                  "Type" : "Pass"
                }
              }
            },
            {
              "StartAt" : "pds-get-patient-details-proxy",
              "States" : {
                "pds-get-patient-details-proxy" : {
                  "Comment" : "Invoke the Lambda function to obtain a PDS Patient Details for Proxy's NHS Number.",
                  "End" : true,
                  "Parameters" : {
                    "FunctionName" : module.pds_get_patient_details.arn,
                    "Payload" : {
                      "authToken.$" : "$.auth.body.token.access_token",
                      "nhsNumber.$" : "$.proxyNhsNumber"
                    }
                  },
                  "Resource" : "arn:aws:states:::lambda:invoke",
                  "ResultSelector" : {
                    "body.$" : "$.Payload.body",
                    "statusCode.$" : "$.Payload.statusCode"
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
              "StartAt" : "pds-get-proxy-related-people",
              "States" : {
                "pds-get-proxy-related-people" : {
                  "Comment" : "Invoke the Lambda function to obtain a PDS Proxy Related people details.",
                  "Parameters" : {
                    "FunctionName" : module.relationship_lookup.arn,
                    "Payload" : {
                      "authToken.$" : "$.auth.body.token.access_token",
                      "nhsNumber.$" : "$.proxyNhsNumber"
                    }
                  },
                  "Resource" : "arn:aws:states:::lambda:invoke",
                  "ResultSelector" : {
                    "body.$" : "$.Payload.body",
                    "statusCode.$" : "$.Payload.statusCode"
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
                  "Type" : "Task",
                  "End" : true
                }
              }
            }
          ],
          "Comment" : "Parallel state for making multiple calls to PDS Lambda functions.",
          "Next" : "parallel-array-to-object",
          "Type" : "Parallel"
        },
        "process-validation-result_error" : {
          "Comment" : "Handles error input to return in FHIR format from the step function.",
          "End" : true,
          "OutputPath" : "$.Payload",
          "Parameters" : {
            "FunctionName" : module.process_validation_result.arn,
            "Payload" : {
              "error.$" : "$.error"
            }
          },
          "Resource" : "arn:aws:states:::lambda:invoke",
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
        "process-validation-result_map" : {
          "Comment" : "Handles PDS Patient & Relationship Array to return in FHIR format from the step function.",
          "End" : true,
          "OutputPath" : "$.Payload",
          "Parameters" : {
            "FunctionName" : module.process_validation_result.arn,
            "Payload" : {
              "pdsPatientRelationship.$" : "$.map",
              "originalRequestUrl.$" : "$.originalRequestUrl",
              "_include.$" : "$._include",
              "proxyIdentifier.$" : "$.pdsDetailsProxy.body.pdsPatientRecord.identifier[0]",
              "requestId.$" : "$.requestId"
            }
          },
          "Resource" : "arn:aws:states:::lambda:invoke",
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
        "proxy-not-eligible" : {
          "Comment" : "Sets map array empty when Proxy is not eligible.",
          "Next" : "process-validation-result_map",
          "Parameters" : [],
          "ResultPath" : "$.map",
          "Type" : "Pass"
        },
        "relationship-map" : {
          "Comment" : "Loops over the relationship array, getting PDS Details and validating the relstaionship.",
          "InputPath" : "$",
          "ItemProcessor" : {
            "ProcessorConfig" : {
              "Mode" : "INLINE"
            },
            "StartAt" : "pds-patient-parrallel-calls",
            "States" : {
              "pds-patient-parrallel-calls" : {
                "Type" : "Parallel",
                "Next" : "patient-parallel-array-to-object",
                "Branches" : [
                  {
                    "StartAt" : "existing-loop-payload-passthrough",
                    "States" : {
                      "existing-loop-payload-passthrough" : {
                        "Comment" : "Passes Parent state through to the parallel returned array.",
                        "End" : true,
                        "Type" : "Pass"
                      }
                    }
                  },
                  {
                    "StartAt" : "pds-get-patient-details",
                    "States" : {
                      "pds-get-patient-details" : {
                        "Comment" : "Invoke the Lambda function to obtain a PDS Patient Details for Patients's NHS Number via the relationship.",
                        "Parameters" : {
                          "FunctionName" : module.pds_get_patient_details.arn,
                          "Payload" : {
                            "authToken.$" : "$.authToken",
                            "nhsNumber.$" : "$.relationship.patient.identifier.value"
                          }
                        },
                        "Resource" : "arn:aws:states:::lambda:invoke",
                        "ResultSelector" : {
                          "body.$" : "$.Payload.body",
                          "statusCode.$" : "$.Payload.statusCode"
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
                        "Type" : "Task",
                        "End" : true
                      }
                    }
                  },
                  {
                    "StartAt" : "pds-get-patient-related-people",
                    "States" : {
                      "pds-get-patient-related-people" : {
                        "Comment" : "Invoke the Lambda function to obtain a PDS Proxy Related people details.",
                        "End" : true,
                        "Parameters" : {
                          "FunctionName" : module.relationship_lookup.arn,
                          "Payload" : {
                            "authToken.$" : "$.authToken",
                            "nhsNumber.$" : "$.relationship.patient.identifier.value"
                          }
                        },
                        "Resource" : "arn:aws:states:::lambda:invoke",
                        "ResultSelector" : {
                          "body.$" : "$.Payload.body",
                          "statusCode.$" : "$.Payload.statusCode"
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
                ]
              },
              "patient-parallel-array-to-object" : {
                "Comment" : "Transforms the parallel array results into a single object.",
                "Next" : "validate-relationship",
                "Parameters" : {
                  "authToken.$" : "$[0].authToken",
                  "proxyNhsNumber.$" : "$[0].proxyNhsNumber",
                  "relationship.$" : "$[0].relationship",
                  "pdsDetailsPatient.$" : "$[1]",
                  "pdsRelationshipLookupPatient.$" : "$[2]",
                  "correlationId.$" : "$[0].correlationId"
                  "requestId.$" : "$[0].requestId"
                },
                "Type" : "Pass"
              },
              "relationship-eligible" : {
                "Comment" : "Picks out the two requried values from the object",
                "End" : true,
                "Parameters" : {
                  "pdsPatient.$" : "$.validateRelationship.body.pdsPatient",
                  "pdsRelationship.$" : "$.validateRelationship.body.pdsRelationshipLookup"
                },
                "Type" : "Pass"
              },
              "relationship-not-eligible" : {
                "Comment" : "Returns null from the map iterations if no relationships are valid",
                "End" : true,
                "Parameters" : null,
                "Type" : "Pass"
              },
              "validate-relationship" : {
                "Comment" : "Invoke the Lambda function to validate the relationship based on Proxy/Patient Details.",
                "Next" : "validate-relationship-check",
                "Parameters" : {
                  "FunctionName" : module.validate_relationship.arn,
                  "Payload" : {
                    "proxyNhsNumber.$" : "$.proxyNhsNumber",
                    "pdsPatient.$" : "$.pdsDetailsPatient.body.pdsPatientRecord",
                    "pdsPatientStatus.$" : "$.pdsDetailsPatient.statusCode",
                    "pdsRelationshipLookup.$" : "$.pdsRelationshipLookupPatient.body.pdsRelationshipRecord",
                    "pdsRelationshipLookupStatus.$" : "$.pdsRelationshipLookupPatient.statusCode",
                    "correlationId.$" : "$.correlationId",
                    "requestId.$" : "$.requestId"
                  }
                },
                "Resource" : "arn:aws:states:::lambda:invoke",
                "ResultPath" : "$.validateRelationship",
                "ResultSelector" : {
                  "body.$" : "$.Payload.body",
                  "statusCode.$" : "$.Payload.statusCode"
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
              "validate-relationship-check" : {
                "Choices" : [
                  {
                    "And" : [
                      {
                        "IsPresent" : true,
                        "Variable" : "$.validateRelationship.body.pdsPatient"
                      },
                      {
                        "IsPresent" : true,
                        "Variable" : "$.validateRelationship.body.pdsRelationshipLookup"
                      }
                    ],
                    "Next" : "relationship-eligible"
                  }
                ],
                "Comment" : "Checks pdsPatient & pdsRelationshipLookup are returned from the previous stage.",
                "Default" : "relationship-not-eligible",
                "Type" : "Choice"
              }
            }
          },
          "ItemSelector" : {
            "authToken.$" : "$.auth.body.token.access_token",
            "proxyNhsNumber.$" : "$.proxyNhsNumber",
            "relationship.$" : "$$.Map.Item.Value",
            "correlationId.$" : "$.correlationId",
            "requestId.$" : "$.requestId"
          },
          "ItemsPath" : "$.eligibility.body.relationshipArr",
          "MaxConcurrency" : 1,
          "Next" : "process-validation-result_map",
          "ResultPath" : "$.map",
          "Type" : "Map"
        },
        "validate-eligibility" : {
          "Comment" : "Invoke the Lambda function to validate the eligibility of the Proxy based on PDS details.",
          "Next" : "is-eligible",
          "Parameters" : {
            "FunctionName" : module.validate_eligibility.arn,
            "Payload" : {
              "patientNhsNumber.$" : "$.patientNhsNumber",
              "pdsProxyDetails.$" : "$.pdsDetailsProxy.body.pdsPatientRecord",
              "pdsProxyStatusCode.$" : "$.pdsDetailsProxy.statusCode",
              "pdsRelationshipLookup.$" : "$.pdsRelationshipLookup.body.pdsRelationshipRecord",
              "pdsRelationshipLookupStatusCode.$" : "$.pdsRelationshipLookup.statusCode",
              "correlationId.$" : "$.correlationId",
              "requestId.$" : "$.requestId"
            }
          },
          "Resource" : "arn:aws:states:::lambda:invoke",
          "ResultPath" : "$.eligibility",
          "ResultSelector" : {
            "body.$" : "$.Payload.body",
            "statusCode.$" : "$.Payload.statusCode"
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
  )
}
