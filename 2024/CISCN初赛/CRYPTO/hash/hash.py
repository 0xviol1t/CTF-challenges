#!/usr/bin/python2
# Python 2.7 (64-bit version)
import os, binascii, hashlib
key = os.urandom(7)
print(key)
print hash(key)
print int(hashlib.sha384(binascii.hexlify(key)).hexdigest(), 16) ^ int(binascii.hexlify(flag), 16)
#7457312583301101235
#13903983817893117249931704406959869971132956255130487015289848690577655239262013033618370827749581909492660806312017
