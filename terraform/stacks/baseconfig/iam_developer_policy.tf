data "aws_iam_policy_document" "developer_access" {
  source_policy_documents = [data.aws_iam_policy_document.prevent_privilege_escalation_policy.json]
  statement {
    sid    = "PrimaryRegionAccess"
    effect = "Allow"

    actions = [
      "ec2:CreateTags",
      "ec2:Describe*",
      "ec2:AllocateAddress",
      "ec2:DisassociateAddress",
      "ec2:ReleaseAddress",
      "ec2:AttachInternetGateway",
      "ec2:CreateInternetGateway",
      "ec2:DetachInternetGateway",
      "ec2:DeleteInternetGateway",
      "ec2:CreateNatGateway",
      "ec2:DeleteNatGateway",
      "ec2:AssociateRouteTable",
      "ec2:CreateRoute",
      "ec2:DeleteRoute",
      "ec2:CreateRouteTable",
      "ec2:DeleteRouteTable",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:CreateSubnet",
      "ec2:DeleteSubnet",
      "ec2:CreateVpcEndpoint",
      "ec2:ModifyVpcEndpoint",
      "ec2:DeleteVpcEndpoints",
      "ec2:CreateFlowLogs",
      "ec2:DeleteFlowLogs",
      "ec2:CreateVpc",
      "ec2:DeleteVpc",
      "ec2:ModifyVpcAttribute",
      "ec2:DisassociateRouteTable",
      "ec2:DeleteNetworkInterface",

      "kms:CancelKeyDeletion",
      "kms:CreateAlias",
      "kms:CreateGrant",
      "kms:CreateKey",
      "kms:Decrypt",
      "kms:DeleteAlias",
      "kms:DescribeKey",
      "kms:DisableKeyRotation",
      "kms:EnableKey",
      "kms:EnableKeyRotation",
      "kms:Encrypt",
      "kms:GetKeyPolicy",
      "kms:GetKeyRotationStatus",
      "kms:GenerateDataKey",
      "kms:ListAliases",
      "kms:ListGrants",
      "kms:ListKeyPolicies",
      "kms:ListKeys",
      "kms:ListResourceTags",
      "kms:ListRetirableGrants",
      "kms:PutKeyPolicy",
      "kms:ReEncrypt*",
      "kms:ReplicateKey",
      "kms:RetireGrant",
      "kms:RevokeGrant",
      "kms:ScheduleKeyDeletion",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:UpdateAlias",
      "kms:UpdateKeyDescription",

      "trustedadvisor:Describe*",
      "trustedadvisor:RefreshCheck",

      "athena:*",
      "access-analyzer:*",
      "acm:*",
      "apigateway:*",
      "cloudformation:*",
      "cloudtrail:*",
      "cloudwatch:*",
      "dynamodb:*",
      "events:*",
      "firehose:*",
      "glue:*",
      "health:*",
      "wafv2:*",
      "lambda:*",
      "logs:*",
      "pipes:*",
      "s3:*",
      "schemas:*",
      "secretsmanager:*",
      "serverlessrepo:*",
      "states:*",
      "sqs:*",
      "tag:*",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"

      values = [var.primary_region]
    }
  }
  statement {
    sid    = "GlobalRegionAccess"
    effect = "Allow"

    actions = [
      "access-analyzer:*",
      "budgets:ModifyBudget",
      "budgets:ViewBudget",
      "cloudformation:*",
      "cloudtrail:*",
      "events:*",
      "health:*",
      "s3:*",
      "serverlessrepo:*",
      "tag:*",

      "iam:GetAccountSummary",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:ListAccountAliases",
      "iam:ListAttachedRolePolicies",
      "iam:ListEntitiesForPolicy",
      "iam:ListInstanceProfilesForRole",
      "iam:ListPolicies",
      "iam:ListPolicyVersions",
      "iam:ListRolePolicies",
      "iam:ListRoles",

      "trustedadvisor:Describe*",
      "trustedadvisor:RefreshCheck",
      "wafv2:*",
      "route53:*",
      "route53domains:*"
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"

      values = [var.global_region]
    }
  }

  # Deny access to terraform remote state file to restrict deployments from local
  statement {
    effect = "Deny"

    actions = [
      "s3:ListBucket"
    ]

    resources = ["arn:aws:s3:::${var.project}-${data.aws_iam_account_alias.current.account_alias}-tfstate"]
  }
  # Deny access to terraform remote state file to restrict deployments from local
  statement {
    effect = "Deny"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = ["arn:aws:s3:::${var.project}-${data.aws_iam_account_alias.current.account_alias}-tfstate/*"]
  }
  # Deny access to terraform lock to restrict deployments from local
  statement {
    effect = "Deny"

    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]

    resources = ["arn:aws:dynamodb:*:*:table/${var.project}-${data.aws_iam_account_alias.current.account_alias}-tflock"]
  }
}

# Developer Access policy
resource "aws_iam_policy" "developer_access_policy" {
  count       = var.environment == "dev" ? 1 : 0
  name        = "${upper(var.project)}-Developer"
  description = "Provide developer level access to whomever assumes a role with this policy attached"
  policy      = data.aws_iam_policy_document.developer_access.json

  tags = {
    Name = "${upper(var.project)}-Developer"
  }
}
