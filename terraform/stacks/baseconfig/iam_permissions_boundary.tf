# Policy document for Permissions boundary
data "aws_iam_policy_document" "permissions_boundary" {
  #checkov:skip=CKV2_AWS_40: Ensure AWS IAM policy does not allow full IAM privileges
  # as this is permission boundary, it restricts access to the resources used using wildcard
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints
  #checkov:skip=CKV_AWS_108: Ensure IAM policies does not allow data exfiltration
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints
  #checkov:skip=CKV_AWS_107: Ensure IAM policies does not allow credentials exposure
  #checkov:skip=CKV_AWS_110: Ensure IAM policies does not allow privilege escalation
  source_policy_documents = [data.aws_iam_policy_document.prevent_privilege_escalation_sso_limited_policy.json]

  statement {
    sid    = "RestrictResourcesGeneral"
    effect = "Allow"

    actions = [
      "xray:*",
      "wafv2:*",
      "ssm:*",
      "sqs:*",
      "sns:*",
      "servicequotas:*",
      "serverlessrepo:*",
      "secretsmanager:*",
      "schemas:*",
      "states:*",
      "support:*",
      "tag:*",
      "trustedadvisor:*",

      "iam:AttachRolePolicy",
      "iam:CreatePolicy",
      "iam:CreatePolicyVersion",
      "iam:CreateRole",
      "iam:CreateServiceLinkedRole",
      "iam:DeletePolicy",
      "iam:DeletePolicyVersion",
      "iam:DeleteRole",
      "iam:DeleteRolePolicy",
      "iam:DetachRolePolicy",
      "iam:GenerateCredentialReport",
      "iam:GetAccountSummary",
      "iam:GetCredentialReport",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAccountAliases",
      "iam:ListAttachedRolePolicies",
      "iam:ListEntitiesForPolicy",
      "iam:ListGroups",
      "iam:ListInstanceProfilesForRole",
      "iam:ListPolicies",
      "iam:ListPolicyTags",
      "iam:ListPolicyVersions",
      "iam:ListRolePolicies",
      "iam:ListRoleTags",
      "iam:ListRoles",
      "iam:ListUsers",
      "iam:ListVirtualMFADevices",
      "iam:PassRole",
      "iam:PutRolePolicy",
      "iam:TagPolicy",
      "iam:TagRole",
      "iam:UntagPolicy",
      "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy",

      "s3:AbortMultipartUpload",
      "s3:CreateBucket",
      "s3:DeleteBucket",
      "s3:DeleteBucketPolicy",
      "s3:DeleteObject",
      "s3:GetAccelerateConfiguration",
      "s3:GetBucketAcl",
      "s3:GetBucketCORS",
      "s3:GetBucketLocation",
      "s3:GetBucketLogging",
      "s3:GetBucketNotification",
      "s3:GetBucketObjectLockConfiguration",
      "s3:GetBucketOwnershipControls",
      "s3:GetBucketPolicy",
      "s3:GetBucketPublicAccessBlock",
      "s3:GetBucketRequestPayment",
      "s3:GetBucketTagging",
      "s3:GetBucketVersioning",
      "s3:GetBucketWebsite",
      "s3:GetEncryptionConfiguration",
      "s3:GetLifecycleConfiguration",
      "s3:GetObject",
      "s3:GetReplicationConfiguration",
      "s3:ListAllMyBuckets",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:ListMultipartUploadParts",
      "s3:PutBucketLogging",
      "s3:PutBucketNotification",
      "s3:PutBucketObjectLockConfiguration",
      "s3:PutBucketOwnershipControls",
      "s3:PutBucketPolicy",
      "s3:PutBucketPublicAccessBlock",
      "s3:PutBucketTagging",
      "s3:PutBucketVersioning",
      "s3:PutEncryptionConfiguration",
      "s3:PutLifecycleConfiguration",
      "s3:PutObject",
      "s3:PutReplicationConfiguration",
      "s3:TagResource",
      "s3:UntagResource",

      "route53domains:*",
      "route53:*",
      "pipes:*",
      "logs:*",
      "lambda:*",
      "kms:*",
      "health:*",
      "glue:*",
      "firehose:*",
      "events:*",
      "ec2:*",
      "dynamodb:*",
      "config:*",
      "cloudwatch:*",
      "cloudtrail:Get*",
      "cloudtrail:Describe*",
      "cloudtrail:List*",
      "cloudtrail:LookupEvents",
      "cloudfront:*",
      "cloudformation:*",
      "budgets:*",
      "athena:*",
      "application-autoscaling:*",
      "apigateway:*",
      "acm:*",
      "access-analyzer:*",
      "codebuild:*",
      "directconnect:*",
      "elasticloadbalancing:*",
      "elasticfilesystem:*",
      "elasticache:*",
      "rds:*",
      "redshift:*",
      "ses:*",
      "elasticmapreduce:*",
      "shield:*",
    ]

    resources = ["*"]

  }

  statement {
    sid     = "RestrictResourcesIAMPassRole"
    effect  = "Allow"
    actions = ["iam:PassRole"]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_NPA-ReadOnly_a569b94af8a53d89",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/PVRS-nhsd-demog-proxy-${var.environment}-OIDC",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_NPA-Developer_2024920324f85a59",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_NPA-ReadOnly_0bd7931d25eb23ce",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/PVRS-ReadOnly",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-reserved/sso.amazonaws.com/eu-west-2/AWSReservedSSO_NPA-ReadOnly_39b915eedcb98806"
    ]
  }
}


# PermissionsBoundary policy
resource "aws_iam_policy" "permissions_boundary" {
  name = "${upper(var.project)}-PermissionsBoundary"

  description = "Allows access to AWS services in the regions the client uses only"
  policy      = data.aws_iam_policy_document.permissions_boundary.json

  tags = {
    Name = "${upper(var.project)}-PermissionsBoundary"
  }
}
