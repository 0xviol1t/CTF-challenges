from flask import Flask, render_template, request, jsonify
from Crypto.Cipher import AES
import os
from string import printable
app = Flask(__name__)

# 初始化全局变量
def initialize_globals():
    global key, iv,register_open, login_attempts
    key = os.urandom(16)
    iv  = os.urandom(16)
    register_open = True
    login_attempts = 500

initialize_globals()

def encrypt(data, key):
    #iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    ct_bytes = cipher.encrypt(data.encode('utf-8'))
    return ct_bytes.hex()

def decrypt(ct, key):
    ct_bytes = bytes.fromhex(ct)
    #iv = ct_bytes[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    data = cipher.decrypt(ct_bytes[:])
    #print("data:",data)
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    global register_open, login_attempts
    message = ""
    
    if request.method in  ['POST']:
        if request.is_json:
            data = request.get_json()
            action = data.get('action')
            
            if action == 'register':
                if not register_open:
                    message = "Registration function is closed"
                else:
                    username = data.get('username')
                    password = data.get('password')
                    if len(password)<8:
                    	message = "Registration failed, password too short"
                    elif not set(password+username)<=set(printable):
                        message = "Registration failed, illegal character"
                    elif 'admin' in username:
                        message = "Registration failed, you are not an admin"
                    else:
                        token = encrypt(f"{username}\x00{password}\x01\x02\x03", key)
                        register_open = False
                        message = f"Please save your token: {token}"
            
            elif action == 'login':
                if login_attempts <= 0:
                    message = "Too many attempts"
                else:
                    username = data.get('username').encode()
                    password = data.get('password').encode()
                    token = data.get('token')
                    
                    try:
                        decrypted = decrypt(token, key)
                        #print(decrypted)
                        token_username, *_, token_password = decrypted.split(b'\x00')
                        #print(token_username,",",token_password)
                        assert(token_password[-3:]==b"\x01\x02\x03")
                        token_password=token_password[:-3]
                        if username == token_username and password == token_password:
                            if username == b'admin':
                                #print(token_password)
                                if password == b'123456':
                                    f=open("./flag","r")
                                    flag=f.read()
                                    #print(flag)
                                    f.close()
                                    message = "You have logged in with admin privileges, here is your flag: "+flag
                                else:
                                    message = "Admin login failed, please try again"
                            else:
                                message = "You have logged in as a regular user"
                        else:
                            message = "Login failed, please try again"
                    except:
                        message = "Login wrong, please try again"
                    finally:
                        login_attempts -= 1
            
            elif action == 'restart':
                initialize_globals()
                message = "System has been restarted. AES key and function counts have been reset."
        else:
            message = "Unsupported Media Type: Content-Type must be application/json"
    
        return jsonify({'message': message})
    return render_template('index.html', message=message)    

if __name__ == '__main__':
    app.run(host="0.0.0.0")
