#   INITIAL SET-UP   #
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt

#   DATA ANALYIS   # 
time_scope = 16

def stake_earnings_list(time_scope): 
    stake_earnings = []
    stake_base_earnings = 1 
    stake_average_RTP = 98
    stake_daily_earnings = stake_base_earnings * (stake_average_RTP / 100)

    for x in range(1, time_scope):
        stake_earnings.append(float((stake_daily_earnings)))
        stake_daily_earnings += float((stake_base_earnings * (stake_average_RTP / 100)))
        stake_daily_earnings = float("{:.2f}".format(stake_daily_earnings))
        # print(stake_daily_earnings)

def chumba_earnings_list(time_scope): 
    chumba_earnings = [] 
    chumba_base_earnings = 1
    chumba_average_RTP = 98.78
    chumba_daily_earnings = chumba_base_earnings * (chumba_average_RTP / 100)

    for x in range(1, time_scope):
        chumba_earnings.append(float((chumba_daily_earnings)))
        chumba_daily_earnings += float((chumba_base_earnings * (chumba_average_RTP / 100)))
        chumba_daily_earnings = float("{:.2f}".format(chumba_daily_earnings))
        # print(chumba_daily_earnings)

def fortune_earnings_list(time_scope): 
    fortune_earnings = []
    fortune_base_earnings = 1
    fortune_average_RTP = 95.33
    fortune_daily_earnings = fortune_base_earnings * (fortune_average_RTP / 100)

    for x in range(1, time_scope):
        fortune_earnings.append(float((fortune_daily_earnings)))
        fortune_daily_earnings += float((fortune_base_earnings * (fortune_average_RTP / 100)))
        fortune_daily_earnings = float("{:.2f}".format(fortune_daily_earnings))
        # print(fortune_daily_earnings)

#        #       
# McLuck # 
#        # 


# McLuckEarnings = []
# # McLuck has a random bonus 'DailyEarningsOptions'
# McLuckEarningsOptions = [0.20, 0.25, 0.30, 0.35, 0.40] 
# McLuckAverageRTP = 96.57

# # Randomly chooses a reward from 'McLuckEarnigns' list
# def McLuckRandomEarning():
#     McLuckEarningsOptions = [0.20, 0.25, 0.35]  # Example list of options
#     RandomEarning = random.choice(McLuckEarningsOptions)
#     return RandomEarning

# for x in range(1, TimeScope):

#     McLuckPreviousEarning = 0

#     # Randomizes Earning amount + Returns earning after RTP 
#     McLuckPredictedEarning = McLuckRandomEarning() * (McLuckAverageRTP/100)
#     # Sets 'McLuckPreviousEarning' as 'McLuckPreviousEarning' to allow for calculation of cumulative earnings
#     McLuckPreviousEarning = McLuckPredictedEarning
#     # Adds sum earnings value to 'McLuckEarnings' list
#     McLuckEarnings.append(float("{:.2f}".format(McLuckPredictedEarning)))


# ModoUS
modo_earnings = [0.3, 0.3, 0.3, 0.5, 1, 1, 1]
modo_base_earnings = 1
modo_average_RTP = 95.93
modo_daily_earnings = modo_base_earnings * (modo_average_RTP / 100)

for x in range(1, (time_scope - 7)):
    modo_earnings.append(float("{:.2f}".format(modo_daily_earnings)))
    modo_daily_earnings += float("{:.2f}".format(modo_base_earnings * (modo_average_RTP / 100)))

#   EXPORT TO CSV   #

def export_to_csv(): 
    # Add EarningsData.csv in the same directory as visualization and calculations 
    earning_data_path = os.path.join('data_analysis', 'earning_data.csv')

    # Write data to EarningsData.csv
    with open(earning_data_path, 'a', newline='') as CSVFile:
        csv_write = csv.writer(CSVFile)
        if os.stat(earning_data_path).st_size == 0:
            csv_write.writerow(['day', 'stake_earning', 'chumba_earning', 'fortune_earning', 'mcluck_earning', 'modo_earnings'])

        # Write data for each day
        for Day, (StakeEarnings, ChumbaEarnings, FortuneEarnings, McLuckEarnings, ModoEarnings) in enumerate(zip(StakeEarnings, ChumbaEarnings, FortuneEarnings,    McLuckEarnings, ModoEarnings), start=1):
            csv_write.writerow([Day, StakeEarnings, ChumbaEarnings, FortuneEarnings, McLuckEarnings, ModoEarnings])


#   VISUALIZATION   # 

def earning_visualization(): 
    # Add EarningsData.csv in the same directory as visualization and calculations 
    earning_data_path = os.path.join('data_analysis', 'earning_data.csv')
    
    # Create data frame from EarningsData.csv
    df = pd.read_csv(earning_data_path)

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
    plt.title('Earnings Over Time', fontsize=16)
    plt.xlabel('Days', fontsize=14)
    plt.ylabel('Earnings', fontsize=14)
    plt.grid(False)
    plt.legend(fontsize=12)

    # Save plot
    plt.savefig('EarningsProjection.png', format = 'png')

    # Show the plot
    plt.show()