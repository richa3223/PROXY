resource "aws_security_group" "load_testing_security_group" {

  name        = "${var.environment}-${local.workspace}-load-testing-security-group"
  description = "Enable Load Testing in ${var.environment}"
  vpc_id      = data.aws_vpc.proxy_vpc.id

  ingress {
    description = "Locust Port"
    from_port   = 8089
    to_port     = 8089
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.proxy_vpc.cidr_block]
  }

  ingress {
    description = "SSH Port"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = local.cidr_block_list
  }

  ingress {
    description = "Allow proxy service access"
    from_port   = 5557
    to_port     = 5557
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.proxy_vpc.cidr_block]
  }

  ingress {
    description = "Enable ping"
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = [data.aws_vpc.proxy_vpc.cidr_block]
  }

  egress {
    description = "Full outbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
