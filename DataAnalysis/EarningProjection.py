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

# FortuneCoins
    
FortuneEarnings = [] 
FortuneBaseEarnings = 1
FortuneAverageRTP = 95.33
FortuneDailyEarnings = FortuneBaseEarnings * (FortuneAverageRTP/100)

for x in range(1, TimeScope):
    FortuneEarnings.append(FortuneDailyEarnings)
    FortuneDailyEarnings += (FortuneBaseEarnings * (FortuneAverageRTP/100))

print(FortuneEarnings)

# # McLuck

# McLuckEarnings = [0.3, 0.3, 0.3, 0.5, 1, 1, 1]

# McLuckThereafterAvgEarnings = 7 
# McLuckAveragedRTP = 96.57

# McLuckThereafterEarnings = McLuckThereafterAvgEarnings * (McLuckAveragedRTP/100)

# # # get average return to player for initial earnings in a loop
# for x in range(1, 8):
#     McLuckEarnings.append(McLuckInitialEarnings)
#     StakeInitialEarnings += StakeAverageWeeklyEarnings * (StakeAveragedRTP/100)

# for x in range(1,DayLimit + 1): 
#     for y in range(8, DayLimit + 1):
#         StakeEarnings.append(StakeEarnings[y] + StakeThereafterEarnings)
#         StakeThereafterEarnings += McLuckThereafterAvgEarnings * (McLuckAveragedRTP/100)

# # ModoUS
# ModoFirstWeekAvgEarnings = 4.4
# ModoThereafterAvgEarnings = 7 
# ModoAveragedRTP = 95.93

# ModoFirstWeekEarnings = ModoFirstWeekAvgEarnings * (ModoAveragedRTP/100)
# ModoThereafterEarnings = ModoThereafterAvgEarnings * (ModoAveragedRTP/100)

# #     # 
# # CSV # 
# #     # 

# # Add EarningsData.csv in the same directory as visualization and calculations 
# CSVPath = os.path.join('DataAnalysis' ,'EarningsData.csv')

# # Adds X and Y axis to EarningsData.csv in order
# with open(CSVPath, 'a', newline='') as CSVFile:
#     CSVWrite = csv.writer(CSVFile)
#     # CSVWrite.writerow(['DaysAxis'])  # Write header
#     # CSVWrite.writerow(DaysAxis) 
#     if os.stat(CSVPath).st_size == 0:
#         CSVWrite.writerow(['DaysAxis', 'StakeEarnings', 'ModoEarnings', 'ChumbaEarnings'])
    
#     # Write data
#     CSVWrite.writerow(DaysAxis + StakeEarnings + ChumbaEarnings)

# #               # 
# # VISUALIZATION # 
# #               # 
    
# plt.xlabel('')
# plt.ylabel('')
# plt.title('')
# plt.show()