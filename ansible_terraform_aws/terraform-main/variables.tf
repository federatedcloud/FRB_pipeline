variable "region" {
  description = "The AWS region to create instance in."
  default = "us-east-1"
}
variable "machine_type" {
  description = "type of instance to fire up"
  default = "t3a.xlarge"
}
variable "zone" {
  description = "zone you wish to create the instance in"
  default = "us-west1-a"
}
variable "PRIVATE_KEY" {
  description = "location of private key"
  default = "~/.ssh/id_rsa"
}
variable "PUBLIC_KEY" {
  description = "location of public key"
  default = "~/.ssh/id_rsa.pub"
}
variable "USER" {
  description = "user to set up instance"
  default = "centos"
}
variable "IAM_ROLE" {
  description = "the iam role to give to an instance" 
  default = "FRB-S3-Bucket-Access"
}
variable "size" {
  description = "the size of the volume in GB" 
  default = "600" 
}
variable "volume_type" {
  description = "the type of volume"
  default = "gp2"
}
variable "worker_count" {
  description = "the number of worker"
  default = "5"
}
variable "worker_machine" {
  description = "the worker machine" 
  default = "t2.micro"
}
variable "vpc_id" {
  description = "the vpc id" 
  default = "id"
}
variable "VPC_GATEWAY" {
  description = "the gateway to the vpc"
  default = "id"
}
variable "route_table_id" {
  description = "route table id"
  default = "id"
}
variable "subnet_id" {
  description = "subnet id"
  default = "id"
}
