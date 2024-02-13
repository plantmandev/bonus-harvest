import random 

TimeScope = 7

McLuckEarnings = []
# McLuck has a random bonus 'DailyEarningsOptions'
McLuckEarningsOptions = [0.25, 0.35] 
McLuckAverageRTP = 96.57

# Randomly chooses a reward from 'McLuckEarnigns' list
def McLuckRandomEarning():
    McLuckEarningsOptions = [0.20, 0.25, 0.35]  # Example list of options
    RandomEarning = random.choice(McLuckEarningsOptions)
    return RandomEarning

for x in range(1, TimeScope):

    McLuckPreviousEarning = 0

    # Randomizes Earning amount + Returns earning after RTP 
    McLuckPredictedEarning = McLuckRandomEarning() * (McLuckAverageRTP/100)
    # Sets 'McLuckPreviousEarning' as 'McLuckPreviousEarning' to allow for calculation of cumulative earnings
    McLuckPreviousEarning = McLuckPredictedEarning
    # Adds sum earnings value to 'McLuckEarnings' list
    McLuckEarnings.append(float("{:.2f}".format(McLuckPredictedEarning)))

print(McLuckPreviousEarning)

print(McLuckEarnings)

# print(McLuckRandomEarning())

# for x in range(1, TimeScope):
#     StakeEarnings.append(float("{:.2f}".format(StakeDailyEarnings)))
#     StakeDailyEarnings += float("{:.2f}".format(StakeBaseEarnings * (StakeAverageRTP / 100)))