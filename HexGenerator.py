import secrets

def HexGenerator(length): 
    # Number of bytes for random hex_value is determined. If length is even it divides the number of bytes by two, otherwise, it adds one
    NumBytes=length // 2 if length % 2==0 else (length // 2) + 1
    # Sequence of random butes is generated + Determined by 'random_bytes' 
    RandomBytes=secrets.token_bytes(NumBytes)
    # Converting random values into hex values. Bytes are converted to integers, then integers are converted to hex value + '[2:] removes '0x' prefix
    HexValue=hex(int.from_bytes(RandomBytes, 'big'))[2:]

    return HexValue

#'password' variable created + Hex value (password) length is assigned
length = 16
password = HexGenerator(length)

# Output of generated password
print('The generated password is', "'" + password + "'")