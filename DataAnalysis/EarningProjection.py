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

# X-axis of earnings visualization
DayLimit = 365
DaysAxis = []
for x in range(1, DayLimit + 1):
    DaysAxis.append(x)
    x += 1

csv_file_path = os.path.join('DataAnalysis' ,'EarningsData.csv')
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['DaysAxis'])  # Write header
    csv_writer.writerow(DaysAxis) 

# StakeUS
StakeEarnings = []
StakeAverageWeeklyEarnings = 7
StakeAveragedRTP = 98

StakeInitialEarnings = StakeAverageWeeklyEarnings * (StakeAveragedRTP/100)
StakeThereafterEarnings = StakeInitialEarnings

for x in range(1, DayLimit):
    StakeEarnings.append(StakeInitialEarnings)
    StakeInitialEarnings += StakeAverageWeeklyEarnings * (StakeAveragedRTP/100)

plt.xlabel('DaysAxis')
plt.ylabel('StakeEarnings')
plt.title('Simple Line Plot')

plt.show()

# ChumbaCasino
ChumbaAverageWeeklyEarnings = 7
ChumbaAveragedRTP = 98.78

ChumbaFirstWeekEarnings = ChumbaAverageWeeklyEarnings * (StakeAveragedRTP/100)
ChumbaThereafterEarnings = ChumbaFirstWeekEarnings

# FortuneCoins
FortuneAverageWeeklyEarnings = 7
FortuneAveragedRTP = 95.33

FortuneFirstWeekEarnings = FortuneAverageWeeklyEarnings * (StakeAveragedRTP/100)
FortuneThereafterEarnings = FortuneFirstWeekEarnings

# McLuck

# McLuckEarnings = [0.3, 0.3, 0.3, 0.3, 0.5, 1]

# McLuckThereafterAvgEarnings = 7 
# McLuckAveragedRTP = 96.57

# McLuckThereafterEarnings = McLuckThereafterAvgEarnings * (McLuckAveragedRTP/100)

# for x in range(1, DayLimit):
#     McLuckEarnings.append(McLuckInitialEarnings)
#     StakeInitialEarnings += StakeAverageWeeklyEarnings * (StakeAveragedRTP/100)

# for x in range(1,DayLimit + 1): 
#     for y in range(8, DayLimit + 1):
#         StakeEarnings.append(StakeEarnings[y] + StakeThereafterEarnings)
#         StakeThereafterEarnings += McLuckThereafterAvgEarnings * (McLuckAveragedRTP/100)

# ModoUS
ModoFirstWeekAvgEarnings = 4.4
ModoThereafterAvgEarnings = 7 
ModoAveragedRTP = 95.93

ModoFirstWeekEarnings = ModoFirstWeekAvgEarnings * (ModoAveragedRTP/100)
ModoThereafterEarnings = ModoThereafterAvgEarnings * (ModoAveragedRTP/100)