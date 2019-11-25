#!/bin/bash


image_id=ami-01d859635d7625db5
count=1
instance_type=c5n.18xlarge
key_name=patrick-ioos-cloud-sandbox
sg_ids="sg-006041073bfa7b072,sg-0a48755f7b926b051,sg-04a6bcecaec589f64"
subnet_id=subnet-09dae53e246bd68e4
placement_group=IOOS-cloud-sandbox-cluster-placement-group

# vpc_id=vpc-039661fdd9f2a896e

# With EFA network adaptor

# aws ec2 run-instances --image-id ami_id --count 1 --instance-type c5n.18xlarge --key-name my_key_pair \
# --network-interfaces DeviceIndex=0,InterfaceType=efa,Groups=sg_id,SubnetId=subnet_id
# --placement "GroupName=$placement_group"

# --tags Key=Name,Value=MyInstance -- obsolete
#  --tag-specifications 'ResourceType=instance,Tags=[{Key=webserver,Value=production}]' 'ResourceType=volume,Tags=[{Key=cost-center,Value=cc123}]'
    # --key-name $key_name --security-group-ids $sg_ids --subnet-id $subnet_id \

aws ec2 run-instances --region us-east-1 --image-id $image_id --count $count --instance-type $instance_type \
    --key-name $key_name  --network-interfaces "DeviceIndex=0,InterfaceType=efa,Groups=$sg_ids,SubnetId=$subnet_id" \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=IOOS-cloud-sandbox-clitest}]' \
    --placement "GroupName=$placement_group"

