/*
  Initial configuration of a terraform-state bucket and DynamoDB lock table must be done to a local state-file.
  Please follow instructions in the README.md file.
  Although you don't technically need the state file in the S3 bucket as this is a one time build it does help to
  have it there just in case we need to update the bootstrap configuration down-the-line.
*/

terraform {
  #backend "local" { path = "./terraform-state/bootstrap.tfstate" }
  backend "s3" {}
}
