# resource "aws_vpc" "api_vpc" {
#   cidr_block = "10.0.0.0/16"
#   instance_tenancy = "default"
#   enable_dns_hostnames = true
#   enable_dns_support = true
#   tags = {
#       Name = "crypto_wallet_vpc"
#   }
# }

# resource "aws_egress_only_internet_gateway" "egress_internet_gh" {
#   vpc_id = aws_vpc.api_vpc.id
#   tags = {
#     Name = "egress_only_internet_gw"
#   }
# }

# resource "aws_internet_gateway" "api_internet_gw" {
#   vpc_id = aws_vpc.api_vpc.id
#   tags = {
#     Name = "api-internet-gateway"
#   }
# }

# resource "aws_eip" "ip" {
#   vpc      = true
#   tags = {
#     Name = "elastic_ip"
#   }
# }

# resource "aws_nat_gateway" "api_nat_gw" {
#   allocation_id = aws_eip.ip.id
#   subnet_id     = aws_subnet.api_public_subnet.id
#   tags = {
#     Name = "nat-gateway"
#   }
# }

# resource "aws_subnet" "api_private_subnet" {
#   vpc_id     = aws_vpc.api_vpc.id
#   cidr_block = "10.0.128.0/20"
#   map_public_ip_on_launch = true
#   availability_zone ="us-east-1a"
#   tags = {
#     Name = "api_private_subnet-1a"
#   }
# }

# resource "aws_subnet" "api_public_subnet" {
#   vpc_id     = aws_vpc.api_vpc.id
#   cidr_block = "10.0.0.0/20"
#   map_public_ip_on_launch = true
#   availability_zone ="us-east-1a"
#   tags = {
#     Name = "api_public_subnet-1a"
#   }
# }

# resource "aws_route_table" "api_rtb_private" {
#   vpc_id = aws_vpc.api_vpc.id
#   route {
#     cidr_block = "0.0.0.0/0"
#     gateway_id = aws_nat_gateway.api_nat_gw.id
#   }
#   # route {
#   #   cidr_block = "10.0.0.0/16"
#   #   gateway_id = "local"
#   # }
#   tags = {
#     Name = "api_rtb_private"
#   }
# }

# resource "aws_route_table_association" "link_rtb_private" {
#   subnet_id      = aws_subnet.api_private_subnet.id
#   route_table_id = aws_route_table.api_rtb_private.id
# }

# resource "aws_route_table" "api_rtb_public" {
#   vpc_id = aws_vpc.api_vpc.id
#   route {
#     ipv6_cidr_block = "::/0"
#     gateway_id = aws_egress_only_internet_gateway.egress_internet_gh.id
#   }
#   route {
#     cidr_block = "0.0.0.0/0"
#     gateway_id = aws_internet_gateway.api_internet_gw.id
#   }
#   # route {
#   #   cidr_block = "10.0.0.0/16"
#   #   gateway_id = "local"
#   # }
#   tags = {
#     Name = "api_rtb_public"
#   }
# }

# resource "aws_route_table_association" "link_rtb_public" {
#   subnet_id      = aws_subnet.api_public_subnet.id
#   route_table_id = aws_route_table.api_rtb_public.id
# }

# resource "aws_security_group" "lambda_internet_access_sec_group" {
#   name        = "lambda_vpc_sec_group"
#   description = "Allow lambda access to the internet"
#   vpc_id      = aws_vpc.api_vpc.id
#   ingress {
#     description = "HTTP"
#     from_port   = 0
#     to_port     = 0
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   tags = {
#     Name = "lambda_vpc_security_group"
#   }
# }
