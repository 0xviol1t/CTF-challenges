#! /usr/bin/env python3

import os
import binascii
from random import random

from flask import request
import json
from libnum import n2s, s2n
from secret import flag, K_as, K_bs
from flask import Flask
from hashlib import md5
import time
from Crypto.Cipher import AES
from os import urandom

# from rpc.restful_service import TodoList, Todo, Datatype_es, Datatype_byte, Datatype_classify
# from rpc.rpc_service import *

app = Flask(__name__)

flag += '\x00' * (- len(flag) % 16)

# from gevent.pywsgi import WSGIServer
A = md5(b'A').hexdigest()[:16]
B = md5(b'B').hexdigest()[:16]
S = md5(b'S').hexdigest()[:16]
K_sc = {A: K_as, B: K_bs}
name2hex = {"A": A, "B": B, "S": S}
# tokens = json.loads(open('token.txt', 'r').read())
hex_chars = set(list('0123456789abcdefg'))

last_time = time.time()

history = {}
keys = {}
if os.path.exists('keys.txt'):
    try:
        keys = json.loads(open('keys.txt', 'r').read())
    except Exception as e:
        keys = {}
        print(e)

if os.path.exists('K_sc.txt'):
    tag = 0
    cur_sc = {}
    try:
        cur_sc = json.loads(open("K_sc.txt", 'r').read())
        tag = 1
    except Exception as e:
        tag = 0
        print(e)
    if tag:
        K_sc.update(cur_sc)


def update_keys(cur_token, left, right, cur_key):
    global keys
    if cur_token not in keys:
        keys[cur_token] = {left: {right: cur_key}}
    else:
        cur_dict = keys[cur_token]
        if left not in cur_dict:
            cur_dict[left] = {right: cur_key}
        else:
            cur_dict[left][right] = cur_key
    cur_time = time.time()
    global last_time
    if cur_time - last_time > 666:
        open('keys.txt', 'w').write(json.dumps(keys))
        last_time = cur_time
    return True


def check_fresh(t):
    cur = time.time()
    # if t > cur:
    #     return False
    if cur - t > 24:
        return False
    return True


def get_token(args):
    cur_token = args.get('token', None)
    if cur_token is None:
        return False, {"message": "Add your Token"}
    cur_token = cur_token.ljust(16, '0')[:16]
    for char in cur_token:
        if char not in hex_chars:
            return False, {"message": "Your token should be made of hex"}
    return True, cur_token


def add_to_history(cur_log, cur_token):
    global history
    if cur_token in history:
        history[cur_token].append(cur_log)
    else:
        history[cur_token] = [cur_log]


def dec_and_split_message(cli, message, need_hex=False):
    message = binascii.unhexlify(message)
    scheme = AES.new(binascii.unhexlify(K_sc[cli]), AES.MODE_ECB)
    message = scheme.decrypt(message)
    if need_hex:
        t, target, cur_key = int(message[:16].hex(), 16), message[16: 24].hex(), message[32: 48].hex()
    else:
        t, target, cur_key = int(message[:16].hex(), 16), message[16: 24], message[32: 48]
    return t, target, cur_key


def send_to_client(cur_token, target, message):  # all of the inputs are hex
    if not len(message) == 16 * 3 * 2:
        return "Your message is not valid"
    cur_log = f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: S -> {target}: {message}'
    add_to_history(cur_log, cur_token)
    t, friend, cur_key = dec_and_split_message(target, message, need_hex=True)
    if not check_fresh(t):
        return "This is an old message, get out"
    return update_keys(cur_token, target, friend, cur_key)


def send_to_server(cur_token, orig_message):
    if not len(orig_message) == 16 * 3 * 2 + 16:
        return "Your message is not valid"
    sender, message = orig_message[0: 16], orig_message[16:]
    t, target, cur_key = dec_and_split_message(sender, message)
    if not check_fresh(t):
        return "This is an old message, get out"

    cur_log = f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: {sender} -> S: {orig_message}'
    add_to_history(cur_log, cur_token)
    suffix = os.urandom(8)
    wait_to_send_m = n2s(int(time.time())).rjust(16, b'0') + binascii.unhexlify(sender) + suffix + cur_key
    target = target.hex()
    scheme = AES.new(binascii.unhexlify(K_sc[target]), AES.MODE_ECB)
    cipher = scheme.encrypt(wait_to_send_m).hex()
    send_to_client(cur_token, target, cipher)
    return True


def send_message(cur_token, target, message):
    if target == S:
        return send_to_server(cur_token, message)
    else:
        return send_to_client(cur_token, target, message)


def exchange_key(cur_token):
    k_ab = os.urandom(16)
    if random() > 0.5:
        sender = A
        target = B
    else:
        sender = B
        target = A
    suffix = os.urandom(8)
    message = n2s(int(time.time())).rjust(16, b'0') + binascii.unhexlify(target) + suffix + k_ab
    scheme = AES.new(binascii.unhexlify(K_sc[sender]), AES.MODE_ECB)
    cipher = scheme.encrypt(message).hex()
    message = sender + cipher
    ans = send_message(cur_token, S, message)
    if ans is not True:
        return ans
    update_keys(cur_token, sender, target, k_ab.hex())
    return {'message': 'A and B have completed key exchange!'}


@app.route('/A_and_B', methods=['GET'])
def index():
    # predict_impl = predict.predict(rows_limit=10000, version=0.02, debug=1)
    # predict_impl.get_data()
    # predict_impl.read_origin_table(0)
    bol, message = get_token(request.args)
    if not bol:
        return {"message": message}
    cur_token = message
    return exchange_key(cur_token)


@app.route('/register', methods=['GET'])  # get token and
def register():
    # cur_token = os.urandom(16).hex()
    bol, message = get_token(request.args)
    if not bol:
        return {"message": message}
    cur_token = message
    if cur_token in K_sc:
        cur_key = binascii.unhexlify(K_sc[cur_token])
    else:
        cur_key = os.urandom(16)
        K_sc[cur_token] = cur_key.hex()
    cur_time = time.time()
    global last_time
    if cur_time - last_time > 666:
        open("K_sc.txt", 'w').write(json.dumps(K_sc))
        last_time = cur_time
    return {'token': cur_token, 'key_to_server': cur_key.hex()}


@app.route('/send_message', methods=['GET'])
def execute_protocol():
    bol, message = get_token(request.args)
    if not bol:
        return {"message": message}
    cur_token = message
    target = request.args.get('to')
    message = request.args.get('message')
    send_message(cur_token, name2hex[target], message)
    return {"message": f"You have sent {message} to {target}"}


@app.route('/view_history', methods=['GET'])
def list_history():
    bol, message = get_token(request.args)
    if not bol:
        return {"message": message}
    cur_token = message
    if cur_token not in history:
        return {"message": "Invalid token or this token has not generated any histories."}
    cur_histories = history[cur_token]
    return_histories = cur_histories[0:]
    return_histories.reverse()

    return {"history": return_histories}


@app.route('/send_flag', methods=['GET'])
def send_flag():
    bol, message = get_token(request.args)
    if not bol:
        return {"message": message}
    cur_token = message
    if random() > 0.5:
        sender = A
        target = B
    else:
        sender = B
        target = A
    if keys[cur_token][sender][target] != keys[cur_token][target][sender]:
        exchange_key(cur_token)
        return {"message": "Keys between A and B are different! There must be something malicious in our system!"}
    cur_key = binascii.unhexlify(keys[cur_token][sender][target])
    scheme = AES.new(cur_key, AES.MODE_ECB)
    cipher = scheme.encrypt(flag.encode()).hex()
    cur_log = f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: {sender} -> {target}: {cipher}'
    add_to_history(cur_log, cur_token)
    return {"message": f'{sender} has sent flag secretly to {target}!'}


if __name__ == '__main__':
    # app.run()
    # app.run(host='0.0.0.0', port=os.environ.get("PORT0"))
    app.run(host='0.0.0.0', port=12138, debug=True)
