#                # 
# INITIAL SET-UP #
#                # 

import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#              # 
# DATA ANALYIS # 
#              # 

# Amount of days model is running for
TimeScope = 20

#         #
# StakeUS # 
#         # 

StakeEarnings = []
StakeBaseEarnings = 1 
StakeAverageRTP = 98
StakeDailyEarnings = StakeBaseEarnings * (StakeAverageRTP/100)

for x in range(1, TimeScope):
    StakeEarnings.append(StakeDailyEarnings)
    StakeDailyEarnings += StakeBaseEarnings * (StakeAverageRTP/100)

#              # 
# ChumbaCasino # 
#              # 

ChumbaEarnings = [] 
ChumbaBaseEarnings = 1
ChumbaAverageRTP = 98.78
ChumbaDailyEarnings = ChumbaBaseEarnings * (ChumbaAverageRTP/100)

for x in range(1, TimeScope):
    ChumbaEarnings.append(ChumbaDailyEarnings)
    ChumbaDailyEarnings += (ChumbaBaseEarnings * (ChumbaAverageRTP/100))