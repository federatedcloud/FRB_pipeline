# Purpose

Deploy small prototype AWS footprint for parallel workloads

See aws/README.md for description of prototype phase version alpaca

By default creates an S3 bucket, a server ami for later VMs, a small master VM,
and two small worker VMs

# Implementation Status

Master node and network pieces creation tested with public ssh access confirmed

Mostly unimplemented WIP

# Technologies
Terraform, Ansible, Docker, Amazon Web Services EC2 and S3
The included Terraform and Ansible scripts allow for creation of above listed
AWS resources.

# Requirements

## Dependencies and Configurations

To get started, the terraform package (version 0.11) and ansible package
(2.7.6+) will need to be installed locally.

https://learn.hashicorp.com/terraform/getting-started/install.html

Optional guides for specific terraform version installation

https://github.com/tfutils/tfenv or https://stackoverflow.com/questions/56283424/upgrade-terraform-to-specific-version

https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#selecting-an-ansible-version-to-install

To get started with aws, the pip3 package and aws-cli will need to be installed
locally. pip3 is needed to install aws-cli as per
[https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
This will create the credentials located in $HOME/.aws/ which will be used by
terraform. After installed aws-cli, configure it by typing the command. 

```
aws configure
```

Alternatively, you can create the aws credentials directory manually in the
location named previously. The credential file is named credentials and its
contents are described below. 

```
[default]
aws_access_key_id = YOURACCESSKEYHERE
aws_secret_access_key = youraccesskeyhere
```

An easy way to activate AWS API credentials in your current shell environment for Terraform to automatically detect them without persisting them to disk is to export them as:

```
export ACCESS_KEY=...
export SECRET_KEY=...
```

All the parameters for setting up the instances are provided in the variables.tf
file. It is important to note that the private and public keys will be used to
access all created virtual machine instances. Many tools exist for browsing S3
including the AWS console navigating to service S3.

# Usage

Setup requirements above

Create a cluster ssh key for the master to issue commands to workers, it will
be registered as an AWS EC2 Key Pair.

todo : Configure additional cluster user ssh keys

git clone this repo

cd checkout_dir

cd aws/tf/alpaca-proto 

copy variables.tf.example to variables.tf and modify file to set the s3 bucket name, instance size and type,
and other resource provisioning details

copy ssh_configfile.tmpl.example to ssh_configfile.tmpl based on the intended placement path of the cluster access ssh key on the new master node

todo : if using an existing bucket, place access credentials to reuse

tf init

tf plan

tf apply

Confirm successful resource creation

# What It Does

## Provisioning Creates and Tests Server Instances
The following steps detail how the instances are created and configured. These
steps are applies automatically when calling the terraform scripts and do not
need to be repeated. 
1. Terraform first creates a new centos7 instance in your AWS account.
2. Ansible installs the following packages in the centos7 instance (shell equivalent).
  ```
    sudo yum install yum-utils \ git \ device-mapper-persistent-data \ lvm2
    sudo yum-config-manager \ --add-repo \ https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install docker-ce
    sudo systemctl start docker
    sudo groupadd docker
    sudo usermod -aG docker $USER
    sudo yum install epel-release \ python-pip \ docker-compose
  ```
3. todo : FRB docker image pull , pull this repo so master has spot manager scripts
4. Ansible sleeps for 300 seconds to let the image build then stops all containers
5. Terraform then creates a snapshot of the instance. Terraform creates a disk
from the snapshot. Finally terraform creates a new image from the disk. N
instances will be created from this image (name alpaca0 to alpacaN).
6. Ansible exports the host file list of worker IP addresses to the master node
7. Run ping and ssh tests
  ```
    ping -c 5 -t 10 $ip_addresses
    ssh -o ConnectTimeout=10 -i ssh_private_key $ip_addresses hostname
  ```
8. todo : s3 bucket creation

# Credits and References

Derived from https://github.com/federatedcloud/ansible-terraform
