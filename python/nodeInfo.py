#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
#import cluster

def getPPN(instance_type) :
 
  awsTypes = { 'c5.large':1, 'c5.xlarge':2, 'c5.2xlarge':4, 'c5.4xlarge':8, \
                'c5.9xlarge':18, 'c5.18xlarge':36, 'c5.24xlarge':48, 'c5n.metal':36, \
                'c5n.large':1, 'c5n.xlarge':2, 'c5n.2xlarge':4, 'c5n.4xlarge':8, 'c5n.9xlarge':18, \
                'c5n.18xlarge':36, 'c5n.24xlarge':48, 'c5n.metal':36}

  # Add try exception handling
  ppn = awsTypes[instance_type]
  return ppn

