provider "aws" {
  profile    = "default"
  region     = "${var.region}"
}
data "aws_ami" "centos_7" {
  most_recent = true
  filter {
    name = "name"
    values = ["CentOS Linux 7 x86_64*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["aws-marketplace"]
}
data "aws_vpc" "S3Bucket" {
  id = "${var.vpc_id}" 
}
data "aws_internet_gateway" "S3Bucket" {
  internet_gateway_id = "${var.VPC_GATEWAY}"
}
#############################################################################
# Currently the IAM role pulls an existing role using data. Ideally this is 
# changed to create an iam role in the future 
#############################################################################
data "aws_iam_role" "FRB" {
  name = "${var.IAM_ROLE}"
}
resource "aws_iam_instance_profile" "FRB_profile" {
  name = "FRB_profile"
  role = "${data.aws_iam_role.FRB.name}"
}
#resource "aws_ebs_volume" "FRB" {
#  availability_zone = "${var.region}"
#  size = "${var.size}"
#  type = "${var.volume_type}"
#}
resource "aws_key_pair" "FRBkey" {
  key_name = "FRB-key"
  public_key = "${replace(file(var.PUBLIC_KEY), "\n", "")}"
}
data "aws_subnet" "S3Bucket" {
  id = "${var.subnet_id}"
}
data "aws_route_table" "S3Bucket" {
  route_table_id = "${var.route_table_id}"
}
#resource "aws_subnet" "FRBnetwork" {
#  cidr_block = "10.0.0.0/24"
#  vpc_id = "${data.aws_vpc.S3Bucket.id}"
#  availability_zone = "us-east-1a"
#}
#resource "aws_route_table" "FRBnetwork" {
#  vpc_id = "${data.aws_vpc.S3Bucket.id}"
#
#  route {
#    cidr_block = "0.0.0.0/0"
#    gateway_id = "${data.aws_internet_gateway.S3Bucket.id}"
#  }
#}
resource "aws_route_table_association" "subnet-association" {
  subnet_id = "${data.aws_subnet.S3Bucket.id}"
  route_table_id = "${data.aws_route_table.S3Bucket.id}"
}
resource "aws_security_group" "ingress-cornell"   {
  name = "allow-cornell-ssh"
  vpc_id = "${data.aws_vpc.S3Bucket.id}"
  ingress {
    cidr_blocks = ["128.84.0.0/16"]
    from_port = 22
    to_port = 22
    protocol = "tcp"
    description = "cornell access"
  }
  ingress {
    cidr_blocks = ["10.0.0.0/16"]
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    description = "internal access"
  }
  ingress {
    cidr_blocks = ["10.0.0.0/16"]
    from_port = -1
    to_port = -1
    protocol = "icmp"
    description = "ping"
  }
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    description = "access anywhere from instance"
  }
}
resource "aws_eip" "FRBnetwork" {
  instance = "${aws_instance.master.id}"
  vpc = true
}
resource "aws_instance" "master" {
  instance_type = "${var.machine_type}"
  ami           = "${data.aws_ami.centos_7.id}"
  key_name = "${aws_key_pair.FRBkey.key_name}"
  security_groups = ["${aws_security_group.ingress-cornell.id}"]
  subnet_id = "${data.aws_subnet.S3Bucket.id}"
  associate_public_ip_address = true
  iam_instance_profile = "${aws_iam_instance_profile.FRB_profile.name}"
  root_block_device {
    volume_type = "${var.volume_type}"
    volume_size = "${var.size}"
    delete_on_termination = "true"
  }
  tags = {
    Resource = "EC2_test_master"
  }
  provisioner "remote-exec" {
    # ensures that a connection is set up
        inline = ["echo"]
    connection {
     host = "${self.public_ip}"
     type = "ssh"
     user = "${var.USER}"
     private_key = "${file("${var.PRIVATE_KEY}")}"
    }
  }
  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i 'centos@${aws_instance.master.public_ip},' --private-key '${var.PRIVATE_KEY}' ../ansible/Master_Node_Setup.yaml"
  }
}

#resource "aws_ami_from_instance" "worker_cluster" {
#  name = "worker_cluster"
#  source_intance_id = "${aws_instance.master.id}"
#}
#resource "aws_instance" "worker_cluster" { 
#  count = "${var.worker_count}"
#  instance_type = "${var.worker_machine}"
#}


