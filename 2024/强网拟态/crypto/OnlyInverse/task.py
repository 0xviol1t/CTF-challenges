from Crypto.Util.number import *
from hashlib import sha256
import socketserver
import signal
import os
import string
import random


s_box=[99, 96, 239, 98, 37, 149, 238, 11, 64, 178, 24, 56, 168, 91, 87, 49, 255, 164, 134, 190, 211, 30, 195, 130, 139, 34, 127, 44, 121, 163, 74, 174, 45, 209, 141, 107, 156, 180, 128, 35, 59, 125, 208, 92, 51, 175, 158, 62, 23, 172, 206, 215, 109, 40, 201, 165, 110, 60, 3, 210, 250, 181, 136, 72, 68, 122, 58, 202, 20, 48, 103, 216, 145, 207, 133, 86, 159, 12, 67, 120, 79, 135, 108, 38, 183, 15, 241, 185, 75, 33, 5, 104, 144, 76, 192, 90, 89, 129, 137, 13, 184, 146, 57, 166, 100, 170, 203, 25, 54, 205, 0, 46, 232, 161, 193, 247, 83, 167, 182, 39, 162, 243, 8, 105, 155, 118, 251, 254, 253, 225, 226, 248, 194, 246, 186, 153, 213, 218, 199, 19, 97, 101, 179, 148, 26, 221, 53, 212, 16, 230, 244, 245, 29, 95, 217, 224, 115, 28, 227, 214, 117, 231, 17, 61, 233, 176, 204, 187, 9, 32, 85, 189, 42, 81, 14, 197, 119, 88, 66, 73, 80, 252, 235, 240, 151, 234, 249, 36, 191, 188, 242, 154, 126, 27, 18, 157, 22, 4, 84, 114, 131, 10, 150, 111, 78, 124, 140, 82, 237, 106, 138, 198, 55, 21, 94, 70, 196, 229, 52, 7, 223, 112, 200, 222, 171, 116, 2, 69, 50, 113, 41, 143, 123, 177, 1, 93, 132, 147, 65, 173, 142, 6, 43, 63, 219, 169, 102, 236, 31, 220, 228, 152, 47, 77, 160, 71]

def matrix2bytes(s):
    m = b''
    for i in range(4):
        m += bytes(s[i])
    return m


def bytes2matrix(s):
    m = list(s)
    return [m[4*i:4*i+4] for i in range(4)]


def transform(a):
    assert len(a) == 4
    assert len(a[0]) == 4
    res = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for j in range(4):
        for i in range(4):
            res[j][i] = a[i][j]
    return res


def add_round_key(s, k):
    return [[x ^ y for x, y in zip(s[i], k[i])] for i in range(4)]

def addI_round_key(s, k):
    return [[(x + y)%256 for x, y in zip(s[i], k[i])] for i in range(4)]


def sub_bytes(s):
    return [[s_box[item] for item in s[i]] for i in range(4)]


def inv_sub_bytes(s):
    return [[inv_s_box[item] for item in s[i]] for i in range(4)]


def shift_rows(s):
    for i in range(4):
        s[i] = s[i][i:]+s[i][:i]
    return s


def inv_shift_rows(s):
    for i in range(4): 
        s[i] = s[i][-i:]+s[i][:-i]
    return s


x0time = lambda x: x
x1time = lambda x: ((x << 1) ^ 0x1B) & 0xFF if x & 0x80 else x << 1
x2time = lambda x: x1time(x1time(x))
x3time = lambda x: x1time(x1time(x1time(x)))
f1 = lambda x: x0time(x) ^ x1time(x)
f2 = lambda x: x3time(x) ^ x2time(x) ^ x1time(x)
f3 = lambda x: x3time(x) ^ x1time(x) ^ x0time(x)
f4 = lambda x: x3time(x) ^ x0time(x)
f5 = lambda x: x3time(x) ^ x2time(x) ^ x0time(x)


def rshift(x, i):
    return x[-i:]+x[:-i]

def add(x, y):
    return [(i^j) for i, j in zip(x, y)]

def mix_single_column(s):
    res = [0, 0, 0, 0]
    for i in range(len(s)):
        res = add(rshift(table[s[i]], i), res)    
    return res

def inv_mix_single_column(a):
    res = [0] * 4
    res[0] = f2(a[0]) ^ f3(a[1]) ^ f5(a[2]) ^ f4(a[3])
    res[1] = f4(a[0]) ^ f2(a[1]) ^ f3(a[2]) ^ f5(a[3])
    res[2] = f5(a[0]) ^ f4(a[1]) ^ f2(a[2]) ^ f3(a[3])
    res[3] = f3(a[0]) ^ f5(a[1]) ^ f4(a[2]) ^ f2(a[3])
    return res

def s_mix_table():
    tb = []
    for x in range(256):
        x_ = s_box[x]
        tb.append([x1time(x_), x_, x_, f1(x_)])
    return tb
table = s_mix_table()

def inv_mix_columns(s):
    inv_mix_res = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for i in range(4):
        res = inv_mix_single_column([s[j][i] for j in range(4)])
        inv_mix_res[0][i] = res[0]
        inv_mix_res[1][i] = res[1]
        inv_mix_res[2][i] = res[2]
        inv_mix_res[3][i] = res[3]
    return inv_mix_res

def S_with_Mix(s):
    r = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for i in range(4):
        res = mix_single_column([s[j][i] for j in range(4)])
        r[0][i] = res[0]
        r[1][i] = res[1]
        r[2][i] = res[2]
        r[3][i] = res[3]
    return r

def key_expand(master_key: bytes, n_round=10):
    key_list = bytes2matrix(master_key)
    r_con = (
        0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36
    )
    while len(key_list) < 4*(n_round+1):
        time = len(key_list)
        if time % 4 == 0:
            temp = key_list[-1][1:]+key_list[-1][:1]
            temp = [s_box[i] for i in temp]
            temp[0] ^= r_con[time//4-1]
        else:
            temp = key_list[-1]
        temp = [i ^ j for i, j in zip(temp, key_list[-4])]
        key_list.append(temp)
    return key_list

def encrypt(plain_text, master_key, n_round=10):
    real_key = key_expand(master_key,n_round)
    m_matrix = transform(bytes2matrix(plain_text))
    m_matrix = add_round_key(m_matrix, transform(real_key[:4]))
    for i in range(1, n_round):
        m_matrix = shift_rows(m_matrix)
        m_matrix = S_with_Mix(m_matrix)
        m_matrix = add_round_key(m_matrix, transform(real_key[4 * i:4 * i + 4]))
    m_matrix = sub_bytes(m_matrix)
    #m_matrix = shift_rows(m_matrix)
    m_matrix = addI_round_key(m_matrix, transform(real_key[-4:]))
    return matrix2bytes(transform(m_matrix))




class Task(socketserver.BaseRequestHandler):
    def _recvall(self):
        BUFF_SIZE = 2048
        data = b''
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break
        return data.strip()

    def send(self, msg, newline=True):
        try:
            if newline:
                msg += b'\n'
            self.request.sendall(msg)
        except:
            pass

    def recv(self, prompt=b'> '):
        self.send(prompt, newline=False)
        return self._recvall()

    def handle(self):
        key=os.urandom(16)
        signal.alarm(600)
        for i in range(130):
            self.send(b"a block of message,plz",newline=False)
            rev=self.recv()
            plain=bytes.fromhex(rev.decode())[:16]
            c=encrypt(plain, key, n_round=5)
            self.send(c.hex().encode())
        self.send(b"now give me my key!",newline=False)
        guess=self.recv()
        if bytes.fromhex(guess.decode())[:16]==key:
            f=open("./flag","rb")
            flag=f.read()
            f.close()
            self.send(flag) 
        else:
            self.send(b"sorry")       
            
                
class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 9999
    print("HOST:POST " + HOST+":" + str(PORT))
    server = ForkedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()

