import re
import random
from secrets import flag
print(f'Can you weight a 128 bits number in 21 steps')
pattern = r'([AB]|\d+)=([AB]|\d+)(\+|\-|\*|//|<<|>>|&|\^|%)([AB]|\d+)'

command = input().strip()
assert command[-1] == ';'
assert all([re.fullmatch(pattern, i) for i in command[:-1].split(';')])

step = 21
for i in command[:-1].split(';'):
    t = i.translate(str.maketrans('', '', '=AB0123456789'))
    if t in ['>>', '<<', '+', '-', '&', '^']:
        step -= 1
    elif t in ['*', '/', '%']:
        step -= 3
if step < 0:exit()

success = 0
w = lambda x: sum([int(i) for i in list(bin(x)[2:])])
for _ in range(100):
    A = random.randrange(0, 2**128)
    wa = w(A)
    B = 0
    try : exec("global A; global B;" + command)
    except : exit()
    if A == wa:
        success += 1

if success == 100:
    print(flag)