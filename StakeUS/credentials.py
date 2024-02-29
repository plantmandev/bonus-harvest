##             ##
## CREDENTIALS ##
##             ##

# Finds credentials based on CredentialType for different social casinos and returns value from 'credentials.JSON' file containing all login credentials

import json

CredentialsPath = 'credentials.JSON'
CredentialType = 'StakeUsername'

def ReadCredentials(CredentialsPath, CredentialType):
    # Read credentials.JSON file
    with open(CredentialsPath, 'r') as file:
        CredentialsData = json.load(file) 
    # Look for CredentialType
    if CredentialType in CredentialsData:
        return CredentialsData[CredentialType]
    else:
        return None 