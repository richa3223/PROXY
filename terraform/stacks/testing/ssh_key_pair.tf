# SSH Key Pair used for the EC2 Instances

resource "tls_private_key" "load_testing_key_pair" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "aws_key_pair" "load_testing_key_pair" {
  key_name   = "${local.workspace}-load-testing-key-pair"
  public_key = tls_private_key.load_testing_key_pair.public_key_openssh
}

resource "random_string" "random" {
  length  = 16
  special = false
}

resource "aws_secretsmanager_secret" "load_testing_key_pair" {
  #checkov:skip=CKV2_AWS_57: Ensure Secrets Manager secrets should have automatic rotation enabled

  name        = "/${local.workspace}/load-testing-key-pair-${random_string.random.result}"
  description = "PEM key for ssh access to EC2 instances and GitHub"
  kms_key_id  = aws_kms_key.load_testing_key_pair_secrets_manager_key.arn

  depends_on = [
    aws_kms_key.load_testing_key_pair_secrets_manager_key,
    aws_kms_key_policy.load_testing_key_pair_secrets_manager_key_policy_attach
  ]
}

resource "aws_secretsmanager_secret_version" "load_testing_key_pair" {
  secret_id     = aws_secretsmanager_secret.load_testing_key_pair.id
  secret_string = tls_private_key.load_testing_key_pair.private_key_pem
}

# Load Testing Secrets Manager KMS Encryption Key
resource "aws_kms_key" "load_testing_key_pair_secrets_manager_key" {
  description             = "${local.workspace} - KMS Key for Load Testing Secrets Manager"
  deletion_window_in_days = local.kms_key_deletion_duration
  enable_key_rotation     = true

  tags = {
    "Description" = "${local.workspace} - KMS Key for Load Testing Secrets Manager"
  }
}

resource "aws_kms_key_policy" "load_testing_key_pair_secrets_manager_key_policy_attach" {
  key_id = aws_kms_key.load_testing_key_pair_secrets_manager_key.id
  policy = data.aws_iam_policy_document.load_testing_key_pair_secrets_manager_kms_policy.json
}

data "aws_iam_policy_document" "load_testing_key_pair_secrets_manager_kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = [aws_kms_key.load_testing_key_pair_secrets_manager_key.arn]
  }

  statement {
    sid    = "Allow Secrets Manager to use the KMS key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["secretsmanager.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.load_testing_key_pair_secrets_manager_key.arn]
  }
}
