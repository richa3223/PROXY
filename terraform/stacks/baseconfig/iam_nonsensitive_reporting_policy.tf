# This policy name is associated in SSO, therfore will only work with resources on the main workspace.
# This policy has been moved from the audit stack to baseconfig to enable the audit stack to be destroyed easly if needs be.
# Resource names are specified explicitly here since there is no way to get them dynamically in the baseconfig stack as its deployed before the audit stack.

resource "aws_iam_policy" "nonsensitive-reporting" {
  name = "${upper(var.project)}-main-Nonsensitive-Reporting"

  policy = templatefile("${path.module}/templates/report-policy.tpl", {
    aws_region       = var.primary_region
    aws_account      = data.aws_caller_identity.current.account_id
    query_bucket     = "main-${var.environment}-queryable-audit-events-bucket"
    result_bucket    = "main-${var.environment}-standard-query-results-bucket"
    crawler          = "main-queryable_data_glue_crawler"
    catalog_database = "main-queryable-data-catalogue"
    workgroup        = "main-standard-athena-workgroup"
  })

  tags = {
    Name = "${upper(var.project)}-nonsensitive-reporting"
  }
}

resource "aws_iam_policy" "nonsensitive-reporting-prevent-privilege-escalation" {
  name = "${upper(var.project)}-main-Nonsensitive-Reporting-PreventPrivilegeEscalation"

  policy = data.aws_iam_policy_document.prevent_privilege_escalation_policy.json

  tags = {
    Name = "${upper(var.project)}-nonsensitive-reporting-prevent-privilege-escalation"
  }
}
