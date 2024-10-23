resource "aws_glue_crawler" "data_crawler" {
  name         = var.crawler_name
  role         = aws_iam_role.glue_iam_role.arn
  table_prefix = var.table_prefix

  # Target data catalogue to store schema/index to.
  database_name = var.database_name

  # Chron expression that specified the schedule of the crawler, the below runs the crawler every day at midnight.
  schedule = "cron(00 00 * * ? *)"

  # Target data to crawl.
  s3_target {
    path = "s3://${var.bucket_name}"
  }
  configuration = jsonencode(
    {
      Grouping = {
        TableGroupingPolicy = "CombineCompatibleSchemas"
      }
      CrawlerOutput = {
        Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
      }
      Version = 1
    }
  )

  # If a schema change is detected, we want to deprecate the old one but keep it, and make the new schema available.
  schema_change_policy {
    delete_behavior = "DEPRECATE_IN_DATABASE"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  # Run crawler on first deployment.
  provisioner "local-exec" {
    command = "aws glue start-crawler --name ${self.name}"
  }
  tags = merge(var.tags, local.common_tags)

  security_configuration = aws_glue_security_configuration.glue_security_configuration.name
}

resource "aws_glue_security_configuration" "glue_security_configuration" {
  name = "${var.workspace}-${var.crawler_name}-glue-crawler-security-configuration"

  encryption_configuration {
    cloudwatch_encryption {
      cloudwatch_encryption_mode = "SSE-KMS"
      kms_key_arn                = aws_kms_key.glue_key.arn
    }

    job_bookmarks_encryption {
      job_bookmarks_encryption_mode = "CSE-KMS"
      kms_key_arn                   = aws_kms_key.glue_key.arn
    }

    s3_encryption {
      s3_encryption_mode = "SSE-KMS"
      kms_key_arn        = aws_kms_key.glue_key.arn
    }
  }
}
