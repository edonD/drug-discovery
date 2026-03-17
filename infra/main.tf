terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_instance" "drug" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "c6a.4xlarge"
  key_name                    = "schemato-key"
  vpc_security_group_ids      = ["sg-09f40e8c99d04ba75"]
  subnet_id                   = "subnet-0ae32ef43f5322974"
  associate_public_ip_address = true

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
    throughput  = 250
    iops        = 3000
  }

  tags = {
    Name    = "drug-discovery"
    Project = "drug-discovery"
  }
}

output "ip" {
  value = aws_instance.drug.public_ip
}

output "ssh" {
  value = "ssh -i ~/.ssh/schemato-key.pem ubuntu@${aws_instance.drug.public_ip}"
}
