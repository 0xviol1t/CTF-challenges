from random import choice, randint
from Crypto.Util.number import isPrime, sieve_base as primes, getPrime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import md5

flag = b'WKCTF{}'
flag = pad(flag,16)
def myPrime(bits):
    while True:
        n = 2
        while n.bit_length() < bits:
            n *= choice(primes)
        if isPrime(n + 1):
            return n + 1

def encrypt(key, message):
    return pow(65537, message, key)

p = myPrime(512)
q = getPrime(512)
N = p * q
m = [getPrime(512) for i in range(1024)]
enc = [encrypt(N, _) for _ in m]

a = [randint(1,2 ** 50) for i in range(70)]
b = [randint(1,2 ** 50) for i in range(50)]
secret = randint(2**119, 2**120)

ra = 1
rb = 1
for i in range(120):
    if(i < 70):
        if (secret >> i) & 1:
            ra *= a[i]
            ra %= p
    else:
        if (secret >> i) & 1:
            rb *= b[i-70]
            rb %= q


key = md5(str(secret).encode()).hexdigest()[16:].encode()
cipher = AES.new(key,AES.MODE_ECB)

with open("output.txt","w") as f:
    f.write(f'c = {cipher.encrypt(flag).hex()}\n')
    f.write(f'm = {m}\n')
    f.write(f'enc = {enc}\n')
    f.write(f'a = {a}\n')
    f.write(f'b = {b}\n')
    f.write(f'ra = {ra}\n')
    f.write(f'rb = {rb}\n')