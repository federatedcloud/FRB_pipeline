provider "aws" {
  profile    = "default"
  region     = "us-east-1"
}
# finds centos_7 AWS ami
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
resource "aws_key_pair" "frb-cluster-alpaca" {
  key_name = "frb-cluster-alpaca"
  public_key = "${replace(file(var.PUBLIC_KEY), "\n", "")}"
}
output "public-key-debug" {
  value = "${replace(file(var.PUBLIC_KEY), "\n", "")}"
  description = "the public key variable content"
}
output "aws-key-pair-debug" {
  value = "${aws_key_pair.frb-cluster-alpaca.key_name}"
  description = "aws key pair name"
}
resource "aws_vpc" "frb-cluster-alpaca" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
  tags {
    Name = "frb-cluster-alpaca-vpc"
  }
}
resource "aws_internet_gateway" "frb-cluster-alpaca" {
  vpc_id = "${aws_vpc.frb-cluster-alpaca.id}"
}
resource "aws_subnet" "frb-cluster-alpaca" {
  cidr_block = "10.0.0.0/24"
  vpc_id = "${aws_vpc.frb-cluster-alpaca.id}"
  availability_zone = "us-east-1a"
}
resource "aws_route_table" "frb-cluster-alpaca" {
  vpc_id = "${aws_vpc.frb-cluster-alpaca.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.frb-cluster-alpaca.id}"
  }
}
resource "aws_route_table_association" "subnet-association" {
  subnet_id = "${aws_subnet.frb-cluster-alpaca.id}"
  route_table_id = "${aws_route_table.frb-cluster-alpaca.id}"
}
resource "aws_security_group" "ingress-cornell"   {
  name = "allow-cornell-ssh"
  vpc_id = "${aws_vpc.frb-cluster-alpaca.id}"
  ingress {
    cidr_blocks = ["128.84.0.0/16"]
    from_port = 22
    to_port = 22
    protocol = "tcp"
    description = "cornell inbound ssh access" 
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
    description = "outbound send anywhere from instance"
  }
}
resource "aws_eip" "frb-cluster-alpaca" {
  instance = "${aws_instance.base_vm.id}"
  vpc = true
}
resource "aws_instance" "base_vm" {
  instance_type = "t2.micro"
  ami           = "${data.aws_ami.centos_7.id}" 
  key_name = "${aws_key_pair.frb-cluster-alpaca.key_name}"
  security_groups = ["${aws_security_group.ingress-cornell.id}"]
  subnet_id = "${aws_subnet.frb-cluster-alpaca.id}"
  associate_public_ip_address = true
  provisioner "remote-exec" {
    # ensures that a connection is set up
        inline = ["echo"]
    connection {
     type = "ssh"
     user = "${var.USER}"
     private_key = "${file("${var.PRIVATE_KEY}")}"
    }
  }
  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i '${var.USER}@${aws_instance.base_vm.public_ip},' --private-key '${var.PRIVATE_KEY}' ../ansible/Centos7_FRB_AMI_setup_alpaca.yml --extra-vars 'user='${var.USER}' ' "
  }
}
resource "aws_ami_from_instance" "frb-cluster-alpaca" {
  name = "cac-frb-cluster-prototype-image-alpaca" 
  source_instance_id = "${aws_instance.base_vm.id}"
}
resource "aws_instance" "frb-cluster-alpaca-master" {
  count = "${var.master_count}"
  instance_type = "${var.master_machine_type}"
  ami = "${aws_ami_from_instance.frb-cluster-alpaca.id}"
  key_name = "${aws_key_pair.frb-cluster-alpaca.key_name}"
  security_groups = ["${aws_security_group.ingress-cornell.id}"]
  subnet_id = "${aws_subnet.frb-cluster-alpaca.id}"
  associate_public_ip_address = true
  provisioner "remote-exec" {
    # ensures that a connection is set up
        inline = ["echo"]
    connection {
     type = "ssh"
     user = "${var.USER}"
     private_key = "${file("${var.PRIVATE_KEY}")}"
    }
  }
}
# todo worker nodes
#data "template_file" "ssh_configfile" {
#  template = "${file("ssh_configfile.tmpl")}"
#  vars {
#    ip_addrs = "${join(",",aws_instance.frb-cluster-alpaca-worker.*.private_ip)}"
#    port = "${var.SSH_PORT}"
#    user = "${var.USER}"
#  }
#}
resource "local_file" "inventory" {
  content = "[external_ips]\n${join("\n",aws_instance.frb-cluster-alpaca-master.*.public_ip)}"
  filename = "${path.module}/../ansible/frb-cluster-alpaca-inventory"
}
# todo workers as separate group in inventory
#resource "local_file" "ssh_config" {
#  content = "${data.template_file.ssh_configfile.rendered}"
#  filename = "../master_files/ssh_configfile"
#}
#resource "null_resource" "master-setup" {
#  triggers = {
#    "after" = "${aws_instance.frb-cluster-alpaca-master.id}"
#  }
#  connection {
#    host = "${aws_instance.frb-cluster-alpaca-master.*.public_ip}"
#  }
#  provisioner "local-exec" {
#    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i '${path.module}/../ansible/frb-cluster-alpaca-inventory' -u '${var.USER}' --private-key '${var.PRIVATE_KEY}' --extra-vars 'user='${var.USER}'' ../ansible/FRB_master_setup_alpaca.yml"
#  }
#}
output "eip_private" {
  value = "${aws_eip.frb-cluster-alpaca.private_ip}"
}
output "eip_public" {
  value = "${aws_eip.frb-cluster-alpaca.public_ip}"
}
output "debug_private" {
  value = "${aws_instance.base_vm.private_ip}" 
}
output "eip_instance" {
  value = "${aws_eip.frb-cluster-alpaca.instance}"
}
output "master_private_ip" {
  value = "${aws_instance.frb-cluster-alpaca-master.*.private_ip}"
}
output "master_public_ip" {
  value = "${aws_instance.frb-cluster-alpaca-master.*.public_ip}"
}
