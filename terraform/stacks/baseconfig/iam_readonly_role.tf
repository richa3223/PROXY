# Read Only Access Role
resource "aws_iam_role" "readonly_access_role" {
  name                 = "${upper(var.project)}-ReadOnly"
  assume_role_policy   = data.aws_iam_policy_document.pipeline_assume_role.json
  permissions_boundary = aws_iam_policy.permissions_boundary.arn

  tags = {
    Name = "${upper(var.project)}-ReadOnly"
  }
}

# Attach ReadOnlyAccess to ReadOnlyRole
resource "aws_iam_role_policy_attachment" "readonly_access" {
  role       = aws_iam_role.readonly_access_role.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}
