provider "aws" {
  region = "eu-west-2"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "c23-yusuf-deployment-security-group"
  description = "Allow PostgreSQL access for me"

  ingress {
    description = "PostgreSQL access from my local machine"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "c23-yusuf-deployment-security-group"
  }
}

resource "aws_db_instance" "museum_db" {
  identifier             = "c23-yusuf-museum-db"
  engine                 = "postgres"
  engine_version         = "17.9"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_name                = "museum"
  username               = "museum_admin"
  password               = var.db_password
  publicly_accessible    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true

  tags = {
    Name = "c23-yusuf-museum-db"
  }
}

resource "aws_key_pair" "lmnh_ec2_key" {
  key_name   = "lmnh-ec2-key"
  public_key = file(var.public_key_path)
}

resource "aws_security_group" "ec2_sg" {
  name        = "c23-yusuf-ec2-security-group"
  description = "Allow SSH access to EC2 from my IP"

  ingress {
    description = "SSH from my local machine"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "c23-yusuf-ec2-security-group"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"]

  filter {
    name = "name"
    values = [
      "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
    ]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "etl_server" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  key_name                    = aws_key_pair.lmnh_ec2_key.key_name
  vpc_security_group_ids      = [aws_security_group.ec2_sg.id]
  associate_public_ip_address = true

  tags = {
    Name = "c23-yusuf-lmn3h-etl-server"
  }
}