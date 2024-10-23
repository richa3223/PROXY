resource "aws_iam_openid_connect_provider" "aws_oidc_provider" {
  url             = var.url
  client_id_list  = coalescelist(var.client_id_list, ["sts.${data.aws_partition.current.dns_suffix}"])
  thumbprint_list = data.tls_certificate.oidc_tls_cert.certificates[*].sha1_fingerprint

  tags = {
    Name = "${upper(var.project)}-${data.aws_iam_account_alias.current.account_alias}-oidc-provider"
  }
}

resource "aws_iam_role" "github_oidc_role" {
  name                 = "${upper(var.project)}-${data.aws_iam_account_alias.current.account_alias}-OIDC"
  assume_role_policy   = data.aws_iam_policy_document.github_oidc_asume_role.json
  permissions_boundary = aws_iam_policy.permissions_boundary.arn

  tags = {
    Name = "${upper(var.project)}-${data.aws_iam_account_alias.current.account_alias}-oidc"
  }
}

resource "aws_iam_role_policy_attachment" "github_oidc_policy1" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_oidc_access_policy1.arn
}

resource "aws_iam_role_policy_attachment" "github_oidc_policy2" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_oidc_access_policy2.arn
}

resource "aws_iam_role_policy_attachment" "github_oidc_policy_global" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_oidc_access_policy_global.arn
}

resource "aws_iam_role_policy_attachment" "github_oidc_policy_terraform" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_oidc_access_policy_terraform.arn
}

resource "aws_iam_role_policy_attachment" "github_oidc_policy_scoutsuite" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_oidc_access_policy_scoutsuite.arn
}

resource "aws_iam_role_policy_attachment" "github_oidc_prevent_sso_privilege_escalation" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_oidc_prevent_sso_privilege_escalation.arn
}
