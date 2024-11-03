# -*- coding: utf-8 -*-

from hashlib import sha256
import gen
from Cstrategy import S0, S1, S2, S3, S4, S5, S6
from termcolor import *
import random, string, base64, os
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')

WALL = '@@'
EMPTY = '  '
# ROAD = '⭐'
ROAD = '* '


def printMap(mmap, path=[], badpath=[]):
    ss = '   '
    print(f"{len(path) = }, {len(badpath) = }")
    h = len(mmap)
    w = len(mmap[0])
    for x in range(h):
        ss += os.linesep
        for y in range(w):
            if (x, y) in path:
                assert mmap[x][y] == 0
                ss += colored(ROAD, 'green')
            elif (x, y) in badpath:
                assert mmap[x][y] == 0
                ss += colored(ROAD, 'red')
            else:
                ss += [EMPTY, WALL][mmap[x][y]]
    print(ss)


def PoW():
    ab = string.ascii_letters + string.digits
    nonce1 = "".join(random.choices(ab, k=8))
    nonce2 = "".join(random.choices(ab, k=4))
    print(f"{nonce1 = }") 
    print(f"{sha256(nonce1.encode() + nonce2.encode()).hexdigest() = }")
    # print(nonce2)
    p = input(f"Give me nonce2:\n> ").strip()
    return p == nonce2


def parseMap(m, shape):
    try:
        s = []
        m = base64.b64decode(str(m).encode()).decode().replace('\r','')
        lines = m.split('\n')
        for line in lines:
            assert set(line) <= set('01'), f"Unknow char: {set(line)}"
            assert line[0] == line[-1] == '1', "Left/Right Wall error"
            s.append(list(map(int, line)))
        
        assert len(set([len(i) for i in s])) == 1, "Not uniformed width"
        assert len(s) == shape[0] and len(s[0]) == shape[1], "Size error"
        assert set(s[0]) ==  set(s[-1]) == set([1]), "Up/Down Wall error"
        assert s[-2][-2] == 0, "Where is the EXIT????"
        return s
    except Exception as e:
        print(e)
        return None


def getMap(w, h):
    userMap = input("Please Give me a map in base64:\n> ").strip()
    userMap = parseMap(userMap, (w, h))
    if not userMap:
        print("Map error")
        return None

    print("Your map:")
    printMap(userMap)
    return userMap


def challenge1():
    mapp = getMap(49, 49)
    if not mapp:
        return False
    solver = S1(mapp)
    p, _ = solver.chaPanda()
    printMap(mapp, p)
    return bool(p)


def challenge2():
    mapp = getMap(49, 49)
    if not mapp:
        return False
    solver1 = S1(mapp)
    solver2 = S0(mapp)
    p1, _ = solver1.chaPanda()
    p2, bp = solver2.chaPanda()
    printMap(mapp, p1)
    printMap(mapp, p2, bp)
    return p1 == p2 and len(bp) > 0.6 * len(mapp) * len(mapp[1])


def challenge3():
    mapp = getMap(49, 49)
    if not mapp:
        return False
    solver = S0(mapp)
    p, bp = solver.chaPanda()
    printMap(mapp, p)
    return len(p) >= 1495


def challenge4():
    mapp = getMap(49, 49)
    if not mapp:
        return False
    sol1 = S3(mapp)
    sol2 = S4(mapp)
    p1, _ = sol1.chaPanda(24, 24)
    p2, _ = sol2.chaPanda(24, 24)
    if not p1 or not p2:
        return False
    printMap(mapp, p1)
    printMap(mapp, p2)
    return len(p1) <= 50 and (len(p2)-1595)/16 + 0.5 >= random.random()


def challenge5():
    mapp = getMap(49, 49)
    if not mapp:
        return False
    sol1 = S0(mapp)
    sol2 = S6(mapp)
    p1, _ = sol1.chaPanda()
    p2, _ = sol2.chaPanda()
    printMap(mapp, p1)
    printMap(mapp, p2)
    return len(p1) <= 142 and len(p2) >= 2210 and len(set(p2))/(49*49) < 0.5


if __name__ == "__main__":

    if PoW():
        challenges = [
            challenge1,
            challenge2,
            challenge3,
            challenge4,
            challenge5
        ]
        for c in challenges:
            print(f"{c.__name__}: ")
            if not c():
                print(f"{c.__name__} Failed")
                break
        else:
            print("Congratulation!!!")
            print("This is your flag:")
            print("flag{5d29a2a9-8701-11ef-9c7b-596965fcb465}")
