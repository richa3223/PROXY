# DynamoDB Lock Table
resource "aws_dynamodb_table" "terraform_lock_db" {
  name         = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-tflock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb_kms_key.arn
  }

  tags = {
    Name = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-tflock"
  }
}
