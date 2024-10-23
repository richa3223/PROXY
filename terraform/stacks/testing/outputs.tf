output "ec2_instance_public_key" {
  value = aws_key_pair.load_testing_key_pair.public_key
}

output "ec2_instance_private_key_arn" {
  value = aws_secretsmanager_secret.load_testing_key_pair.arn
}

output "load_testing_master_instance_ip_address" {
  value = aws_instance.load_testing_master_instance.public_ip
}

output "load_testing_worker_instance_ip_address" {
  value = aws_instance.load_testing_worker_instance.public_ip
}
