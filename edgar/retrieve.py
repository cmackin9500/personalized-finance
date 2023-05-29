#!/usr/bin/env python3
# Retrieval for XBRL from EDGAR

import requests
from urllib.request import urlopen, Request
from zipfile import ZipFile
from io import BytesIO
import json
import enum
import os
from dataclasses import dataclass
import sys

from util import retreival as re

FORM_MAP = {
		"10-K": [
			"10-K",
			"FORM 10-K",
			"ANNUAL REPORT"
			],
		"10-Q": [
			"10-Q",
			"FORM 10-Q"
			]
		}


BASE_HEADERS = {
	"user-agent": "OVERMAC cale.overstreet@gmail.com",
	"origin": "https://efts.sec.gov"
	}

# Uses EDGAR API to get the CIK for company lookup
# Kind of jank since it uses the method for a text field on the site
def get_company_CIK(ticker:str):
	url = "https://efts.sec.gov/LATEST/search-index"
	res = requests.post(url, headers=BASE_HEADERS, json={"keysTyped": ticker})
	hits = res.json()["hits"]["hits"]
	
	if len(hits) < 1:
		raise Exception("EDGAR returned not hits for symbol \"{}\"".format(ticker))

	return hits[0]["_id"]

# Standard CIK format
# 10 characters
def pad_CIK(CIK:str):
	return "0" * (10 - len(CIK)) + CIK

# Check if any string is equivalent to a target phrase
def str_cmp_mlt(buf, words):
	for word in words:
		if word == buf:
			return True

	return False

# Checks if any of multiple strings starts with a phrase
def str_startswith_mlt(buf, words):
	for word in words:
		if buf.startswith(word):
			return True

	return False

# Retrieves all filings for a company
def get_recent_filings(CIK:str):
	CIK = pad_CIK(CIK) 
	url = f"https://data.sec.gov/submissions/CIK{CIK}.json"
	res_json = json.loads(requests.get(url, headers=BASE_HEADERS).text)

	recent = res_json["filings"]["recent"]
	return recent

def get_older_filings(CIK:str):
	CIK = pad_CIK(CIK)
	url = f"https://data.sec.gov/submissions/CIK{CIK}-submissions-001.json"
	return json.loads(requests.get(url, headers=BASE_HEADERS).text)

# Key info for company filings
@dataclass
class FormInfo:
	accessionNumber: str
	filingDate: str
	reportDate: str
	form: str
	isXBRL: bool
	isInlineXBRL: bool
	primaryDocument: str
	primaryDocDescription: str

# Goes through retrieved filings to find forms of a type
def get_forms_of_type(master, form_type:str):
	form_names = FORM_MAP[form_type]

	accessionNumber = master['accessionNumber']
	filingDate = master['filingDate']
	reportDate = master['reportDate']
	form = master['form']
	isXBRL = master['isXBRL']
	isInlineXBRL = master['isInlineXBRL']
	primaryDocument = master['primaryDocument']
	primaryDocDescription = master['primaryDocDescription']

	forms = []
	for i, name in enumerate(primaryDocDescription):
		if str_cmp_mlt(name, form_names):
			forms.append(FormInfo(
									accessionNumber[i],
									filingDate[i],
									reportDate[i],
									form[i],
									isXBRL[i],
									isInlineXBRL[i],
									primaryDocument[i],
									primaryDocDescription[i]
								)
						)
	return forms

# Target URL for inline HTML
def create_inline_html_url(ticker, CIK, form):
	return "https://www.sec.gov/Archives/edgar/data/{}/{}/{}".format(CIK, form.accessionNumber.replace("-", ""), form.primaryDocument)

# Target URL for instance data
def create_xbrl_inst_url(CIK, form):
	return "https://www.sec.gov/Archives/edgar/data/{}/{}/{}".format(CIK, form.accessionNumber.replace("-", ""), form.accessionNumber + "-xbrl.zip")

# Target URL for facts data
# Not used
def create_facts_url(CIK):
	return "https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json".format(pad_CIK(CIK))

def create_tags_url(CIK):
	return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

# Creates the data directory based on the convention
# ticker/form_type/form_date
def dest_dir_name(ticker, form_type, form):
	return f"forms/{ticker}/{form_type}/{form.reportDate}"

def save_form_data(ticker, form_type, date):
	CIK = get_company_CIK(ticker)
	forms = get_forms_of_type(get_recent_filings(CIK), form_type)

	form = None
	for f in forms:
		if f.date == date:
			form = f

	if form == None:
		raise Exception("Invalid form specified")

	dest_dir = dest_dir_name(ticker, form_type, form)
	if os.path.isdir(dest_dir):
		print("The specified form data is already downloaded. Ignoring download")
		return dest_dir

	mkdir_if_NE(dest_dir)
	print("Saving files in dir \"{}\"".format(dest_dir))

	# Create url for inline HTML
	htmlurl = create_inline_html_url(ticker, CIK, form)
	xbrlurl = create_xbrl_inst_url(CIK, form)
	factsurl = create_facts_url(CIK)
	tagsurl = create_tags_url(CIK)


	# Retrieve XBRL instance
	print("Retrieving XBRL instance (zipfile) from:\n\t{}".format(xbrlurl))
	get_and_extract_zip(xbrlurl, dest_dir)

	# Retrieve inline HTML
	print("Retrieving inline HTML from:\n\t{}".format(htmlurl))
	html_fullpath = dest_dir + "/{}_{}.html".format(ticker, form.date)
	htmltext = requests.get(htmlurl, headers=BASE_HEADERS).text
	write_file(html_fullpath, htmltext) 

	re.remove_extra_files(dest_dir)

	return dest_dir

def save_data_from_index(ticker, CIK, form, form_type):
	htmlurl = create_inline_html_url(ticker, CIK, form)
	xbrlurl = create_xbrl_inst_url(CIK, form)

	dest_dir = dest_dir_name(ticker, form_type, form)
	re.mkdir_if_NE(dest_dir)

	print(f"{ticker} {form_type}: {form.reportDate}")
	print("    Saving files in dir \"{}\"".format(dest_dir))

	# Retrieve XBRL instance
	print("    Retrieving XBRL instance (zipfile) from:\n\t{}".format(xbrlurl))
	try:
		re.get_and_extract_zip(xbrlurl, dest_dir)
	except:
		print('    XBRL does not exist for the year.')

	# Retrieve inline HTML
	print("    Retrieving inline HTML from:\n\t{}".format(htmlurl))
	html_fullpath = dest_dir + f"/{ticker}_{form.reportDate}.html"

	try:
		htmltext = requests.get(htmlurl, headers=BASE_HEADERS).text
		re.write_file(html_fullpath, htmltext) 
	except:
		print('    Cannot retrieve HTML.')
	re.remove_extra_files(dest_dir)

	return dest_dir

def get_forms_of_type_xbrl(CIK, form_type):
	recent_filings = get_recent_filings(CIK)
	older_filings = get_older_filings(CIK)
	forms = get_forms_of_type(recent_filings,form_type) + get_forms_of_type(older_filings,form_type)
	
	forms_xbrl = []
	for form in forms:
		if form.isXBRL:
			forms_xbrl.append(form)

	return forms_xbrl

def save_all_forms(ticker, form_type, forms):
	CIK = get_company_CIK(ticker)
	
	for form in forms:
		save_data_from_index(ticker, CIK, form, form_type)


def save_all_facts(ticker):
	CIK = get_company_CIK(ticker)
	factsurl = create_facts_url(CIK)
	print(f"Retrieving json instance from:\n\t{factsurl}")
	res = requests.get(factsurl, headers=BASE_HEADERS, stream=True)
	download_file(res,ticker)


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("USAGE: python3 omretrieve.py <ticker> <form type>")
		print("\tex. python3 omretrive.py AAPL 10-K")
		sys.exit(0)

	ticker = sys.argv[1]
	form_type = sys.argv[2]
	CIK = get_company_CIK(ticker)
	forms = get_forms_of_type_xbrl(CIK, form_type)
	save_all_forms(ticker, form_type, forms)
