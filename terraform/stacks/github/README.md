# Github stack

The Github stack is used for managing team membership and access to VRS repos. It exists only in the `dev` AWS environment.

## Scope

This stack is used for maintaining Teams, Repositories and Teams relationships to Repositories

## Configuration

To update team members edit the `teamname.csv` file in [`team-members`](team-members) e.g. [`proxy-service-admins.csv`](team-members/proxy-service-admins.csv).

First line is the header line `username,role`. Following lines are the GitHub username followed by the role in the team.

To update which teams have access to a repository edit the `reponame.csv`
file in [`repos-team`](repos-team) e.g. [`proxy-validated-relationships-service.csv`](repos-team/proxy-validated-relationships-service.csv).

First line is the header line `team_name,permission`. Following lines are the GitHub team name followed by the permissions that team have on the repository.

Note that roles and permissions are as used by the [GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28) rather than the names that appear in the GitHub UI.

## Deployment

Ensure you are authenticated with GitHub by setting the `GITHUB_TOKEN` environment variable to your Personal Access Token. This token must have access to the NHSDigital organisation and you must be a maintainer of the GitHub teams that are being managed.

Do not attempt to run terraform commands directly in this directory as the root `Makefile` ensures that the correct location
of the state file in S3 is used.

Use `make` in the project root e.g.

- Plan: `make terraform tf-command=plan env=dev stack=github workspace=main`
- Apply: `make terraform tf-command=apply env=dev stack=github workspace=main`
