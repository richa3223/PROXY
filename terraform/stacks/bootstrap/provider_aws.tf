# The default AWS provider in the default region
provider "aws" {
  region = var.region

  default_tags {
    tags = {
      TagVersion         = "1"
      Programme          = "Spine"
      Project            = "proxy"
      DataClassification = "1"
      Environment        = "ba0"
      ServiceCategory    = "N/A"
      OnOffPattern       = "AlwaysOn"
      Tool               = "terraform"
    }
  }
}
