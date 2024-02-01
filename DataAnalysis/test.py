#                # 
# INITIAL SET-UP #
#                # 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#              # 
# DATA ANALYIS # 
#              # 

# X-axis of earnings visualization
DayLimit = 365
DaysAxis = []

for x in range(1, DayLimit + 1):
    DaysAxis.append(x)
    x += 1

# OutputFilePath = 'DaysAxis.JSON'
# with open(OutputFilePath, 'w') as JSONFile:
#     json.dump(DaysAxis, JSONFile)
    


print(DaysAxis)