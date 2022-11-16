# import os
# import sys
# import pandas as pd
# import pyterrier as pt

# pt.init()

# euid = os.geteuid()
# if euid != 0:
#     print ("Script not started as root. Running sudo..")
#     args = ['sudo', sys.executable] + sys.argv + [os.environ]
#     # the next line replaces the currently-running process with the sudo
#     os.execlpe('sudo', *args)

# print ('Running. Your euid is', euid)
# print(sys.executable)

# inputQuery = sys.argv[1]

# def testTrial (inputQuery):
#   query = bonaFides(inputQuery)
  
#   eng_data = pd.read_csv('eng.csv')
#   # print('end here 2')
#   output = eng_data.to_json()
#   print(output, query)
#   sys.stdout.flush()
# testTrial(inputQuery)

import sys
import json
import random
import numpy as np
import pandas as pd

# print("I am the result:"+ str(int(1) + int(2)))
# sys.stdout.flush()


eng_data = pd.read_csv('eng.csv')
print(eng_data.to_json())
sys.stdout.flush()
