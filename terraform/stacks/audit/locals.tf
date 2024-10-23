locals {
  # tflint-ignore: terraform_unused_declarations
  workspace              = lower(terraform.workspace)
  common_stack_workspace = var.use_shared_common_stack ? var.main_workspace : lower(terraform.workspace)
  aws_region             = "eu-west-2"
  # tflint-ignore: terraform_unused_declarations

  ###########################################
  # KMS locals
  ###########################################
  kms_key_deletion_duration = 14

  tags = {
    Environment = var.environment
    Programme   = "NPA"
    Project     = "Proxy"
    TagVersion  = "1"
    Tool        = "Terraform"
    Workspace   = terraform.workspace
    Stack       = "audit"
  }

  match_validation_result_pattern = jsonencode({ "detail-type" : ["Validation Successful", "Validation Failed", "Validation Errored"] })

  standard_s3_bucket_names = {
    queryable_audit_events = "queryable-audit-events"
    standard_query_results = "standard-query-results"
    log_store              = "log-store"
  }

  sensitive_s3_bucket_names = {
    sensitive_audit_events  = "sensitive-audit-events"
    sensitive_query_results = "sensitive-query-results"
  }

  standard_audit_kinesis_firehose_destination  = module.standard_s3_buckets["queryable-audit-events"]
  sensitive_audit_kinesis_firehose_destination = module.sensitive_s3_buckets["sensitive-audit-events"]
  standard_audit_athena_query_destination      = module.standard_s3_buckets["standard-query-results"]
  sensitive_audit_athena_query_destination     = module.sensitive_s3_buckets["sensitive-query-results"]

  # TODO: Discuss appropriate retention period - NPA-1706
  firehose_log_retention_in_days = 30

  audit_bucket_prefix = "!{partitionKeyFromQuery:detailType}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"

}
