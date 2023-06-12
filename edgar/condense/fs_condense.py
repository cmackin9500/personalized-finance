import os
import sys
import json

def create(fs):
	skip = ['Items','Axis','Member','Domain','Table','Abstract']
	with open(f"./hashmap/{fs}_hashmap.json", 'r') as f:
		data = f.read()
	fs_tags = json.loads(data)
	
	out = {}
	for tag in fs_tags:
		if any(tag.endswith(end) for end in skip):
			continue

		con = fs_tags[tag]
		if con not in out:
			out[con] = [tag]
		else:
			out[con].append(tag)

	with open(f"{fs}_condense.json", 'w') as f:
		json.dump(out, f, indent=4)

if __name__ == "__main__":
	fs = sys.argv[1]
	create(fs)
