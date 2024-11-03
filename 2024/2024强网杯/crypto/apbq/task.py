from Crypto.Util.number import *
from secrets import flag
from math import ceil
import sys

class RSA():
    def __init__(self, privatekey, publickey):
        self.p, self.q, self.d = privatekey
        self.n, self.e = publickey

    def encrypt(self, plaintext):
        if isinstance(plaintext, bytes):
            plaintext = bytes_to_long(plaintext)
        ciphertext = pow(plaintext, self.e, self.n)
        return ciphertext

    def decrypt(self, ciphertext):
        if isinstance(ciphertext, bytes):
            ciphertext = bytes_to_long(ciphertext)
        plaintext = pow(ciphertext, self.d, self.n)
        return plaintext

def get_keypair(nbits, e = 65537):
    p = getPrime(nbits//2)
    q = getPrime(nbits//2)
    n = p * q
    d = inverse(e, n - p - q + 1)
    return (p, q, d), (n, e)

if __name__ == '__main__':
    pt = './output.txt'
    fout = open(pt, 'w')
    sys.stdout = fout

    block_size = ceil(len(flag)/3)
    flag = [flag[i:i+block_size] for i in range(0, len(flag), block_size)]
    e = 65537

    print(f'[+] Welcome to my apbq game')
    # stage 1
    print(f'┃ stage 1: p + q')
    prikey1, pubkey1 = get_keypair(1024)
    RSA1 = RSA(prikey1, pubkey1)
    enc1 = RSA1.encrypt(flag[0])
    print(f'┃ hints = {prikey1[0] + prikey1[1]}')
    print(f'┃ public key = {pubkey1}')
    print(f'┃ enc1 = {enc1}')
    print(f'----------------------')

    # stage 2
    print(f'┃ stage 2: ai*p + bi*q')
    prikey2, pubkey2 = get_keypair(1024)
    RSA2 = RSA(prikey2, pubkey2)
    enc2 = RSA2.encrypt(flag[1])
    kbits = 180
    a = [getRandomNBitInteger(kbits) for i in range(100)]
    b = [getRandomNBitInteger(kbits) for i in range(100)]
    c = [a[i]*prikey2[0] + b[i]*prikey2[1] for i in range(100)]
    print(f'┃ hints = {c}')
    print(f'┃ public key = {pubkey2}')
    print(f'┃ enc2 = {enc2}')
    print(f'----------------------')

    # stage 3
    print(f'┃ stage 3: a*p + q, p + bq')
    prikey3, pubkey3 = get_keypair(1024)
    RSA3 = RSA(prikey3, pubkey3)
    enc3 = RSA2.encrypt(flag[2])
    kbits = 512
    a = getRandomNBitInteger(kbits)
    b = getRandomNBitInteger(kbits)
    c1 = a*prikey3[0] + prikey3[1]
    c2 = prikey3[0] + b*prikey3[1] 
    print(f'┃ hints = {c1, c2}')
    print(f'┃ public key = {pubkey3}')
    print(f'┃ enc3 = {enc3}')
