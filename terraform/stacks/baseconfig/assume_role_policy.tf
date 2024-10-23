################################################################################
# Policy to define who can assume a role. This is reused in the other .tf files
################################################################################

data "aws_iam_policy_document" "pipeline_assume_role" {

  statement {
    sid     = "PipelineRole"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      identifiers = [
        "arn:aws:iam::${var.account_id["nhsd-identities"]}:root",
      ]

      type = "AWS"
    }

    condition {
      test     = "BoolIfExists"
      values   = ["true"]
      variable = "aws:MultiFactorAuthPresent"
    }
  }
}

################################################################################
# GitHub OIDC Assume Role Policy Document
################################################################################

data "aws_iam_policy_document" "github_oidc_asume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.aws_oidc_provider.arn]
    }

    actions = ["sts:AssumeRoleWithWebIdentity"]

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = var.allowed_repos
    }
  }
}