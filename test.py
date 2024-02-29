#   INITIAL SET-UP   #
import os
import csv
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#   DATA ANALYIS   # 

# Model time scope (exclusive)
time_scope = 16

def modo_earnings_list(time_scope): 
    modo_earnings = [0.3, 0.3, 0.3, 0.5, 1, 1, 1]
    modo_base_earnings = 1
    modo_average_RTP = 95.93
    modo_daily_earnings = modo_base_earnings * (modo_average_RTP / 100)

    for x in range(1,8):
        print(modo_earnings[x])

    # for x in range(1, (time_scope - 7)):
    #     modo_earnings.append(float((modo_daily_earnings)))
    #     modo_daily_earnings += float((modo_base_earnings * (modo_average_RTP / 100)))
    #     modo_daily_earnings = float("{:.2f}".format(modo_daily_earnings))
        
        # print(modo_daily_earnings)

modo_earnings_list(time_scope)


# print(chumba_earnings_list(time_scope))
# print(stake_earnings_list(time_scope))