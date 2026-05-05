provider "aws" {
  region = "ap-southeast-3"
}

# VPC Provision - Use existing VPC
data "aws_vpc" "selected" {
  tags = {
    Name = "learner-vpc"
  }
}

# Subnet Provision
resource "aws_subnet" "public_subnet" {
  vpc_id     = data.aws_vpc.selected.id
  cidr_block = "172.31.201.0/28"

  tags = {
    Name = "mint-ai-public"
  }
}

# Security Group Provision
resource "aws_security_group" "public_security_group" {
  name        = "mint-ai-public-security-group"
  description = "Security group for mint-ai public ec2 instance"
  vpc_id      = data.aws_vpc.selected.id

  tags = {
    Name = "mint-ai-public-security-group"
  }
}

resource "aws_vpc_security_group_ingress_rule" "allow_tls_ipv4" {
  security_group_id = aws_security_group.public_security_group.id
  cidr_ipv4         = data.aws_vpc.selected.cidr_block
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

data "http" "my_ip" {
  url = "https://checkip.amazonaws.com"
}

resource "aws_vpc_security_group_ingress_rule" "allow_ssh_ipv4" {
  security_group_id = aws_security_group.public_security_group.id
  cidr_ipv4         = "${chomp(data.http.my_ip.response_body)}/32"
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}

resource "aws_vpc_security_group_ingress_rule" "allow_http_ipv4" {
  security_group_id = aws_security_group.public_security_group.id
  cidr_ipv4         = data.aws_vpc.selected.cidr_block
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.public_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# Secrets Manager Provision

# Policy Provision

# IAM Role Provision

# EC2 Provision
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"]
}

resource "aws_key_pair" "deployer" {
  key_name   = "mint-ai-deployer-key"
  public_key = file("~/.ssh/mint_ai.pub")
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  key_name      = aws_key_pair.deployer.key_name

  tags = {
    Name = "mint-ai-public"
  }
}

# Elastic IP Provision
resource "aws_eip" "public_ec2_eip" {
  domain = "vpc"

  instance = aws_instance.app_server.id

  tags = {
    Name = "mint-ai-public-ec2-eip"
  }
}

# Route 53 Provision
data "aws_route53_zone" "selected" {
  name = "devopsinstitute.id"
}

resource "aws_route53_record" "mintai" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = "mintai.${data.aws_route53_zone.selected.name}"
  type    = "A"
  ttl     = "300"
  records = [aws_eip.public_ec2_eip.public_ip]
}
