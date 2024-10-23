resource "aws_athena_workgroup" "sensitive_athena_workgroup" {
  name = "${local.workspace}-sensitive-athena-workgroup"

  depends_on = [aws_kms_key.athena_sensitive_s3_bucket_key]

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location       = "s3://${local.sensitive_audit_athena_query_destination.bucket_name}/"
      expected_bucket_owner = data.aws_caller_identity.current.account_id
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = aws_kms_key.athena_sensitive_s3_bucket_key.arn
      }
    }
  }
}

resource "aws_athena_workgroup" "standard_athena_workgroup" {
  name = "${local.workspace}-standard-athena-workgroup"

  depends_on = [aws_kms_key.athena_standard_s3_bucket_key]

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location       = "s3://${local.standard_audit_athena_query_destination.bucket_name}/"
      expected_bucket_owner = data.aws_caller_identity.current.account_id
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = aws_kms_key.athena_standard_s3_bucket_key.arn
      }
    }
  }
}