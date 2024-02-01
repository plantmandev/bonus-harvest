##             ## 
## DESCRIPTION ## 
##             ## 

# This script is used to log into the Stake.us website. This function stores the username and generates a hex-value secure password in order to prevent the main user to have access to this website, as our primary goal is to obtain daily rewards and cash them in, not gamble using the Stake.us website. 

# import stake_credentials
import SocialCasinos.StakeUS.StakeLogin as StakeLogin
# import stake_verification
import SocialCasinos.StakeUS.StakeFarming as StakeFarming
import SocialCasinos.StakeUS.StakeHarvest as StakeHarvest


# stake_credentials()
StakeLogin()
# stake_verification()
StakeFarming()
StakeHarvest()
