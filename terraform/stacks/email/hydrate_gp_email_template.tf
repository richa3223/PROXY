module "hydrate_gp_email_template_step_function" {
  source                    = "../../modules/step_functions"
  workspace                 = local.workspace
  environment               = var.environment
  step_functions_name       = "hydrate-gp-email-template"
  aws_region                = local.aws_region
  kms_key_deletion_duration = local.kms_key_deletion_duration

  lambda_arn_list = [
    module.get_email_template.arn,
    module.ods_lookup.arn,
    module.create_merged_email.arn
  ]

  state_machine_definition = jsonencode({
    "Comment" : "Step function to handle building email content for sending to GP",
    "StartAt" : "Retrieve DynamoDB Record",
    "States" : {
      "Create Merged Email" : {
        "Next" : "Update ApplicationStatus and Add S3 Key",
        "Parameters" : {
          "FunctionName" : module.create_merged_email.arn,
          "Payload.$" : "$"
        },
        "Resource" : "arn:aws:states:::lambda:invoke",
        "ResultPath" : "$.create_merged_email",
        "ResultSelector" : {
          "file_name.$" : "$.Payload.file_name"
        },
        "Retry" : [
          {
            "BackoffRate" : 2,
            "Comment" : "Default Retry Policy",
            "ErrorEquals" : [
              "States.ALL"
            ],
            "IntervalSeconds" : 1,
            "MaxAttempts" : 3
          }
        ],
        "Type" : "Task"
      },
      "Parallel Get Email Address/Content" : {
        "Branches" : [
          {
            "StartAt" : "Get Email Template",
            "States" : {
              "Get Email Template" : {
                "End" : true,
                "OutputPath" : "$.Payload",
                "Parameters" : {
                  "FunctionName" : module.get_email_template.arn,
                  "Payload" : {
                    "template_identifier" : "adult_to_child"
                  }
                },
                "Resource" : "arn:aws:states:::lambda:invoke",
                "Retry" : [
                  {
                    "BackoffRate" : 2,
                    "Comment" : "Default Retry Policy",
                    "ErrorEquals" : [
                      "States.ALL"
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
            "StartAt" : "ODS Lookup",
            "States" : {
              "ODS Lookup" : {
                "End" : true,
                "OutputPath" : "$.Payload",
                "Parameters" : {
                  "FunctionName" : module.ods_lookup.arn,
                  "Payload" : {
                    "ods_code.$" : "$.PatientPDSPatientRecord.generalPractitioner[0].identifier.value"
                  }
                },
                "Resource" : "arn:aws:states:::lambda:invoke",
                "Retry" : [
                  {
                    "BackoffRate" : 2,
                    "Comment" : "Default Retry Policy",
                    "ErrorEquals" : [
                      "States.ALL"
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
        "Next" : "Create Merged Email",
        "ResultPath" : "$.email_details",
        "ResultSelector" : {
          "email_content.$" : "$[0]",
          "gp_email.$" : "$[1]"
        },
        "Type" : "Parallel"
      },
      "Retrieve DynamoDB Record" : {
        "Next" : "Parallel Get Email Address/Content",
        "Parameters" : {
          "Key" : {
            "ReferenceCode" : {
              "S.$" : "$.detail.referenceCode"
            }
          },
          "TableName" : data.aws_dynamodb_table.patient_relationship.name
        },
        "Resource" : "arn:aws:states:::dynamodb:getItem",
        "ResultSelector" : {
          "Item.$" : "$.Item",
          "PatientPDSPatientRecord.$" : "States.StringToJson($.Item.PatientPDSPatientRecord.S)",
          "ProxyPDSPatientRecord.$" : "States.StringToJson($.Item.ProxyPDSPatientRecord.S)"
        },
        "Retry" : [
          {
            "BackoffRate" : 2,
            "Comment" : "Default Retry Policy",
            "ErrorEquals" : [
              "States.ALL"
            ],
            "IntervalSeconds" : 1,
            "MaxAttempts" : 3
          }
        ],
        "Type" : "Task"
      },
      "Update ApplicationStatus and Add S3 Key" : {
        "End" : true,
        "Parameters" : {
          "ExpressionAttributeValues" : {
            ":gpEmailAddresses.$" : "$.email_details.gp_email",
            ":newStatus" : {
              "S" : "GP_AUTHORISATION_REQUEST_CREATED"
            },
            ":s3key" : {
              "S.$" : "$.create_merged_email.file_name"
            }
          },
          "Key" : {
            "ReferenceCode" : {
              "S.$" : "$.Item.ReferenceCode.S"
            }
          },
          "TableName" : data.aws_dynamodb_table.patient_relationship.name,
          "UpdateExpression" : "SET ApplicationStatus = :newStatus, S3Key = :s3key, GPEmailAddresses = :gpEmailAddresses"
        },
        "Resource" : "arn:aws:states:::dynamodb:updateItem",
        "ResultSelector" : {
          "body" : "Step Function completed successfully",
          "statusCode" : 200
        },
        "Retry" : [
          {
            "BackoffRate" : 2,
            "Comment" : "Default Retry Policy",
            "ErrorEquals" : [
              "States.ALL"
            ],
            "IntervalSeconds" : 1,
            "MaxAttempts" : 3
          }
        ],
        "Type" : "Task"
      }
    }
  })
}

data "aws_iam_policy_document" "hydrate_gp_email_template_step_function_dynamodb_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
    ]
    resources = [data.aws_dynamodb_table.patient_relationship.arn]
  }
}

resource "aws_iam_policy" "hydrate_gp_email_template_step_function_dynamodb_policy" {
  name        = "${local.workspace}-hydrate-gp-email-template-dynamodb-permissions"
  description = "A policy for putting and updating items in the patient relationship table"
  policy      = data.aws_iam_policy_document.hydrate_gp_email_template_step_function_dynamodb_policy_document.json
}

resource "aws_iam_role_policy_attachment" "hydrate_gp_email_template_step_function_dynamodb_attachment" {
  role       = module.hydrate_gp_email_template_step_function.iam_role_name
  policy_arn = aws_iam_policy.hydrate_gp_email_template_step_function_dynamodb_policy.arn
}

data "aws_iam_policy_document" "hydrate_gp_email_template_step_function_kms_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
    ]
    resources = [data.aws_kms_key.dynamodb_kms_key.arn]
  }
}

resource "aws_iam_policy" "hydrate_gp_email_template_step_function_kms_policy" {
  name        = "${local.workspace}-hydrate-gp-email-template-kms-permissions"
  description = "A policy for decrypting data keys for the questionnaire exchange lambda"
  policy      = data.aws_iam_policy_document.hydrate_gp_email_template_step_function_kms_policy_document.json
}

resource "aws_iam_role_policy_attachment" "hydrate_gp_email_template_step_function_kms_attachment" {
  role       = module.hydrate_gp_email_template_step_function.iam_role_name
  policy_arn = aws_iam_policy.hydrate_gp_email_template_step_function_kms_policy.arn
}
