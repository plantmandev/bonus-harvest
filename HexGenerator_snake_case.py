import secrets

def hex_generator(length): 
    # Number of bytes for random hex_value is determined. If length is even it divides the number of bytes by two, otherwise, it adds one
    num_bytes=length // 2 if length % 2==0 else (length // 2) + 1
    # Sequence of random butes is generated + Determined by 'random_bytes' 
    random_bytes=secrets.token_bytes(num_bytes)
    # Converting random values into hex values. Bytes are converted to integers, then integers are converted to hex value + '[2:] removes '0x' prefix
    hex_value=hex(int.from_bytes(random_bytes, 'big'))[2:]

    return hex_value

#'password' variable created + Hex value (password) length is assigned
length = 16
password = hex_generator(length)

# Output of generated password
print('The generated password is', "'" + password + "'")