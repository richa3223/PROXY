environment = "qa"
global_tags = {
  iac = true
}
region                               = "eu-west-2"
vpc_cidr                             = "10.1.0.0/16"
aws_azs                              = ["eu-west-2a", "eu-west-2b", "eu-west-2c"]
internet_gateway_enabled             = 1
number_of_additional_public_subnets  = 0
number_of_additional_private_subnets = 0
