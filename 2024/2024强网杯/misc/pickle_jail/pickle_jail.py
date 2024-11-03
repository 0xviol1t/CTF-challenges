#!/usr/local/bin/python
from io import BytesIO
from os import _exit
from pathlib import Path
from pickle import Pickler, Unpickler
from sys import stderr, stdin, stdout
from time import time

from faker import Faker

Faker.seed(time())
fake = Faker("en_US")
flag = Path("flag").read_text()


def print(_):
    stdout.buffer.write(f"{_}\n".encode())
    stdout.buffer.flush()


def input(_=None, limit: int = -1):
    if _:
        print(_)
    _ = stdin.buffer.readline(limit)
    stdin.buffer.flush()
    return _


def bye(_):
    print(_)
    _exit(0)


players = [fake.unique.first_name().encode() for _ in range(50)]
print("Welcome to this jail game!")
print(f"Play this game to get the flag with these players: {players}!")
name = input("So... What's your name?", 300).strip()

assert name not in players, "You are already joined!"

print(f"Welcome {name}!")
players.append(name)

biox = BytesIO()
Pickler(biox).dump(
    (
        name,
        players,
        flag,
    )
)

data = bytearray(biox.getvalue())
num = input("Enter a random number to win: ", 1)[0]
assert num < len(data), "You are not allowed to win!"
data[num] += 1
data[num] %= 0xFF

del name, players, flag
biox.close()
stderr.close()

try:
    safe_dic = {
        "__builtins__": None,
        "n": BytesIO(data),
        "F": type("f", (Unpickler,), {"find_class": lambda *_: "H4cker"}),
    }
    name, players, _ = eval("F(n).load()", safe_dic, {})
    if name in players:
        del _
        print(f"{name} joined this game, but here is no flag!")
except Exception:
    print("What happened? IDK...")
finally:
    bye("Break this jail to get the flag!")
