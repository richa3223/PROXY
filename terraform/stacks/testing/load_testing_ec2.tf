data "aws_subnet" "eu_west_2_a_public_subnet" {
  tags = {
    Name = "${local.common_stack_workspace}-vpc-public-eu-west-2a"
  }
}

# Load Testing Master EC2 Instance
resource "aws_instance" "load_testing_master_instance" {
  #checkov:skip=CKV_AWS_135: Ensure that EC2 is EBS optimized
  #checkov:skip=CKV_AWS_88: EC2 instance should not have public IP.
  #checkov:skip=CKV_AWS_79: Ensure Instance Metadata Service Version 1 is not enabled
  #checkov:skip=CKV_AWS_8: Ensure all data stored in the Launch configuration or instance Elastic Blocks Store is securely encrypted
  #checkov:skip=CKV_AWS_126: Ensure that detailed monitoring is enabled for EC2 instances

  depends_on = [
    aws_iam_role.load_testing_role,
    aws_secretsmanager_secret_version.load_testing_key_pair
  ]

  ami                         = "ami-053a617c6207ecc7b"
  subnet_id                   = data.aws_subnet.eu_west_2_a_public_subnet.id
  instance_type               = "t2.micro"
  availability_zone           = "eu-west-2a"
  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.load_testing_security_group.id]

  key_name = aws_key_pair.load_testing_key_pair.key_name


  user_data = base64encode(templatefile(
    "cloud-init.sh",
    {
      hostname = "master"
      key_pair = aws_secretsmanager_secret.load_testing_key_pair.arn
    }
    )
  )

  iam_instance_profile = aws_iam_instance_profile.load_testing_role_instance_profile.name

  tags = {
    Name = "${local.workspace}-load-testing-master"
  }

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }

}

# Load Testing Worker EC2 Instance
resource "aws_instance" "load_testing_worker_instance" {
  #checkov:skip=CKV_AWS_135: Ensure that EC2 is EBS optimized
  #checkov:skip=CKV_AWS_88: EC2 instance should not have public IP.
  #checkov:skip=CKV_AWS_79: Ensure Instance Metadata Service Version 1 is not enabled
  #checkov:skip=CKV_AWS_8: Ensure all data stored in the Launch configuration or instance Elastic Blocks Store is securely encrypted
  #checkov:skip=CKV_AWS_126: Ensure that detailed monitoring is enabled for EC2 instances

  depends_on = [
    aws_iam_role.load_testing_role,
    aws_secretsmanager_secret_version.load_testing_key_pair
  ]

  ami                         = "ami-053a617c6207ecc7b"
  subnet_id                   = data.aws_subnet.eu_west_2_a_public_subnet.id
  instance_type               = "t2.micro"
  availability_zone           = "eu-west-2a"
  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.load_testing_security_group.id]

  key_name = aws_key_pair.load_testing_key_pair.key_name

  user_data = base64encode(templatefile(
    "cloud-init.sh",
    {
      hostname = "worker"
      key_pair = aws_secretsmanager_secret.load_testing_key_pair.arn
    }
    )
  )

  iam_instance_profile = aws_iam_instance_profile.load_testing_role_instance_profile.name

  tags = {
    Name = "${local.workspace}-load-testing-worker"
  }

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }
}
