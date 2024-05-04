import sys
import os

DEBUG_MODE = os.environ["OVERMAC_DEBUG"] if "OVERMAC_DEBUG" in os.environ else None
print(DEBUG_MODE)

# ==================== DEBUG TOOLS ====================
def oprint(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
	if not DEBUG_MODE: return None

	print("\033[0;34m", end="")
	print(*objects, sep=sep, end=end, file=file, flush=flush)
	print("\033[0m", end="")
	return None

# ==================== END DEBUG TOOLS ====================


# ==================== FILE OPERATIONS ====================

def read_file(filename):
	with open(filename) as f:
		return f.read()

def write_file(filename, data):
	with open(filename, "w") as f:
		f.write(data)

# ==================== END FILE OPERATIONS ====================
