from Crypto.Util.number import *
from Crypto.PublicKey import RSA
import random
from secret import flag

m = bytes_to_long(flag)
key = RSA.generate(1024)
passphrase = str(random.randint(0,999999)).zfill(6).encode()
output = key.export_key(passphrase=passphrase).split(b'\n')
for i in range(7, 15):
    output[i] = b'*' * 64
with open("priv.pem", 'wb') as f:
    for line in output:
        f.write(line + b'\n')
with open("enc.txt", 'w') as f:
    f.write(str(key._encrypt(m)))
