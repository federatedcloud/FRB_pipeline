# Purpose 

Run embarrassingly parallel data chunk processing on many AWS VMs

# Status

Experimental Untested WIP

# Target

v.alpaca - see private implementation documentation

create small prototype footprint AWS resources - s3 bucket, small master EC2 node, 2 small worker EC2 nodes

prototype generating and triggering code for worker jobs on parallel data chunks to run on AWS worker nodes

those prototype codes will run on the master, and jobs triggered on workers will push to s3 also notifying master

# Requirements

Terraform deployment context

Ansible installed

Cloud provider credentials ex AWS api keys through an IAM role with EC2 and S3 access

todo : spot code docker image available on Docker Hub, Amazon ECR or similar

todo : for faster deployment, bake docker image into an ami with software pre-installed and code versions noted

# Usage

use or create a Terraform deployment context https://learn.hashicorp.com/terraform/getting-started/install.html

example OS Centos 7 Terraform Terraform v0.11.14 Ansible ansible 2.8.4

git checkout this repository commit

cd checkout_dir

cd aws/tf

configure variables for desired region, instance size, etc in variables.tf

todo : configure variables for s3 bucket, spot count

configure cloud provider access through environment variables that terraform will automatically detect as per https://www.terraform.io/docs/providers/aws/index.html

tf init

now create the master that will process data chunks and spots that will perform lots of custom work on those chunks

tf plan

tf apply

confirm that bucket, master and worker resources have been created

## more todos planned


use ansible to install ansible on master

provide spot ip list as short term worker discovery list

use ansible to setup worker nodes with docker engine install etc

generate list of jobs that are worker configurations / scripts of data to process

configuration will include data access keys, so master node needs the data access keys or how to retrieve them

on master, either start loop where ansible triggers jobs on spots or manually execute ansible async to spawn work processes on workers using ssh

the loop over ansible triggers continues until no idle worker is found

use ansible to start spot manager on master

spot manager will retain expected s3 data output paths for workers, and expected time to check in

spot manager on master will listen for reports from spots of work completion

provide spot discovery information to master (as spots may die the master may need to rediscover)

when spots are interrupted, master would need terraform privileges to spawn new spots and resume loop handing out work

consider ansible to install and configure terraform on master as a new automated IAM role

factor spot creation into a separate folder and thus apply phase than master creation

after some time, when no jobs remain to be executed, consider giving the master the ability to terraform cleanup only the spots




