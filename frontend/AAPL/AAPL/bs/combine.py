import json
import os

files = filter(lambda x: "json" in x, os.listdir())

out = {}
for f in files:
    date = f.split(".")[0].split("_")[2]
    with open(f) as file:
        data = json.loads(file.read())

    out[date] = data

with open("AAPL-combined", "w") as f:
    f.write(json.dumps(out, indent=4))
