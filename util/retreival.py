#!/usr/bin/env python3
# Retrieval for XBRL from EDGAR

import requests
from zipfile import ZipFile
from io import BytesIO
import json
import os


BASE_HEADERS = {
	"user-agent": "OVERMAC cale.overstreet@gmail.com",
	"origin": "https://efts.sec.gov"
	}

def get_and_extract_zip(url, dest):
	res = requests.get(url, headers=BASE_HEADERS, stream=True)
	zipfile = ZipFile(BytesIO(res.raw.read()))
	zipfile.extractall(path=dest)

# Creates the data directory based on the convention
# ticker/form_type/form_date
def dest_dir_name(ticker, form_type, form):
	return "forms/{}/{}/{}".format(ticker, form_type, form.date)

# Makes a directory if it doesn't exist
def mkdir_if_NE(pathname):
	if not os.path.isdir(pathname):
		os.makedirs(pathname)

# Standard write file function
def write_file(filename, data):
	with open(filename, "w") as f:
		f.write(data)

# Removes unecessary files from download
def remove_extra_files(dirname):
	files = os.listdir(dirname)
	for file in files:
		if not file.endswith(".html")\
				and not file.endswith(".xml")\
				and not file.endswith(".xsd"):
			os.remove(dirname + "/" + file)