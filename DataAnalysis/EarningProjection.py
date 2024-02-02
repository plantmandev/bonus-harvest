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
TimeScope = 16

# StakeUS # 
StakeEarnings = []
StakeBaseEarnings = 1 
StakeAverageRTP = 98
StakeDailyEarnings = StakeBaseEarnings * (StakeAverageRTP/100)

for x in range(1, TimeScope):
    StakeEarnings.append(float("{:.2f}".format(StakeDailyEarnings)))
    StakeDailyEarnings += float("{:.2f}".format(StakeBaseEarnings * (StakeAverageRTP / 100)))


# ChumbaCasino # 
ChumbaEarnings = [] 
ChumbaBaseEarnings = 1
ChumbaAverageRTP = 98.78
ChumbaDailyEarnings = ChumbaBaseEarnings * (ChumbaAverageRTP/100)

for x in range(1, TimeScope):
    ChumbaEarnings.append(float("{:.2f}".format(ChumbaDailyEarnings)))
    ChumbaDailyEarnings += float("{:.2f}".format(ChumbaBaseEarnings * (ChumbaAverageRTP / 100)))

# FortuneCoins
FortuneEarnings = []
FortuneBaseEarnings = 1
FortuneAverageRTP = 95.33
FortuneDailyEarnings = FortuneBaseEarnings * (FortuneAverageRTP/100)

for x in range(1, TimeScope):
    FortuneEarnings.append(float("{:.2f}".format(FortuneDailyEarnings)))
    FortuneDailyEarnings += float("{:.2f}".format(FortuneBaseEarnings * (FortuneAverageRTP / 100)))

# McLuck
McLuckEarnings = [0.3, 0.3, 0.3, 0.5, 1, 1, 1]
McLuckBaseEarnings = 1
McLuckAverageRTP = 96.57
McLuckDailyEarnings = McLuckBaseEarnings * (McLuckAverageRTP/100)

for x in range(1, (TimeScope - 7)):
    McLuckEarnings.append(float("{:.2f}".format(McLuckDailyEarnings)))
    McLuckDailyEarnings += float("{:.2f}".format(McLuckBaseEarnings * (McLuckAverageRTP / 100)))

# ModoUS
ModoEarnings = [0.3, 0.3, 0.3, 0.5, 1, 1, 1]
ModoBaseEarnings = 1
ModoAverageRTP = 95.93
ModoDailyEarnings = ModoBaseEarnings * (ModoAverageRTP/100)

for x in range(1, (TimeScope - 7)):
    ModoEarnings.append(float("{:.2f}".format(ModoDailyEarnings)))
    ModoDailyEarnings += float("{:.2f}".format(ModoBaseEarnings * (ModoAverageRTP / 100)))

#               # 
# EXPORT TO CSV #
#               # 

# Add EarningsData.csv in the same directory as visualization and calculations 
EarningsDataPath = os.path.join('DataAnalysis', 'EarningsData.csv')

# Write data to EarningsData.csv
with open(EarningsDataPath, 'a', newline='') as CSVFile:
    CSVWrite = csv.writer(CSVFile)
    if os.stat(EarningsDataPath).st_size == 0:
        CSVWrite.writerow(['Day', 'StakeEarnings', 'ChumbaEarnings', 'FortuneEarnings', 'McLuckEarnings', 'ModoEarnings'])

    # Write data for each day
    for Day, (StakeEarnings, ChumbaEarnings, FortuneEarnings, McLuckEarnings, ModoEarnings) in enumerate(zip(StakeEarnings, ChumbaEarnings, FortuneEarnings, McLuckEarnings, ModoEarnings), start=1):
        CSVWrite.writerow([Day, StakeEarnings, ChumbaEarnings, FortuneEarnings, McLuckEarnings, ModoEarnings])

#               # 
# VISUALIZATION # 
#               # 

# Create data frame from EarningsData.csv
df = pd.read_csv(EarningsDataPath)

# Extract data from EarningsData.csv into data frames
Day = df['Day']
StakeEarnings = df['StakeEarnings']
ChumbaEarnings = df['ChumbaEarnings']
FortuneEarnings = df['FortuneEarnings']
McLuckEarnings = df['McLuckEarnings']
ModoEarnings = df['ModoEarnings']

plt.plot(Day, StakeEarnings, label='Stake Earnings', marker='o', linewidth=2, markersize=6)
plt.plot(Day, ChumbaEarnings, label='Chumba Earnings', marker='s', linewidth=2, markersize=6)
plt.plot(Day, FortuneEarnings, label='Fortune Earnings', marker='^', linewidth=2, markersize=6)
plt.plot(Day, McLuckEarnings, label='McLuck Earnings', marker='d', linewidth=2, markersize=6)
plt.plot(Day, ModoEarnings, label='Modo Earnings', marker='v', linewidth=2, markersize=6)

# Customize plot appearance
plt.title('Earnings Over Days', fontsize=16)
plt.xlabel('Days', fontsize=14)
plt.ylabel('Earnings', fontsize=14)
plt.grid(False)
plt.legend(fontsize=12)

# Save plot
plt.savefig('EarningsProjection.png', format = 'png')

# Show the plot
plt.show()