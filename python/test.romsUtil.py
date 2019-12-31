#!/usr/bin/python3

import romsUtil as util

template="../adnoc/ocean.in.template"
outfile="ocean.in"


nodeCount=4
coresPN=36

tiles = util.getTiling( nodeCount, coresPN )

# Just a dictionary
# Could also read this in from a json file 
settings = {
  "__NTILEI__": tiles["NtileI"],
  "__NTILEJ__": tiles["NtileJ"],
  "__NTIMES__": 60,
  "__TIME_REF__": "20191212.00"
}

util.sedoceanin ( template, outfile, settings )

