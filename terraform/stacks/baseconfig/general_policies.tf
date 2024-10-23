data "aws_iam_policy_document" "prevent_privilege_escalation_policy" {
  # Please consider any changes to this policy very carefully. It is designed to prevent privilege escalation.

  statement {
    sid    = "PreventPermissionEscalation"
    effect = "Deny"

    actions = [
      "iam:AddUserToGroup",
      "iam:AttachRolePolicy",
      "iam:AttachUserPolicy",
      "iam:CreateAccessKey",
      "iam:CreateLoginProfile",
      "iam:CreatePolicy",
      "iam:CreatePolicyVersion",
      "iam:CreatePolicyVersion",
      "iam:CreateRole",
      "iam:CreateUser",
      "iam:DeletePolicy",
      "iam:DeleteRole",
      "iam:DeleteRolePermissionsBoundary",
      "iam:DeleteRolePolicy",
      "iam:DeleteUserPermissionsBoundary",
      "iam:DeleteUserPolicy",
      "iam:DetachRolePolicy",
      "iam:PassRole",
      "iam:PutRolePermissionsBoundary",
      "iam:PutRolePolicy",
      "iam:PutUserPermissionsBoundary",
      "iam:SetDefaultPolicyVersion",
      "iam:UpdateAssumeRolePolicy",
      "iam:UpdateLoginProfile",
      "iam:UpdateRole",
      "iam:UpdateRoleDescription",
      "sts:AssumeRole"
    ]
    resources = ["*"]
  }
}


data "aws_iam_policy_document" "prevent_privilege_escalation_sso_limited_policy" {
  # Please consider any changes to this policy very carefully. It is designed to prevent privilege escalation.
  statement {

    # Stop GH actions from escalating privileges or removing the permissions blockers
    sid    = "RestrictPrivilegeEscalation"
    effect = "Deny"

    actions = [
      "iam:AddUserToGroup",
      "iam:AttachRolePolicy",
      "iam:AttachUserPolicy",
      "iam:CreateAccessKey",
      "iam:CreateLoginProfile",
      "iam:CreatePolicyVersion",
      "iam:CreateRole",
      "iam:CreateUser",
      "iam:DeleteRole",
      "iam:DeleteRolePermissionsBoundary",
      "iam:DeleteRolePolicy",
      "iam:DeleteUserPermissionsBoundary",
      "iam:DeleteUserPolicy",
      "iam:DetachRolePolicy",
      "iam:PassRole",
      "iam:PutRolePermissionsBoundary",
      "iam:PutRolePolicy",
      "iam:PutUserPermissionsBoundary",
      "iam:SetDefaultPolicyVersion",
      "iam:UpdateAssumeRolePolicy",
      "iam:UpdateLoginProfile",
      "iam:CreatePolicyVersion",
      "iam:UpdateRole",
      "iam:UpdateRoleDescription",
      "sts:AssumeRole"
    ]

    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/*PermissionsBoundary",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-reserved/*", # SSO roles
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${upper(var.project)}-ReadOnly",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/PVRS-nhsd-demog-proxy-${var.environment}-OIDC",
    ]
  }
}
