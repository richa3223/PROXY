data "github_user" "all" {
  for_each = toset(local.usernames)
  username = each.key
}
