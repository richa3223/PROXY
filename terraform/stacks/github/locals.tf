locals {
  teams = {
    "proxy-service-admins"     = 8742505
    "proxy-service-developers" = 8742500
  }

  # Parse team member files
  team_members_path = "team-members"
  team_members_files = {
    for file in fileset(local.team_members_path, "*.csv") :
    trimsuffix(file, ".csv") => csvdecode(file("${local.team_members_path}/${file}"))
  }
  # Create temp object that has team ID and CSV contents
  team_members_temp = flatten([
    for team, members in local.team_members_files : [
      for tn, t in github_team.all : {
        name    = t.name
        id      = t.id
        slug    = t.slug
        members = members
      } if t.slug == team
    ]
  ])
  # Create object for each team-user relationship
  team_members = flatten([
    for team in local.team_members_temp : [
      for member in team.members : {
        name     = "${team.slug}-${member.username}"
        team_id  = team.id
        username = member.username
        role     = member.role
      }
    ]
  ])

  usernames = distinct([for item in local.team_members : item.username])

  # Parse repo team membership files
  repo_teams_path = "repos-team"
  repo_teams_files = {
    for file in fileset(local.repo_teams_path, "*.csv") :
    trimsuffix(file, ".csv") => csvdecode(file("${local.repo_teams_path}/${file}"))
  }

  proxy_validated_relationships_service_environments = {
    "prod" = {
      can_admins_bypass   = false
      prevent_self_review = false
      deployment_branch_policy = {
        custom_branch_policies = true
        protected_branches     = false
      }
      reviewers = {
        users = [
          data.github_user.all["chris-young-12-nhs"].id
        ]
      }
    }
    "qa" = {
      can_admins_bypass   = false
      prevent_self_review = false
      deployment_branch_policy = {
        custom_branch_policies = true
        protected_branches     = false
      }
      reviewers = {
        users = [
          data.github_user.all["chris-young-12-nhs"].id,
          data.github_user.all["LeoKHoward"].id,
          data.github_user.all["JackPlowman"].id
        ]
      }
    }
    "int" = {
      can_admins_bypass   = false
      prevent_self_review = false
      deployment_branch_policy = {
        custom_branch_policies = true
        protected_branches     = false
      }
      reviewers = {
        users = [
          data.github_user.all["chris-young-12-nhs"].id,
          data.github_user.all["LeoKHoward"].id,
          data.github_user.all["JackPlowman"].id
        ]
      }
    }
    "dev" = {
      can_admins_bypass   = null
      prevent_self_review = null
      deployment_branch_policy = {
        custom_branch_policies = true
        protected_branches     = false
      }
      reviewers = null
    }
  }
}
