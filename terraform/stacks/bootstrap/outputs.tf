# Statefile bucket outputs
output "statefile_bucket_arn" {
  value = aws_s3_bucket.statefile.arn
}

output "statefile_bucket_name" {
  value = aws_s3_bucket.statefile.id
}

# Audit bucket outputs
output "audit_bucket_arn" {
  value = aws_s3_bucket.audit.arn
}

output "audit_bucket_name" {
  value = aws_s3_bucket.audit.id
}

# TF Audit KMS Key Output
output "audit_kms_key_arn" {
  value = aws_kms_key.bootstrap_s3_audit_bucket_key.arn
}

output "audit_kms_key_id" {
  value = aws_kms_key.bootstrap_s3_audit_bucket_key.id
}

# TF State KMS Key Output
output "statefile_kms_key_arn" {
  value = aws_kms_key.bootstrap_s3_statefile_bucket_key.arn
}

output "statefile_kms_key_id" {
  value = aws_kms_key.bootstrap_s3_statefile_bucket_key.id
}

# DynamoDB TF Lock Table Outputs
output "tflock_db" {
  value = aws_dynamodb_table.terraform_lock_db.name
}