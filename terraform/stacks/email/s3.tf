module "email_template_bucket" {
  source                   = "../../modules/s3"
  bucket_name              = "${local.workspace}-${var.environment}-email-template-bucket"
  workspace                = local.workspace
  enable_bucket_versioning = true
  audit_bucket_id          = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  vpc_endpoint_id          = data.aws_vpc_endpoint.s3.id
  force_destroy            = var.environment == "prod" ? false : true
  tags = {
    "Description" : "Email template bucket for storing email subject and body"
  }
}

resource "null_resource" "adult_to_child_template" {
  depends_on = [module.email_template_bucket]
  triggers = {
    bucket_name   = module.email_template_bucket.bucket_name
    file_contents = file("${path.module}/email_templates/adult_to_child_template.json")
  }

  provisioner "local-exec" {
    command = "aws s3 cp ${path.module}/email_templates/adult_to_child_template.json s3://${module.email_template_bucket.bucket_name}"
  }
}

module "hydrated_email_temporary_storage_bucket" {
  source          = "../../modules/s3"
  bucket_name     = "${local.workspace}-${var.environment}-hydrated-email-temporary-storage-bucket"
  workspace       = local.workspace
  audit_bucket_id = "${var.project}-${data.aws_iam_account_alias.current.account_alias}-s3-audit"
  vpc_endpoint_id = data.aws_vpc_endpoint.s3.id
  force_destroy   = var.environment == "prod" ? false : true
  retention_days  = 7
  tags = {
    "Description" : "Hydrated email temporary storage bucket for storing full emails including email subject and content"
  }
}