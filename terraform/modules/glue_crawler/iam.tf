# Define role and specify what resource can assume this role
resource "aws_iam_role" "glue_iam_role" {
  name               = "${var.workspace}-${var.crawler_name}-glue_iam_role"
  assume_role_policy = data.aws_iam_policy_document.glue_assume_role_policy_document.json
}

# Define role policy attachments
resource "aws_iam_policy" "glue_iam_policy" {
  name   = "${var.workspace}-${var.crawler_name}-glue-policy"
  policy = data.aws_iam_policy_document.glue_resource_access_policy_document.json
}

resource "aws_iam_policy" "glue_log_policy" {
  name   = "${var.workspace}-${var.crawler_name}-glue-log-policy"
  policy = data.aws_iam_policy_document.glue_log_access_policy_document.json
}

# Attach policies to the role created
resource "aws_iam_role_policy_attachment" "glue_policy_attachment" {
  role       = aws_iam_role.glue_iam_role.name
  policy_arn = aws_iam_policy.glue_iam_policy.arn
}

resource "aws_iam_role_policy_attachment" "glue_log_access_attachment" {
  role       = aws_iam_role.glue_iam_role.name
  policy_arn = aws_iam_policy.glue_log_policy.arn
}
