data "aws_iam_policy_document" "assume_role_for_sfn" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_sfn" {
  name               = "${var.workspace}-${substr(var.step_functions_name, 0, 42)}-iam-for-sfn"
  assume_role_policy = data.aws_iam_policy_document.assume_role_for_sfn.json
}

data "aws_iam_policy_document" "policy_invoke_lambda" {
  count = local.step_functions_require_lambdas ? 1 : 0
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction", "lambda:InvokeAsync"]
    resources = var.lambda_arn_list
  }
}

data "aws_iam_policy_document" "policy_invoke_state_machine" {
  count = local.step_functions_require_state_machines ? 1 : 0
  statement {
    effect = "Allow"
    actions = [
      "states:StartExecution"
    ]
    resources = var.state_machine_arn_list
  }
  statement {
    effect = "Allow"
    actions = [
      "states:DescribeExecution",
      "states:StopExecution"
    ]
    resources = var.state_machine_arn_list
  }
  statement {
    effect = "Allow"
    actions = [
      "events:PutTargets",
      "events:PutRule",
      "events:DescribeRule",
    ]
    resources = ["arn:aws:events:${var.aws_region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule"]
  }
}

resource "aws_iam_policy" "policy_invoke_lambda" {
  count  = local.step_functions_require_lambdas ? 1 : 0
  name   = "${var.workspace}-${var.step_functions_name}-policy-invoke-lambda"
  policy = data.aws_iam_policy_document.policy_invoke_lambda[0].json
}

resource "aws_iam_policy" "policy_invoke_state_machine" {
  count  = local.step_functions_require_state_machines ? 1 : 0
  name   = "${var.workspace}-${var.step_functions_name}-policy-invoke-state-machine"
  policy = data.aws_iam_policy_document.policy_invoke_state_machine[0].json
}

resource "aws_iam_role_policy_attachment" "iam_for_sfn_attach_policy_invoke_lambda" {
  count      = local.step_functions_require_lambdas ? 1 : 0
  role       = aws_iam_role.iam_for_sfn.name
  policy_arn = aws_iam_policy.policy_invoke_lambda[0].arn
}

resource "aws_iam_role_policy_attachment" "iam_for_sfn_attach_policy_invoke_state_machine" {
  count      = local.step_functions_require_state_machines ? 1 : 0
  role       = aws_iam_role.iam_for_sfn.name
  policy_arn = aws_iam_policy.policy_invoke_state_machine[0].arn
}

data "aws_iam_policy_document" "policy_logging" {
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions #reason: The AWS implementation:  you need to specify * in the Resource field because CloudWatch API actions, such as CreateLogDelivery and DescribeLogGroups, don't support Resource types defined by Amazon CloudWatch Logs. https://docs.aws.amazon.com/step-functions/latest/dg/cw-logs.html#cloudwatch-iam-policy
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints TODO: investigate if all the permissions below  are required, these are set as per AWS documentation for enabling logging for step finctions. https://docs.aws.amazon.com/step-functions/latest/dg/cw-logs.html#cloudwatch-iam-policy
  statement {
    sid    = "AllowLogging"
    effect = "Allow"
    actions = [
      "logs:CreateLogDelivery",
      "logs:CreateLogStream",
      "logs:GetLogDelivery",
      "logs:UpdateLogDelivery",
      "logs:DeleteLogDelivery",
      "logs:ListLogDeliveries",
      "logs:PutLogEvents",
      "logs:PutResourcePolicy",
      "logs:DescribeResourcePolicies",
      "logs:DescribeLogGroups"
    ]

    resources = ["*"]
  }
  statement {
    sid       = "AllowXray"
    effect    = "Allow"
    actions   = ["xray:PutTraceSegments", "xray:PutTelemetryRecords", "xray:GetSamplingRules"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "policy_logging" {
  name   = "${var.workspace}-${var.step_functions_name}-policy-sfn-logging"
  policy = data.aws_iam_policy_document.policy_logging.json
}

resource "aws_iam_role_policy_attachment" "iam_for_sfn_attach_policy_logging" {
  role       = aws_iam_role.iam_for_sfn.name
  policy_arn = aws_iam_policy.policy_logging.arn
}
