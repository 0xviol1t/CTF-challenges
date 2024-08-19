from ecdsa.ecdsa import *
from Crypto.Util.number import *
import hashlib
import gmpy2

def inverse_mod(a, m):
    if a == 0:
        return 0
    return gmpy2.powmod(a, -1, m)

def bit_length(x):
    return x.bit_length()

def get_malicious_key():
    a = getRandomNBitInteger(20)
    b = getRandomNBitInteger(21)
    w = getRandomNBitInteger(30)
    X = getRandomNBitInteger(25)
    return a, b, w, X

class RSZeroError(RuntimeError):
    pass


class InvalidPointError(RuntimeError):
    pass


class Signature(object):
    """ECDSA signature."""

    def __init__(self, r, s):
        self.r = r
        self.s = s


class Public_key(object):
    """Public key for ECDSA."""

    def __init__(self, generator, point, verify=True):

        self.curve = generator.curve()
        self.generator = generator
        self.point = point
        n = generator.order()
        p = self.curve.p()
        if not (0 <= point.x() < p) or not (0 <= point.y() < p):
            raise InvalidPointError(
                "The public point has x or y out of range."
            )
        if verify and not self.curve.contains_point(point.x(), point.y()):
            raise InvalidPointError("Point does not lay on the curve")
        if not n:
            raise InvalidPointError("Generator point must have order.")

        if (
            verify
            and self.curve.cofactor() != 1
            and not n * point == ellipticcurve.INFINITY
        ):
            raise InvalidPointError("Generator point order is bad.")


class Private_key(object):
    """Private key for ECDSA."""

    def __init__(self, public_key, secret_multiplier):

        self.public_key = public_key
        self.secret_multiplier = secret_multiplier

    def sign(self, hash, random_k):

        G = self.public_key.generator
        n = G.order()
        k = random_k % n
        p1 = k * G
        r = p1.x() % n
        if r == 0:
            raise RSZeroError("amazingly unlucky random number r")
        s = (
            inverse_mod(k, n)
            * (hash + (self.secret_multiplier * r) % n)
        ) % n
        if s == 0:
            raise RSZeroError("amazingly unlucky random number s")
        return Signature(r, s)

    def malicious_sign(self,hash, random_k, a, b, w, X):
        # t = random.randint(0,1)
        t = 1
        G = self.public_key.generator
        Y = X * G
        n = G.order()
        k1 = random_k
        z = (k1 - w * t) * G + (-a * k1 - b) * Y
        zx = z.x() % n
        k2 = int(hashlib.sha1(str(zx).encode()).hexdigest(), 16)
        #print(f'k2 = {k2}')
        p1 = k2 * G
        r = p1.x() % n
        if r == 0:
            raise RSZeroError("amazingly unlucky random number r")
        s = (
                    inverse_mod(k2, n)
                    * (hash + (self.secret_multiplier * r) % n)
            ) % n
        if s == 0:
            raise RSZeroError("amazingly unlucky random number s")
        return (Signature(r, s),k2)

if __name__ == '__main__':
    a,b,w,X = get_malicious_key()
   
    message1 = b'It sounds as though you were lamenting,'
    message2 = b'a butterfly cooing like a dove.'
    hash_message1 = int(hashlib.sha1(message1).hexdigest(), 16)
    hash_message2 = int(hashlib.sha1(message2).hexdigest(), 16)
    private = getRandomNBitInteger(50)
    rand = getRandomNBitInteger(49)
    public_key = Public_key(generator_192, generator_192 * private)
    private_key = Private_key(public_key, private)
    sig = private_key.sign(hash_message1, rand)
    malicious_sig,k2 = private_key.malicious_sign(hash_message2, rand, a,b,w,X)
    
    print(a,b,w,X)
    print(sig.r)
    print(malicious_sig.r)

    '''
    751818 1155982 908970521 20391992
    6052579169727414254054653383715281797417510994285530927615
    3839784391338849056467977882403235863760503590134852141664
    '''
    
    # flag为flag{uuid}格式
    flag = b''
    m = bytes_to_long(flag)
    p = k2
    for i in range(99):
        p = gmpy2.next_prime(p)
    q = gmpy2.next_prime(p)
    e = 65537
    c = pow(m,e,p*q)
    print(c)
    # 1294716523385880392710224476578009870292343123062352402869702505110652244504101007338338248714943