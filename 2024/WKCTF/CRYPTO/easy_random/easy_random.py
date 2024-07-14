import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

flag = b'WKCTF{}'
pad_flag = pad(flag,16)
key = random.randbytes(16)
cipher = AES.new(key,AES.MODE_ECB)
print(cipher.encrypt(pad_flag))
# b'a\x93\xdc\xc3\x90\x0cK\xfa\xfb\x1c\x05$y\x16:\xfc\xf3+\xf8+%\xfe\xf9\x86\xa3\x17i+ab\xca\xb6\xcd\r\xa5\x94\xeaVM\xdeo\xa7\xdf\xa9D\n\x02\xa3'
with open('random.txt','w') as f:
    for i in range(2496):
        f.write(str(random.getrandbits(8))+'\n')

