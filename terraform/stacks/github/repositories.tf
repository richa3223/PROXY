data "github_repository" "proxy-validated-relationships-service" {
  full_name = "NHSDigital/proxy-validated-relationships-service"
}

resource "github_repository_environment" "proxy-validated-relationships-service" {
  for_each    = local.proxy_validated_relationships_service_environments
  environment = each.key
  repository  = data.github_repository.proxy-validated-relationships-service.name

  can_admins_bypass = local.proxy_validated_relationships_service_environments[each.key].can_admins_bypass
  deployment_branch_policy {
    custom_branch_policies = local.proxy_validated_relationships_service_environments[each.key].deployment_branch_policy.custom_branch_policies
    protected_branches     = local.proxy_validated_relationships_service_environments[each.key].deployment_branch_policy.protected_branches
  }

  prevent_self_review = local.proxy_validated_relationships_service_environments[each.key].prevent_self_review

  dynamic "reviewers" {
    for_each = local.proxy_validated_relationships_service_environments[each.key].reviewers != null ? [1] : []
    content {
      users = local.proxy_validated_relationships_service_environments[each.key].reviewers.users
    }
  }

}

resource "github_team_repository" "proxy-validated-relationships-service" {
  repository = data.github_repository.proxy-validated-relationships-service.name
  for_each = {
    for team in local.repo_teams_files["proxy-validated-relationships-service"] :
    team.team_name => {
      team_id    = github_team.all[team.team_name].id
      permission = team.permission
    } if lookup(github_team.all, team.team_name, false) != false
  }
  team_id    = each.value.team_id
  permission = each.value.permission
}

data "github_repository" "validated-relationships-service-api" {
  full_name = "NHSDigital/validated-relationships-service-api"
}

resource "github_team_repository" "validated-relationships-service-api" {
  repository = data.github_repository.validated-relationships-service-api.name
  for_each = {
    for team in local.repo_teams_files["validated-relationships-service-api"] :
    team.team_name => {
      team_id    = github_team.all[team.team_name].id
      permission = team.permission
    } if lookup(github_team.all, team.team_name, false) != false
  }
  team_id    = each.value.team_id
  permission = each.value.permission
}
