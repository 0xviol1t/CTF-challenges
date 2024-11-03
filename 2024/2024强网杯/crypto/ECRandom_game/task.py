from flag import M, q, a, b, select
import hashlib
from hashlib import sha256
from Crypto.Util.number import *
from Crypto.Cipher import AES
import sys
import ecdsa
from Crypto.Util.Padding import pad, unpad
from ecdsa.ellipticcurve import CurveFp,Point
from math import ceil
import os
import random
import string

flag = b'qwb{kLeMjJw_HBPtoHsVhnnxZdvtGjomivNDUI_vMRhZHrfKlCZ6HlGAeXRV_gQ8i117nGhzEMr0Zk_YTl1wftSskpX4JLnryE9Mhl96cPTWorGCl_R6nD33bcx1AYflag_leak}'
assert len(flag) == 136

BANNER = '''
 GGGGG   OOOOO   DDDDD   DDDDD    GGGGG    AAA    MM    MM EEEEEEE 
GG      OO   OO  DD   D  DD   D  GG       AAAAA   MMM  MMM EE      
GG  GGG OO   OO  DD   D  DD   D  GG  GGG  A   A   MM MM MM EEEEE   
GG   GG OO   OO  DD   D  DD   D  GG   GG  AAAAA   MM    MM EE      
GGGGGGG  OOOOO   DDDDD   DDDDD   GGGGGGG  A   A   MM    MM EEEEEEE 
 '''

NNN = []
def die(*args):
    pr(*args)
    quit()

def pr(*args):
    s = " ".join(map(str, args))
    sys.stdout.write(s + "\n")
    sys.stdout.flush()

def sc():
    return sys.stdin.buffer.readline()

def Rng(k):
    ran = random.getrandbits(k)
    NNN.append(ran)
    return ran


def ADD(num):
    NUM = 0
    for i in range(num):
        NUM += Rng(32)
    return NUM

def secure_choice(sequence):
    if not sequence:
        return None
    randbelow = 0
    for i, x in enumerate(sequence):
        randbelow += 1
        if os.urandom(1)[0] < (1 << 8) * randbelow // len(sequence):
            return x

def xDBLADD(P, Q, PQ, q, a, b):
    (X1, Z1), (X2, Z2), (X3, Z3) = PQ, P, Q
    X4 = (X2**2 - a * Z2**2) ** 2 - 8 * b * X2 * Z2**3
    Z4 = 4 * (X2 * Z2 * (X2**2 + a * Z2**2) + b * Z2**4)
    X5 = Z1 * ((X2 * X3 - a * Z2 * Z3) ** 2 - 4 * b * Z2 * Z3 * (X2 * Z3 + X3 * Z2))
    Z5 = X1 * (X2 * Z3 - X3 * Z2) ** 2
    X4, Z4, X5, Z5 = (c % q for c in (X4, Z4, X5, Z5))
    return (X4, Z4), (X5, Z5)

def xMUL(P, k, q, a, b):
    Q, R = (1, 0), P
    for i in reversed(range(k.bit_length() + 1)):
        if k >> i & 1:
            R, Q = Q, R
        Q, R = xDBLADD(Q, R, P, q, a, b)
        if k >> i & 1:
            R, Q = Q, R
    return Q

def shout(x, d, q, a, b):
    P = (x,1)
    Q = xMUL(P, d, q, a, b)
    return Q[0] * pow(Q[1], -1, q) % q

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secure_choice(characters) for i in range(length))
    return random_string

class ECCDu():
    def __init__(self,curve,G):
        self.state = getRandomNBitInteger(512)
        self.Curve = curve
        self.g = G

        self.num = Rng(32)
        d = 65537
        self.Q = self.num*self.g
        self.P = d * self.Q

    def ingetkey(self):
        t = int((self.state * self.Q).x())
        self.updade()
        return t%(2**250)

    def updade(self):
        self.state = int((self.state * self.P).x())

    def Random_key(self, n:int):
        out = 0
        number = ceil(n/250)
        for i in range(number):
            out = (out<<250) + self.ingetkey()
        return out % (2**n)

def proof_of_work():
    random.seed(os.urandom(8))
    proof = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(20)])
    _hexdigest = sha256(proof.encode()).hexdigest()
    pr(f"sha256(XXXX+{proof[4:]}) == {_hexdigest}".encode())
    pr('Give me XXXX: ')
    x = sc().rstrip(b'\n')
    if len(x) != 4 or sha256(x + proof[4:].encode()).hexdigest() != _hexdigest:
        return False
    return True

def main():
    pr(BANNER)
    pr('WELCOME TO THIS SIMPLE GAME!!!')
    ASSERT = proof_of_work()
    if not ASSERT:
        die("Not right proof of work")

    pr('Now we will start our formal GAME!!!')
    pr('===== First 1💪: =====')
    pr('Enter an integer as the parameter p for Curve: y^2 = x^3+12x+17 (mod p) and 250<p.bit_length()')
    p1 = int(sc())
    if not 250<=p1.bit_length():
        die('Wrong length!')
    curve = CurveFp(p1, 12, 17,1)
    pr(curve)
    pr('Please Enter a random_point G:')
    G_t = sc().split(b' ')
    Gx,Gy = int(G_t[0]),int(G_t[1])
    if not curve.contains_point(Gx,Gy):
        die('This point is outside the curve')
    G = Point(curve,Gx,Gy)

    for i in range(500):
        ECDU = ECCDu(curve,G)
        m  = 'My secret is a random saying of phrase,As below :' + generate_random_string(119)
        Number = ECDU.Random_key(1344)
        c = Number^bytes_to_long(m.encode())
        pr(f'c = {c}')
        pr(f'P = {int(ECDU.P.x()), int(ECDU.P.y())}')
        pr(f'Q = {int(ECDU.Q.x()), int(ECDU.Q.y())}')

        pr('Enter m:')
        m_en = sc().rstrip(b'\n')
        if m_en != m.encode():
            die('This is not the right m,Please try again')
        else:
            pr('Right m!!!')
    pr('Bingo!')
    new_state,new_state1 = ADD(136),ADD(50)
    
    random.seed(new_state)

    pr('===== Second 2💪: =====')
    curve1 = CurveFp(q,a,b,1)
    pr(f'{int(curve1.p()),int(curve1.a()),int(curve1.b())}')

    pr("Enter a number that does not exceed 1500")
    number = int(sc())

    pr(f'You only have {number} chances to try')
    success = 0
    for i in range(number):
        Gx = secure_choice(select)
        R = Rng(25)
        pr('Gx = ',Gx)
        pr('Px = ',shout(Gx, R, q, a, b))
        R_n = int(sc().rstrip(b'\n'))
        if R_n != R:
            pr(f'Wrong number!!!,Here is your right number {R}')
        else:
            pr('GGood!')
            success += 1

    if int(success)/int(number) <= 0.262:
        die('Please Try more...')

    random.seed(new_state)
    iv_num = ADD(2000)

    iv = hashlib.sha256(str(iv_num).encode()).digest()[:16]
    key = hashlib.sha256(str(new_state1).encode()).digest()[:16]
    Aes = AES.new(key,AES.MODE_CBC, iv)
    C = Aes.encrypt(pad(flag,16))

    key_n, iv_n = int(sc()), int(sc())
    iv1 = hashlib.sha256(str(iv_n).encode()).digest()[:16]
    key1 = hashlib.sha256(str(key_n).encode()).digest()[:16]
    Aes_verify = AES.new(key1,AES.MODE_CBC, iv1)
    C_verify = unpad(Aes_verify.decrypt(C),16)

    if C_verify == flag:
        pr('Congratulations🎇🎇🎇!!!!')
        pr('Here is your flag😊：', M)
    else:
        pr('Maybe you could get the right flag!')

if __name__ == '__main__':
    main()