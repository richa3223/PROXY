# Load Testing IAM Policy and Role

data "aws_iam_policy_document" "load_testing_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "load_testing_role" {
  name               = "${var.environment}-${local.workspace}-load-testing-role"
  assume_role_policy = data.aws_iam_policy_document.load_testing_assume_role.json
}

data "aws_iam_policy_document" "load_testing_role_access_policy" {
  #checkov:skip=CKV_AWS_111: Ensure IAM policies does not allow write access without constraints
  #checkov:skip=CKV_AWS_108: Ensure IAM policies does not allow data exfiltration

  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = [
      module.load_testing_bucket.bucket_arn,
      "${module.load_testing_bucket.bucket_arn}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecrets",
    ]
    resources = [aws_secretsmanager_secret.load_testing_key_pair.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey"
    ]
    resources = [module.load_testing_bucket.kms_key_arn,
    aws_secretsmanager_secret.load_testing_key_pair.kms_key_id]
  }
}


resource "aws_iam_role_policy" "load_testing_role_access_policy" {
  name   = "${var.environment}-${local.workspace}-load-testing-access-policy"
  role   = aws_iam_role.load_testing_role.id
  policy = data.aws_iam_policy_document.load_testing_role_access_policy.json
}

resource "aws_iam_role_policy_attachment" "cloudwatch_agent_policy" {
  role       = aws_iam_role.load_testing_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "ssm_managed_instance_policy" {
  role       = aws_iam_role.load_testing_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "load_testing_role_instance_profile" {
  name = "${var.environment}-${local.workspace}-load-testing-instance-profile"
  role = aws_iam_role.load_testing_role.name
}
