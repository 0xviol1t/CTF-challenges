# coding: utf-8
#!/usr/bin/env python2

import gmpy2
import random
import binascii
from hashlib import sha256
from sympy import nextprime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import long_to_bytes
from FLAG import flag
#flag = 'wdflag{123}'
def victory_encrypt(plaintext, key):
    key = key.upper()
    key_length = len(key)
    plaintext = plaintext.upper()
    ciphertext = ''

    for i, char in enumerate(plaintext):
        if char.isalpha():
            shift = ord(key[i % key_length]) - ord('A')
            encrypted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            ciphertext += encrypted_char
        else:
            ciphertext += char

    return ciphertext

victory_key = "WANGDINGCUP"
victory_encrypted_flag = victory_encrypt(flag, victory_key)

p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
a = 0
b = 7
xG = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
yG = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
G = (xG, yG)
n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
h = 1
zero = (0,0)

dA = nextprime(random.randint(0, n))

if dA > n:
    print("warning!!")

def addition(t1, t2):
    if t1 == zero:
        return t2
    if t2 == zero:
        return t2
    (m1, n1) = t1
    (m2, n2) = t2
    if m1 == m2:
        if n1 == 0 or n1 != n2:
            return zero
        else:
            k = (3 * m1 * m1 + a) % p * gmpy2.invert(2 * n1 , p) % p
    else:
        k = (n2 - n1 + p) % p * gmpy2.invert((m2 - m1 + p) % p, p) % p
    m3 = (k * k % p - m1 - m2 + p * 2) % p
    n3 = (k * (m1 - m3) % p - n1 + p) % p
    return (int(m3),int(n3))

def multiplication(x, k):
    ans = zero
    t = 1
    while(t <= k):
        if (k &t )>0:
            ans = addition(ans, x)
        x = addition(x, x)
        t <<= 1
    return ans

def getrs(z, k):
    (xp, yp) = P
    r = xp
    s = (z + r * dA % n) % n * gmpy2.invert(k, n) % n
    return r,s

z1 = random.randint(0, p)
z2 = random.randint(0, p)
k = random.randint(0, n)
P = multiplication(G, k)
hA = multiplication(G, dA)
r1, s1 = getrs(z1, k)
r2, s2 = getrs(z2, k)

print("r1 = {}".format(r1))
print("r2 = {}".format(r2))
print("s1 = {}".format(s1))
print("s2 = {}".format(s2))
print("z1 = {}".format(z1))
print("z2 = {}".format(z2))

key = sha256(long_to_bytes(dA)).digest()
cipher = AES.new(key, AES.MODE_CBC)
iv = cipher.iv
encrypted_flag = cipher.encrypt(pad(victory_encrypted_flag.encode(), AES.block_size))
encrypted_flag_hex = binascii.hexlify(iv + encrypted_flag).decode('utf-8')

print("Encrypted flag (AES in CBC mode, hex):", encrypted_flag_hex)

# output
# r1 = 28857061626266697731960297346547380130694223166851804642930502594650578288425
# r2 = 28857061626266697731960297346547380130694223166851804642930502594650578288425
# s1 = 81842916501936654327181596127464444170184582938148211467350979906270329843047
# s2 = 54199410087637342004207138894657653701426382978399616033659324046436549994669
# z1 = 114768147762808206397023700697633814229154932218327120646122869299219028759434
# z2 = 63513092260201266423877548128429517837199255134650637253201969399356248912467
# ('Encrypted flag (AES in CBC mode, hex):', u'51559ebae12fdd12e0e84df2baf07e3389b688398a71b62717fb77e0f6abdd40d848ee028b70681bc566ef2729d80b7a2778ad5b322b68501b6bbcef820b4719')