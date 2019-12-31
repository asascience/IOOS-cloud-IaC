#!/usr/bin/python3

import romsUtil as util

template="../adnoc/ocean.in.template"
outfile="ocean.in"

# Just a dictionary
# Could also read this in from a json file 
settings = {
  "__NTILEI__": 2,
  "__NTILEJ__": 2,
  "__NTIMES__": 60,
  "__TIME_REF__": "20191212.00"
}

util.sedoceanin ( template, outfile, settings )



nodeCount=4
coresPN=36

util.getTiling( nodeCount, coresPN )
