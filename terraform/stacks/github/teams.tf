resource "github_team" "all" {
  for_each = local.teams
  name     = each.key

  # import was going to change these two attributes so are set to be ignored
  lifecycle {
    ignore_changes = [
      description,
      privacy
    ]
  }
}

resource "github_team_membership" "members" {
  for_each = { for tm in local.team_members : tm.name => tm }

  team_id  = each.value.team_id
  username = each.value.username
  role     = each.value.role
}
