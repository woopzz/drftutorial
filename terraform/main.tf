provider "aws" {
    profile = "default"
    region = "eu-central-1"
}

resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    enable_dns_support = true

    tags = {
        Name = "drftutorial-vpc"
    }
}

resource "aws_subnet" "public_eu_central_1a" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.0.1.0/24"
    availability_zone = "eu-central-1a"

    tags = {
        Name = "drftutorial-subnet-public-eu-central-1a"
    }
}

resource "aws_subnet" "private_eu_central_1a" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.0.2.0/24"
    availability_zone = "eu-central-1a"

    tags = {
        Name = "drftutorial-subnet-private-eu-central-1a"
    }
}

resource "aws_subnet" "private_eu_central_1b" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.0.3.0/24"
    availability_zone = "eu-central-1b"

    tags = {
        Name = "drftutorial-subnet-private-eu-central-1b"
    }
}

resource "aws_internet_gateway" "main" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "drftutorial-igw"
    }
}

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.main.id
    }

    tags = {
        Name = "drftutorial-rtb-public"
    }
}

resource "aws_route_table_association" "public_rtb_asso" {
    subnet_id = aws_subnet.public_eu_central_1a.id
    route_table_id = aws_route_table.public.id
}

resource "aws_key_pair" "common" {
    key_name = "drftutorial_ssh_key"
    public_key = file("./drftutorial.pub")
}

resource "aws_security_group" "allow_ssh" {
    name = "allow_ssh"
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "allow_ssh"
    }
}

resource "aws_vpc_security_group_ingress_rule" "allow_ssh" {
    security_group_id = aws_security_group.allow_ssh.id
    cidr_ipv4 = "0.0.0.0/0"
    ip_protocol = "tcp"
    from_port = 22
    to_port = 22
}

resource "aws_vpc_security_group_egress_rule" "allow_all" {
    security_group_id = aws_security_group.allow_ssh.id
    cidr_ipv4 = "0.0.0.0/0"
    ip_protocol = "-1"
}

resource "aws_security_group" "expose_tcp_8000" {
    name = "expose_tcp_8000"
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "expose_tcp_8000"
    }
}

resource "aws_vpc_security_group_ingress_rule" "expose_tcp_8000" {
    security_group_id = aws_security_group.expose_tcp_8000.id
    cidr_ipv4 = "0.0.0.0/0"
    ip_protocol = "tcp"
    from_port = 8000
    to_port = 8000
}

resource "aws_security_group" "ingress_tcp_9200" {
    name = "ingress_tcp_9200"
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "ingress_tcp_9200"
    }
}

resource "aws_vpc_security_group_ingress_rule" "ingress_tcp_9200" {
    security_group_id = aws_security_group.ingress_tcp_9200.id
    referenced_security_group_id = aws_security_group.egress_tcp_9200.id

    ip_protocol = "tcp"
    from_port = 9200
    to_port = 9200
}

resource "aws_security_group" "egress_tcp_9200" {
    name = "egress_tcp_9200"
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "egress_tcp_9200"
    }
}

resource "aws_vpc_security_group_egress_rule" "egress_tcp_9200" {
    security_group_id = aws_security_group.egress_tcp_9200.id
    referenced_security_group_id = aws_security_group.ingress_tcp_9200.id

    ip_protocol = "tcp"
    from_port = 9200
    to_port = 9200
}

resource "aws_security_group" "ec2_rds" {
    name = "ec2_rds"
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "ec2_rds"
    }
}

resource "aws_vpc_security_group_egress_rule" "ec2_rds" {
    security_group_id = aws_security_group.ec2_rds.id
    referenced_security_group_id = aws_security_group.rds_ec2.id

    ip_protocol = "tcp"
    from_port = 5432
    to_port = 5432
}

resource "aws_security_group" "rds_ec2" {
    name = "rds_ec2"
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "rds_ec2"
    }
}

resource "aws_vpc_security_group_ingress_rule" "rds_ec2" {
    security_group_id = aws_security_group.rds_ec2.id
    referenced_security_group_id = aws_security_group.ec2_rds.id

    ip_protocol = "tcp"
    from_port = 5432
    to_port = 5432
}

resource "aws_instance" "main" {
    ami = "ami-04f1b917806393faa"
    instance_type = "t2.micro"
    key_name = aws_key_pair.common.key_name

    subnet_id = aws_subnet.public_eu_central_1a.id
    vpc_security_group_ids = [
        aws_security_group.allow_ssh.id,
        aws_security_group.expose_tcp_8000.id,
        aws_security_group.egress_tcp_9200.id,
        aws_security_group.ec2_rds.id
    ]
    associate_public_ip_address = true

    tags = {
        Name = "drftutorial_main"
    }
}

resource "aws_instance" "elasticsearch" {
    ami = "ami-04f1b917806393faa"
    instance_type = "t2.micro"
    key_name = aws_key_pair.common.key_name

    subnet_id = aws_subnet.public_eu_central_1a.id
    vpc_security_group_ids = [aws_security_group.allow_ssh.id, aws_security_group.ingress_tcp_9200.id]
    associate_public_ip_address = true

    tags = {
        Name = "drftutorial_elasticsearch"
    }
}

resource "aws_db_subnet_group" "postgres_subnet_group" {
    name = "postgres_subnet_group"
    subnet_ids = [aws_subnet.private_eu_central_1a.id, aws_subnet.private_eu_central_1b.id]
}

resource "aws_db_instance" "postgres" {
    identifier = "drftutorial-postgres"
    engine = "postgres"
    engine_version = "16.3"
    instance_class = "db.t3.micro"
    allocated_storage = 5
    skip_final_snapshot = true
    apply_immediately = true
    publicly_accessible = false

    username = var.postgres_user
    password = var.postgres_password

    db_subnet_group_name = aws_db_subnet_group.postgres_subnet_group.name
    vpc_security_group_ids = [aws_security_group.rds_ec2.id]
}
