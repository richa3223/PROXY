# VPC Security Group for the lambda (Internet Access Enabled)

resource "aws_security_group" "lambda_base_internet_access" {
  #checkov:skip=CKV2_AWS_5: Ensure that Security Groups are attached to another resource #reason: Seems to be a checkov false positive, that happends when the security group isn't referenced in the same file its defined in. There is an issue about it https://github.com/bridgecrewio/checkov/issues/1203
  name        = "${local.workspace}-lambda-base-internet-access-sg"
  description = "Security Group for Lambda to provide basic access permissions"
  vpc_id      = module.vpc.vpc_id

  tags = {
    "Name" = "${local.workspace}-lambda-base-internet-access-sg"
  }
}

resource "aws_security_group_rule" "lambda_base_internet_access" {
  security_group_id = aws_security_group.lambda_base_internet_access.id
  type              = "egress"
  description       = "Internet HTTPS access"
  from_port         = 443
  protocol          = "TCP"
  to_port           = 443
  cidr_blocks       = ["0.0.0.0/0"]
}

# VPC Security Group for the lambda (Private Access Only)
resource "aws_security_group" "lambda_base_private_access" {
  #checkov:skip=CKV2_AWS_5: Ensure that Security Groups are attached to another resource #reason: Seems to be a checkov false positive, that happends when the security group isn't referenced in the same file its defined in. There is an issue about it https://github.com/bridgecrewio/checkov/issues/1203
  name        = "${local.workspace}-lambda-base-private-access-sg"
  description = "Security Group for Lambda to provide basic access permissions"
  vpc_id      = module.vpc.vpc_id

  tags = {
    "Name" = "${local.workspace}-lambda-base-private-access-sg"
  }
}

# Only allow traffic to the security group where all the endpoints are held in.
resource "aws_security_group_rule" "lambda_base_private_access" {
  security_group_id        = aws_security_group.lambda_base_private_access.id
  type                     = "egress"
  description              = "Internal VPC access only rule"
  from_port                = 443
  protocol                 = "TCP"
  to_port                  = 443
  source_security_group_id = aws_security_group.endpoints.id
}
