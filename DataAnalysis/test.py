import random 

TimeScope = 16

McLuckEarnings = []
# McLuck has a random bonus 'DailyEarningsOptions'
McLuckEarningsOptions = [0.25, 0.35] 
McLuckAverageRTP = 96.57


def McLuckRandomEarning():
    McLuckEarningsOptions = [0.25, 0.35]  # Example list of options
    RandomEarning = random.choice(McLuckEarningsOptions)
    return RandomEarning

for x in range(1, TimeScope):
    McLuckPredictedEarning = McLuckRandomEarning() * (McLuckAverageRTP/100)
    McLuckEarnings.append(McLuckPredictedEarning)
    McLuckPredictedEarning += McLuckRandomEarning() * (McLuckAverageRTP/100)

    print(McLuckEarnings)

print(McLuckEarnings)

# print(McLuckRandomEarning())