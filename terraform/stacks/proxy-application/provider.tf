provider "aws" {
  region = local.aws_region

  default_tags {
    tags = local.tags
  }
}

provider "aws" {
  alias  = "us"
  region = local.aws_global_region

  default_tags {
    tags = local.tags
  }
}
