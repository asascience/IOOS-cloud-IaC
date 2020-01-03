import sys
import shutil
import re
import math



def sedoceanin ( template, outfile, settings ) :
 
  with open(template, 'r') as infile :
    lines = infile.readlines()

  with open(outfile, 'w') as outfile :
    for line in lines:
      newline = line

      for key, value in settings.items() :
        newline = re.sub(key, str(value), newline)        

      outfile.write(re.sub(key, value, newline))

  return




# TODO: just need totalCores
#def getTiling( nodeCount, coresPN ) :
def getTiling( totalCores ) :
  ''' Algorithm

    prefer a square or closest to it

    if sqrt of total is an integer then use it for I and J
    if not find factorization closest to square

    examples:

      assert must be even, there are no even primes > 2
      36 = sqrt(36) = ceil(6)  36 mod 6 = 0 - DONE

      32 = sqrt(32) = 5.65 32 mod 6 != 0
                              mod 5 != 0
                              mod 4 == 0
                            32 / 4 = 8 DONE NtileI=8, NtileJ=4
  '''

  NtileI=1
  NtileJ=1

  #totalCores = coresPN * nodeCount
  print('In getTiling: totalCores = ', str(totalCores))

  if ((totalCores != 1) and (totalCores % 2 != 0)):
    raise Exception("Total cores must be even")

  square = math.sqrt(totalCores) 
  ceil = math.ceil(square)

  done="false"

  print("totalCores : ", totalCores)

  while (done == "false" ) :
    if ((totalCores % ceil) == 0) :
      NtileJ = ceil
      NtileI = int(totalCores / NtileJ)
      done="true"
    else:
      ceil -= 1

  print("NtileI : ", NtileI, " NtileJ ", NtileJ)

  return { "NtileI": NtileI, "NtileJ": NtileJ }
      
