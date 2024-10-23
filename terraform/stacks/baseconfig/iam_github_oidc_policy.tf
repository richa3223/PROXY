# Policy document for PIPELINE Access role (should be able to do everything needed to deploy environments but no more)
data "aws_iam_policy_document" "github_oidc_access_1" {
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions #reason: CICD need access to a range of resources
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints #reason: CICD role need those permissions to be able to apply policies on S3 buckets
  statement {
    effect = "Allow"

    actions = [
      "acm:DescribeCertificate",
      "acm:GetCertificate",

      "apigateway:CreateDeployment",
      "apigateway:CreateRequestValidator",
      "apigateway:CreateResource",
      "apigateway:CreateRestApi",
      "apigateway:CreateStage",
      "apigateway:DeleteDeployment",
      "apigateway:GetAccount",
      "apigateway:GetDeployment",
      "apigateway:GetIntegration",
      "apigateway:GetIntegrationResponse",
      "apigateway:GetMethod",
      "apigateway:GetMethodResponse",
      "apigateway:GetModel",
      "apigateway:GetRequestValidator",
      "apigateway:GetResource",
      "apigateway:GetResources",
      "apigateway:GetRestApi",
      "apigateway:GetStage",
      "apigateway:PutIntegration",
      "apigateway:PutIntegrationResponse",
      "apigateway:PutMethod",
      "apigateway:PutMethodResponse",
      "apigateway:UpdateAccount",
      "apigateway:UpdateIntegration",
      "apigateway:UpdateMethod",
      "apigateway:UpdateRequestValidator",
      "apigateway:UpdateResource",
      "apigateway:UpdateStage",
      "apigateway:PUT",
      "apigateway:PATCH",
      "apigateway:POST",
      "apigateway:GET",
      "apigateway:DELETE",
      "apigateway:SetWebACL",
      "apigateway:AddCertificateToDomain",
      "apigateway:RemoveCertificateFromDomain",

      "athena:BatchGetQueryExecution",
      "athena:GetQueryExecution",
      "athena:GetQueryResults",
      "athena:GetQueryRuntimeStatistics",
      "athena:GetWorkGroup",
      "athena:CreateWorkGroup",
      "athena:DeleteWorkGroup",
      "athena:ListQueryExecutions",
      "athena:StartQueryExecution",
      "athena:ListDataCatalogs",
      "athena:ListWorkGroups",
      "athena:ListTagsForResource",
      "athena:TagResource",
      "athena:UpdateWorkGroup",

      "cloudwatch:GetMetricStream",
      "cloudwatch:PutMetricStream",
      "cloudwatch:TagResource",
      "cloudwatch:ListTagsForResource",
      "cloudwatch:DeleteMetricStream",

      "dynamodb:CreateTable",
      "dynamodb:DeleteItem",
      "dynamodb:DeleteTable",
      "dynamodb:DescribeTable",
      "dynamodb:DescribeTimeToLive",
      "dynamodb:GetItem",
      "dynamodb:ListTables",
      "dynamodb:ListTagsOfResource",
      "dynamodb:PutItem",
      "dynamodb:TagResource",
      "dynamodb:UntagResource",
      "dynamodb:UpdateContinuousBackups",
      "dynamodb:UpdateTable",
      "dynamodb:UpdateTimeToLive",

      "ec2:AllocateAddress",
      "ec2:AssociateRouteTable",
      "ec2:AttachInternetGateway",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CreateFlowLogs",
      "ec2:CreateInternetGateway",
      "ec2:CreateNatGateway",
      "ec2:CreateRoute",
      "ec2:CreateRouteTable",
      "ec2:CreateSecurityGroup",
      "ec2:CreateSubnet",
      "ec2:CreateTags",
      "ec2:CreateVpc",
      "ec2:CreateVpcEndpoint",
      "ec2:DeleteFlowLogs",
      "ec2:DeleteInternetGateway",
      "ec2:DeleteNatGateway",
      "ec2:DeleteNetworkInterface",
      "ec2:DeleteRoute",
      "ec2:DeleteRouteTable",
      "ec2:DeleteSecurityGroup",
      "ec2:DeleteSubnet",
      "ec2:DeleteTags",
      "ec2:DeleteVpc",
      "ec2:DeleteVpcEndpoints",
      "ec2:DescribeAddresses",
      "ec2:DescribeAddressesAttribute",
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeFlowLogs",
      "ec2:DescribeInternetGateways",
      "ec2:DescribeNatGateways",
      "ec2:DescribeNetworkAcls",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribePrefixLists",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSecurityGroupRules",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcAttribute",
      "ec2:DescribeVpcEndpoints",
      "ec2:DescribeVpcs",
      "ec2:DetachInternetGateway",
      "ec2:DisassociateAddress",
      "ec2:DisassociateRouteTable",
      "ec2:ModifyVpcAttribute",
      "ec2:ModifyVpcEndpoint",
      "ec2:ReleaseAddress",
      "ec2:ReplaceRoute",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress",

      "events:CreateEventBus",
      "events:DeleteEventBus",
      "events:DeleteRule",
      "events:DescribeEventBus",
      "events:DescribeRule",
      "events:ListTagsForResource",
      "events:ListTargetsByRule",
      "events:PutEvents",
      "events:PutPermission",
      "events:PutRule",
      "events:PutTargets",
      "events:RemovePermission",
      "events:RemoveTargets",
      "events:TagResource",
      "events:UntagResource",

      "firehose:CreateDeliveryStream",
      "firehose:DescribeDeliveryStream",
      "firehose:ListTagsForDeliveryStream",
      "firehose:StartDeliveryStreamEncryption",
      "firehose:DeleteDeliveryStream",
      "firehose:TagDeliveryStream",
      "firehose:UntagDeliveryStream",
      "firehose:ListDeliveryStreams",
      "firehose:UpdateDestination",

      "glue:CreateCrawler",
      "glue:CreateDatabase",
      "glue:CreateSecurityConfiguration",
      "glue:DeleteCrawler",
      "glue:DeleteDatabase",
      "glue:DeleteSecurityConfiguration",
      "glue:GetCrawler",
      "glue:GetDatabase",
      "glue:GetSecurityConfiguration",
      "glue:GetTags",
      "glue:GetTable",
      "glue:GetPartitions",
      "glue:StartCrawler",
      "glue:TagResource",
      "glue:UpdateCrawler",

      "iam:ListPolicyTags",
      "iam:UntagPolicy",
      "iam:UntagRole",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"

      values = [var.primary_region]
    }
  }

  statement {
    sid     = "IAMPassRoleAccess"
    effect  = "Allow"
    actions = ["iam:PassRole"]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-DynamoDBStreamToEventBridge*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-api-gateway-role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-audit-kinesis-firehose-iam-role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-event-bus",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-event-bus-audit-iam-role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-event-bus-email-iam-role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-event-bus-proxy-application-iam-role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-iam-for-lambda",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-iam-for-sfn",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-rest-apigw-sfn",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-splunk-firehose-role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-splunk-metric-stream-role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*-splunk-metrics-firehose",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*_data_glue_crawler-glue_iam_role",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/PVRS-nhsd-demog-proxy-${var.environment}-OIDC",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/vpc-flow-log-role-*",
    ]
  }
}

data "aws_iam_policy_document" "github_oidc_access_2" {
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions #reason: CICD need access to a range of resources
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints #reason: CICD need access to a range of resources

  statement {
    effect = "Allow"

    actions = [
      "kms:CreateAlias",
      "kms:CreateGrant",
      "kms:CreateKey",
      "kms:Decrypt",
      "kms:DeleteAlias",
      "kms:DescribeKey",
      "kms:DisableKeyRotation",
      "kms:EnableKeyRotation",
      "kms:EnableKeyRotation",
      "kms:Encrypt",
      "kms:GenerateDataKey",
      "kms:GetKeyPolicy",
      "kms:GetKeyRotationStatus",
      "kms:ListAliases",
      "kms:ListResourceTags",
      "kms:PutKeyPolicy",
      "kms:ScheduleKeyDeletion",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:UpdateAlias",
      "kms:UpdateKeyDescription",

      "lambda:AddPermission",
      "lambda:CreateEventSourceMapping",
      "lambda:CreateFunction",
      "lambda:DeleteEventSourceMapping",
      "lambda:DeleteFunction",
      "lambda:DeleteLayerVersion",
      "lambda:GetEventSourceMapping",
      "lambda:GetFunction",
      "lambda:GetFunctionCodeSigningConfig",
      "lambda:GetLayerVersion",
      "lambda:GetPolicy",
      "lambda:InvokeFunction",
      "lambda:ListVersionsByFunction",
      "lambda:PublishLayerVersion",
      "lambda:PublishVersion",
      "lambda:RemovePermission",
      "lambda:TagResource",
      "lambda:UntagResource",
      "lambda:UpdateFunctionCode",
      "lambda:UpdateFunctionConfiguration",

      "logs:AssociateKmsKey",
      "logs:CreateLogDelivery",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DeleteLogDelivery",
      "logs:DeleteLogGroup",
      "logs:DeleteLogStream",
      "logs:DeleteRetentionPolicy",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:DescribeResourcePolicies",
      "logs:GetLogDelivery",
      "logs:GetLogEvents",
      "logs:ListLogDeliveries",
      "logs:ListTagsForResource",
      "logs:ListTagsLogGroup",
      "logs:PutLogEvents",
      "logs:PutResourcePolicy",
      "logs:PutRetentionPolicy",
      "logs:TagLogGroup",
      "logs:TagResource",
      "logs:UntagLogGroup",
      "logs:UntagResource",
      "logs:UpdateLogDelivery",

      "pipes:CreatePipe",
      "pipes:DeletePipe",
      "pipes:DescribePipe",
      "pipes:ListPipes",
      "pipes:ListTagsForResource",
      "pipes:StartPipe",
      "pipes:StopPipe",
      "pipes:TagResource",
      "pipes:UntagResource",
      "pipes:UpdatePipe",

      "s3:CreateBucket",
      "s3:DeleteBucket",
      "s3:DeleteBucketPolicy",
      "s3:GetAccelerateConfiguration",
      "s3:GetBucketAcl",
      "s3:GetBucketCORS",
      "s3:GetLifecycleConfiguration",
      "s3:PutLifecycleConfiguration",
      "s3:GetEncryptionConfiguration",
      "s3:PutEncryptionConfiguration",
      "s3:GetBucketPublicAccessBlock",
      "s3:PutBucketPublicAccessBlock",
      "s3:GetBucketLogging",
      "s3:PutBucketLogging",
      "s3:GetBucketNotification",
      "s3:PutBucketNotification",
      "s3:GetBucketObjectLockConfiguration",
      "s3:PutBucketObjectLockConfiguration",
      "s3:GetBucketOwnershipControls",
      "s3:PutBucketOwnershipControls",
      "s3:GetBucketPolicy",
      "s3:GetReplicationConfiguration",
      "s3:PutReplicationConfiguration",
      "s3:GetBucketRequestPayment",
      "s3:GetBucketTagging",
      "s3:TagResource",
      "s3:UntagResource",
      "s3:PutBucketTagging",
      "s3:GetBucketVersioning",
      "s3:PutBucketVersioning",
      "s3:GetBucketWebsite",
      "s3:PutBucketPolicy",
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:ListBucketVersions",
      "s3:ListObjectVersions",
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "s3:ListBucketMultipartUploads",
      "s3:AbortMultipartUpload",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListMultipartUploadParts",

      "schemas:CreateRegistry",
      "schemas:DescribeRegistry",
      "schemas:CreateSchema",
      "schemas:DescribeSchema",
      "schemas:ListTagsForResource",
      "schemas:TagResource",
      "schemas:UntagResource",
      "schemas:DeleteSchema",
      "schemas:UpdateRegistry",
      "schemas:DeleteRegistry",
      "schemas:UpdateSchema",
      "schemas:ListRegistries",
      "schemas:ListSchemas",
      "schemas:ListSchemaVersions",

      "secretsmanager:CreateSecret",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds",
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DeleteSecret",
      "secretsmanager:UpdateSecret",
      "secretsmanager:PutSecretValue",
      "secretsmanager:ListSecrets",
      "secretsmanager:TagResource",
      "secretsmanager:UpdateSecretVersionStage",

      "states:CreateStateMachine",
      "states:DeleteStateMachine",
      "states:CreateStateMachineAlias",
      "states:DeleteStateMachineAlias",
      "states:DescribeStateMachine",
      "states:DescribeStateMachineForExecution",
      "states:DescribeStateMachineAlias",
      "states:ListStateMachineVersions",
      "states:ListTagsForResource",
      "states:UpdateStateMachine",
      "states:UpdateStateMachineAlias",
      "states:TagResource",
      "states:StartSyncExecution",
      "states:StartExecution",
      "states:DescribeExecution",

      "sts:GetCallerIdentity",

      "sqs:CreateQueue",
      "sqs:GetQueueAttributes",
      "sqs:SetQueueAttributes",
      "sqs:DeleteQueue",
      "sqs:ListQueues",
      "sqs:ListQueueTags",
      "sqs:TagQueue",
      "sqs:UntagQueue",
      "sqs:GetQueueUrl",
      "sqs:PurgeQueue",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",

      "wafv2:DeleteLoggingConfiguration",
      "wafv2:DeleteWebACL",
      "wafv2:GetLoggingConfiguration",
      "wafv2:GetWebACL",
      "wafv2:GetWebACLForResource",
      "wafv2:ListTagsForResource",
      "wafv2:ListWebACLs",

      "xray:GetTraceGraph"
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"

      values = [var.primary_region]
    }
  }

  statement {
    effect = "Allow"
    actions = [
      "acm:ListCertificates",
      "acm:ListTagsForCertificate"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "github_oidc_access_global_region" {
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  # CICD need access to a range of resources
  statement {
    effect = "Allow"

    actions = [
      "acm:ListCertificates",
      "acm:DescribeCertificate",
      "acm:GetCertificate",
      "acm:ListTagsForCertificate",

      "cloudfront:UpdateDistribution",

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
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAccountAliases",
      "iam:ListAttachedRolePolicies",
      "iam:ListEntitiesForPolicy",
      "iam:ListInstanceProfilesForRole",
      "iam:ListPolicyTags",
      "iam:ListPolicyVersions",
      "iam:ListRolePolicies",
      "iam:PutRolePolicy",
      "iam:TagPolicy",
      "iam:TagRole",
      "iam:UntagPolicy",
      "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy",

      "route53:CreateHostedZone",
      "route53:DeleteHostedZone",
      "route53:GetHostedZone*",
      "route53:ListHostedZone*",
      "route53:ListResourceRecord*",
      "route53:ChangeResourceRecord*",
      "route53:ListTagsForResource",
      "route53:GetChange",

      "shield:CreateProtection",
      "shield:DeleteProtection",
      "shield:DescribeProtection",
      "shield:ListProtections",
      "shield:ListTagsForResource",
      "shield:TagResource",
      "shield:UntagResource",

      "wafv2:ListWebACLs",
      "wafv2:GetLoggingConfiguration",
      "wafv2:GetWebACL",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = [var.global_region]
    }
  }
}

data "aws_iam_policy_document" "github_oidc_access_terraform" {
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints

  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.project}-${data.aws_iam_account_alias.current.account_alias}-tfstate"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = ["arn:aws:s3:::${var.project}-${data.aws_iam_account_alias.current.account_alias}-tfstate/*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]
    resources = ["arn:aws:dynamodb:*:*:table/${var.project}-${data.aws_iam_account_alias.current.account_alias}-tflock"]
  }
}

data "aws_iam_policy_document" "github_oidc_access_scoutsuite" {
  #checkov:skip=CKV_AWS_356: Ensure no IAM policies documents allow "*" as a statement's resource for restrictable actions
  #checkov:skip=CKV_AWS_109: Ensure IAM policies does not allow permissions management / resource exposure without constraints
  #checkov:skip=CKV_AWS_108: Ensure IAM policies does not allow data exfiltration
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints

  statement {
    effect = "Allow"
    actions = [
      "acm:DescribeCertificate",
      "acm:ListCertificates",
      "cloudformation:DescribeStacks",
      "cloudformation:GetStackPolicy",
      "cloudformation:GetTemplate",
      "cloudformation:ListStacks",
      "cloudtrail:DescribeTrails",
      "cloudtrail:GetEventSelectors",
      "cloudtrail:GetTrailStatus",
      "cloudwatch:DescribeAlarms",
      "cloudfront:ListDistributions",
      "codebuild:BatchGetProjects",
      "codebuild:ListProjects",
      "cognito-identity:DescribeIdentityPool",
      "cognito-identity:ListIdentityPools",
      "cognito-idp:DescribeUserPool",
      "cognito-idp:ListUserPools",
      "config:DescribeConfigRules",
      "config:DescribeConfigurationRecorderStatus",
      "config:DescribeConfigurationRecorders",
      "directconnect:DescribeConnections",
      "dynamodb:DescribeContinuousBackups",
      "dynamodb:DescribeTable",
      "dynamodb:ListBackups",
      "dynamodb:ListTables",
      "dynamodb:ListTagsOfResource",

      "ec2:DescribeCustomerGateways",
      "ec2:DescribeFlowLogs",
      "ec2:DescribeImages",
      "ec2:DescribeInstanceAttribute",
      "ec2:DescribeInstances",
      "ec2:DescribeNetworkAcls",
      "ec2:DescribeNetworkInterfaceAttribute",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeRegions",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSnapshotAttribute",
      "ec2:DescribeSnapshots",
      "ec2:DescribeSubnets",
      "ec2:DescribeTags",
      "ec2:DescribeVolumes",
      "ec2:DescribeVpcPeeringConnections",
      "ec2:DescribeVpcs",
      "ec2:DescribeVpnConnections",
      "ec2:DescribeVpnGateways",

      "ecr:DescribeImages",
      "ecr:DescribeRepositories",
      "ecr:GetLifecyclePolicy",
      "ecr:GetRepositoryPolicy",
      "ecr:ListImages",
      "ecs:DescribeClusters",
      "ecs:ListAccountSettings",
      "ecs:ListClusters",
      "eks:DescribeCluster",
      "eks:ListClusters",
      "elasticache:DescribeCacheClusters",
      "elasticache:DescribeCacheParameterGroups",
      "elasticache:DescribeCacheSecurityGroups",
      "elasticache:DescribeCacheSubnetGroups",
      "elasticfilesystem:DescribeFileSystems",
      "elasticfilesystem:DescribeMountTargetSecurityGroups",
      "elasticfilesystem:DescribeMountTargets",
      "elasticfilesystem:DescribeTags",
      "elasticloadbalancing:DescribeListeners",
      "elasticloadbalancing:DescribeLoadBalancerAttributes",
      "elasticloadbalancing:DescribeLoadBalancerPolicies",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeSSLPolicies",
      "elasticloadbalancing:DescribeTags",
      "elasticmapreduce:DescribeCluster",
      "elasticmapreduce:ListClusters",
      "guardduty:GetDetector",
      "guardduty:ListDetectors",
      "iam:GenerateCredentialReport",
      "iam:GetAccountPasswordPolicy",
      "iam:GetCredentialReport",
      "iam:GetGroup",
      "iam:GetGroupPolicy",
      "iam:GetLoginProfile",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:GetUserPolicy",
      "iam:ListAccessKeys",
      "iam:ListAttachedRolePolicies",
      "iam:ListEntitiesForPolicy",
      "iam:ListGroupPolicies",
      "iam:ListGroups",
      "iam:ListGroupsForUser",
      "iam:ListInstanceProfilesForRole",
      "iam:ListMFADevices",
      "iam:ListPolicies",
      "iam:ListRolePolicies",
      "iam:ListRoleTags",
      "iam:ListRoles",
      "iam:ListUserPolicies",
      "iam:ListUserTags",
      "iam:ListUsers",
      "iam:ListVirtualMFADevices",
      "kms:DescribeKey",
      "kms:GetKeyPolicy",
      "kms:GetKeyRotationStatus",
      "kms:ListAliases",
      "kms:ListGrants",
      "kms:ListKeys",
      "lambda:GetFunctionConfiguration",
      "lambda:GetPolicy",
      "lambda:ListFunctions",
      "lambda:InvokeFunction",
      "logs:DescribeMetricFilters",
      "rds:DescribeDBClusterSnapshotAttributes",
      "rds:DescribeDBClusterSnapshots",
      "rds:DescribeDBClusters",
      "rds:DescribeDBInstances",
      "rds:DescribeDBParameterGroups",
      "rds:DescribeDBParameters",
      "rds:DescribeDBSecurityGroups",
      "rds:DescribeDBSnapshotAttributes",
      "rds:DescribeDBSnapshots",
      "rds:DescribeDBSubnetGroups",
      "rds:ListTagsForResource",
      "redshift:DescribeClusterParameterGroups",
      "redshift:DescribeClusterParameters",
      "redshift:DescribeClusterSecurityGroups",
      "redshift:DescribeClusters",
      "route53:ListHostedZones",
      "route53:ListResourceRecordSets",
      "route53domains:ListDomains",
      "s3:GetBucketAcl",
      "s3:GetBucketLocation",
      "s3:GetBucketLogging",
      "s3:GetBucketPolicy",
      "s3:GetBucketTagging",
      "s3:GetBucketVersioning",
      "s3:GetBucketWebsite",
      "s3:GetEncryptionConfiguration",
      "s3:GetBucketPublicAccessBlock",
      "s3:ListAllMyBuckets",
      "secretsmanager:ListSecrets",
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetResourcePolicy",
      "ses:GetIdentityDkimAttributes",
      "ses:GetIdentityPolicies",
      "ses:ListIdentities",
      "ses:ListIdentityPolicies",
      "ssm:DescribeParameters",
      "ssm:GetParameters",
      "sns:GetTopicAttributes",
      "sns:ListSubscriptions",
      "sns:ListTopics",
      "sqs:GetQueueAttributes",
      "sqs:ListQueues"
    ]
    resources = ["*"]
  }
}

# CI CD Access policies
resource "aws_iam_policy" "github_oidc_access_policy1" {
  name        = "${upper(var.project)}-github-oidc-1"
  description = "Provide pipeline level access to whomever assumes a role with this policy attached"
  policy      = data.aws_iam_policy_document.github_oidc_access_1.json

  tags = {
    Name = "${upper(var.project)}-github-oidc-1"
  }
}

resource "aws_iam_policy" "github_oidc_access_policy2" {
  name        = "${upper(var.project)}-github-oidc-2"
  description = "Provide pipeline level access to whomever assumes a role with this policy attached"
  policy      = data.aws_iam_policy_document.github_oidc_access_2.json

  tags = {
    Name = "${upper(var.project)}-github-oidc-2"
  }
}

resource "aws_iam_policy" "github_oidc_access_policy_global" {
  name        = "${upper(var.project)}-github-oidc-global"
  description = "Provide pipeline level access to whomever assumes a role with this policy attached"
  policy      = data.aws_iam_policy_document.github_oidc_access_global_region.json

  tags = {
    Name = "${upper(var.project)}-github-oidc-global"
  }
}

resource "aws_iam_policy" "github_oidc_access_policy_terraform" {
  name        = "${upper(var.project)}-github-oidc-terraform"
  description = "Provide pipeline level access to whomever assumes a role with this policy attached"
  policy      = data.aws_iam_policy_document.github_oidc_access_terraform.json

  tags = {
    Name = "${upper(var.project)}-github-oidc-terraform"
  }
}

resource "aws_iam_policy" "github_oidc_access_policy_scoutsuite" {
  name        = "${upper(var.project)}-github-oidc-scoutsuite"
  description = "Provide pipeline level access to whomever assumes a role with this policy attached"
  policy      = data.aws_iam_policy_document.github_oidc_access_scoutsuite.json

  tags = {
    Name = "${upper(var.project)}-github-oidc-scoutsuite"
  }
}

resource "aws_iam_policy" "github_oidc_prevent_sso_privilege_escalation" {
  name        = "${upper(var.project)}-github-oidc-prevent-privilege-escalation"
  description = "Prevent privilege escalation"
  policy      = data.aws_iam_policy_document.prevent_privilege_escalation_sso_limited_policy.json

  tags = {
    Name = "${upper(var.project)}-github-oidc-scoutsuite"
  }
}
