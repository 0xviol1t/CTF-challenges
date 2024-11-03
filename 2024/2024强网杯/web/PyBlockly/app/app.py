from flask import Flask, request, jsonify
import re
import unidecode
import string
import ast
import sys
import os
import subprocess
import importlib.util
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

blacklist_pattern = r"[!\"#$%&'()*+,-./:;<=>?@[\\\]^_`{|}~]"

def module_exists(module_name):

    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return False

    if module_name in sys.builtin_module_names:
        return True
    
    if spec.origin:
        std_lib_path = os.path.dirname(os.__file__)
        
        if spec.origin.startswith(std_lib_path) and not spec.origin.startswith(os.getcwd()):
            return True
    return False

def verify_secure(m):
    for node in ast.walk(m):
        match type(node):
            case ast.Import:  
                print("ERROR: Banned module ")
                return False
            case ast.ImportFrom: 
                print(f"ERROR: Banned module {node.module}")
                return False
    return True

def check_for_blacklisted_symbols(input_text):
    if re.search(blacklist_pattern, input_text):
        return True
    else:
        return False



def block_to_python(block):
    block_type = block['type']
    code = ''
    
    if block_type == 'print':
        text_block = block['inputs']['TEXT']['block']
        text = block_to_python(text_block)  
        code = f"print({text})"
           
    elif block_type == 'math_number':
        
        if str(block['fields']['NUM']).isdigit():      
            code =  int(block['fields']['NUM']) 
        else:
            code = ''
    elif block_type == 'text':
        if check_for_blacklisted_symbols(block['fields']['TEXT']):
            code = ''
        else:
        
            code =  "'" + unidecode.unidecode(block['fields']['TEXT']) + "'"
    elif block_type == 'max':
        
        a_block = block['inputs']['A']['block']
        b_block = block['inputs']['B']['block']
        a = block_to_python(a_block)  
        b = block_to_python(b_block)
        code =  f"max({a}, {b})"

    elif block_type == 'min':
        a_block = block['inputs']['A']['block']
        b_block = block['inputs']['B']['block']
        a = block_to_python(a_block)
        b = block_to_python(b_block)
        code =  f"min({a}, {b})"

    if 'next' in block:
        
        block = block['next']['block']
        
        code +="\n" + block_to_python(block)+ "\n"
    else:
        return code 
    return code

def json_to_python(blockly_data):
    block = blockly_data['blocks']['blocks'][0]

    python_code = ""
    python_code += block_to_python(block) + "\n"

        
    return python_code

def do(source_code):
    hook_code = '''
def my_audit_hook(event_name, arg):
    blacklist = ["popen", "input", "eval", "exec", "compile", "memoryview"]
    if len(event_name) > 4:
        raise RuntimeError("Too Long!")
    for bad in blacklist:
        if bad in event_name:
            raise RuntimeError("No!")

__import__('sys').addaudithook(my_audit_hook)

'''
    print(source_code)
    code = hook_code + source_code
    tree = compile(source_code, "run.py", 'exec', flags=ast.PyCF_ONLY_AST)
    try:
        if verify_secure(tree):  
            with open("run.py", 'w') as f:
                f.write(code)        
            result = subprocess.run(['python', 'run.py'], stdout=subprocess.PIPE, timeout=5).stdout.decode("utf-8")
            os.remove('run.py')
            return result
        else:
            return "Execution aborted due to security concerns."
    except:
        os.remove('run.py')
        return "Timeout!"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/blockly_json', methods=['POST'])
def blockly_json():
    blockly_data = request.get_data()
    print(type(blockly_data))
    blockly_data = json.loads(blockly_data.decode('utf-8'))
    print(blockly_data)
    try:
        python_code = json_to_python(blockly_data)
        return do(python_code)
    except Exception as e:
        return jsonify({"error": "Error generating Python code", "details": str(e)})
    
if __name__ == '__main__':
    app.run(host = '0.0.0.0')
