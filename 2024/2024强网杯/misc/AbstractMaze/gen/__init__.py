import os

modules = [file[:-3] for file in os.listdir('gen') if file.endswith(".py") ]
modules.remove("__init__")
for i in modules:
    exec(f"import gen.{i} as {i}")