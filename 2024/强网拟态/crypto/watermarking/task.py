from Crypto.Util.number import *
from Crypto.Cipher import AES
from hashlib import sha256
import socketserver
import signal
import os
import string
import random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.number import getPrime,getStrongPrime
from Crypto.Random import get_random_bytes
from sympy import nextprime





class Task(socketserver.BaseRequestHandler):
    def _recvall(self):
        BUFF_SIZE = 4096
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
        e=3
        maxlens=4096
        RSAparameter=None
        signal.alarm(60)
        watermark=os.urandom(512)
        
        self.send(b"welcome to my proxy encryption program with watermarking")
        messages=[]
        while 1:
            self.send(b"1 for free encrypt with time limit")
            self.send(b"2 for check your watermarking ")
            self.send(b"plz input function code")
            try:
                mode=int(self.recv())
            except:
                self.send(b"plz input right function code")
                continue
            if mode==1:
                if maxlens<=0:
                    self.send(b"sorry, no free chance, try last time~")
                    continue
                self.send(b"now choose your n bitlens")
                self.send(b"1. 1024 2. 2048 3. 4096")
                try:
                    mode=int(self.recv())
                except:
                    self.send(b"plz input right function code")
                    continue
                if mode==1:
                    newparameter=1024
                if mode==2:
                    newparameter=2048
                if mode==3:
                    newparameter=4096
                if newparameter!= RSAparameter:
                        RSAparameter=newparameter
                        p=getStrongPrime(RSAparameter//2)
                        q=getStrongPrime(RSAparameter//2)
                        n=p*q
                        phi=(p-1)*(q-1)
                        self.send(b"your n is changed to")
                        self.send(hex(n).encode())
                try:
                        rsa_key = RSA.construct((n, e))
                        public_key = rsa_key.publickey().export_key()
                        cipher = PKCS1_v1_5.new(RSA.import_key(public_key))
                        self.send(b"plz input your message with hex")
                        message=self.recv().decode()
                        #print(message,len(message))
                        messages.append(message)
                        message=watermark[:RSAparameter//16]+bytes.fromhex(message)
                        #print(message)
                        
                        c = (cipher.encrypt(message)).hex().encode()
                        #print(c)
                        self.send(c)
                        e=nextprime(e)
                        maxlens-=RSAparameter
                except:
                        self.send(b"wrong~ try again")
                        continue
            elif mode==2:
                if maxlens>0:
                    self.send(b"sorry, not even yet~")
                    continue
                self.send(b"now give me your message without free chance")
                e=65537
                d=pow(e,-1,phi)
                rsa_key = RSA.construct((n, e,d))
                public_key = rsa_key.publickey().export_key()
                cipher = PKCS1_v1_5.new(rsa_key)
                
                cts=self.recv().decode()
                cts=bytes.fromhex(cts)
                try:
                    p = (cipher.decrypt(cts,b"bad cipertext"))
                    print(p)    
                except Exception as e:
                    print(e)
                    self.send(b"wrong~ try again")
                    continue    
                if p[:RSAparameter//16]!=watermark[:RSAparameter//16]:
                    self.send(b"not used the watermark!")
                    continue    
                if p[RSAparameter//16:].hex() in messages:
                    self.send(b"not cost!")
                    continue 
                f=open("./flag","rb")
                flag=f.read()
                f.close()       
                self.send(b"cong! your flag is "+flag)        
                                         
                                        
                                
                                                
    
    
                        
                
                
                
        
        self.request.close()


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