resource "aws_dynamodb_table" "patient_relationship" {
  name                        = "${local.workspace}-${var.project}-patient-relationship"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "ReferenceCode"
  deletion_protection_enabled = var.environment == "dev" || var.environment == "qa" ? false : true

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "ReferenceCode"
    type = "S"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb_key.arn
  }

  point_in_time_recovery {
    enabled = true
  }

}

resource "aws_dynamodb_table" "pds_response_cache" {
  name                        = "${local.workspace}-${var.project}-pds-response-cache"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "CacheKey"
  deletion_protection_enabled = var.environment == "dev" || var.environment == "qa" ? false : true

  stream_enabled = false

  attribute {
    name = "CacheKey"
    type = "S"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb_key.arn
  }

  point_in_time_recovery {
    enabled = true
  }

}
