import os
from bs4 import BeautifulSoup
import sys
from dataclasses import dataclass
from typing import List

from files import read_forms_from_dir, find_latest_form_dir
from util.operations import contains_no_numbers

@dataclass
class XBRLNode:
	tag: str
	parent: str
	children: List[str]
	val: List[float]
	weight: float
	order: float
	date: str
	text: List[str]
	lineup: List[int]

	def	__init__(self,tag=None,parent=None,children=[],weight=1):
		self.tag = tag
		self.parent = parent
		self.children = children
		self.val = None
		self.weight = None
		self.order = None
		self.date = None
		self.text = None
		self.lineup = None

	def __str__(self):
		children = []
		if self.children != []:
			children = [c for c in self.children]
		
		return (f"{self.tag},\n" + 
				f"	parent = {self.parent}:\n" +
				f"	children = {children},\n" +
				f"	val = {self.val},\n" +
				f"	weight = {self.weight},\n" +
				f"	order = {self.order},\n" +
				f"	date = {self.date},\n" +
				f"	text = {self.text},\n" + 
				f"	line-up = {self.lineup}\n")


	def __repr__(self):
		return str(self)

# Parses xsd file. It will return a list of all the statement URI.
def get_statement_URI(file_xsd:str) -> list:
	statement_roleURI = list()
	soup = BeautifulSoup(file_xsd, "html.parser")
	roleType = soup.find_all("link:roletype")

	# We specifically look for 'Statement' because balance sheet, income statement, and cash flow statement always have 'Statement' in it
	for e in roleType:
		if 'Statement' in e.get_text():
			statement_roleURI.append(e.get('roleuri'))

	assert statement_roleURI != [], "statement roleURI not found"
	return statement_roleURI

# Parses xsd file. It will return a list of all the disclosure URI.
def get_disclosure_URI(file_xsd:str) -> list:
	statement_roleURI = list()
	soup = BeautifulSoup(file_xsd, "html.parser")
	roleType = soup.find_all("link:roletype")

	# We specifically look for 'Statement' because balance sheet, income statement, and cash flow statement always have 'Statement' in it
	for e in roleType:
		if 'Disclosure' in e.get_text():
			statement_roleURI.append(e.get('roleuri'))

	assert statement_roleURI != [], "statement roleURI not found"
	return statement_roleURI

def get_role_path(uri:str) -> str:
	uri_parts = uri.split('/')
	return uri_parts[-1]

# Given the list of URI, we return the URI for balance sheet, income statement, or cash flow
def statement_URI(statement_roleURI:list, statement:str) -> str:
	BS = ['balancesheet','financialposition','financialcondition','consolidatedbalancesheet', 'statementsofcondition']
	IS = ['incomestatement','statementsofoperation','statementsofinccome','statementofincome','statementsofincome',
	   	  'statementsofoperations','consolidatedoperations', 'statementsofearnings']
	CF = ['statementsofcashflows','statementofcashflows','cashflow']
	PPE = ['propertyplantandequipment','propertyandequipment','investmentproperties']
	skip = ['comprehensive','details']
	avoid = ['paranthetical']
	terms = {
		'bs': BS,
		'is': IS,
		'cf': CF,
		'ppe': PPE,
		'skip': skip,
		'avoid': avoid
	}
	# I can keep track of the tables that has alredy been looked at to prevent it from runnin through the same forms multiple times
	# Adding check for numbers because NXST has numbers in URI:
	#	Role_StatementCONSOLIDATEDSTATEMENTSOFOPERATIONSANDCOMPREHENSIVEINCOME -> real one
	#	StatementConsolidatedStatementsOfOperationsAndComprehensiveIncome2 -> fake one

	# first check will skip the skip and avoid terms, and numbers
	for uri in statement_roleURI:
		stipped_uri = get_role_path(uri)
		if any(s in stipped_uri.replace("_", "").replace("-", "").lower() for s in terms['skip']): 
			continue
		if any(s in stipped_uri.replace("_", "").replace("-", "").lower() for s in terms['avoid']): 
			continue
		if not contains_no_numbers(stipped_uri): 
			continue
		if any(b in stipped_uri.replace("_", "").replace("-", "").lower() for b in terms[statement]): 
			return uri

	# second check won't skip the skip terms and skip uri that has numbers
	for uri in statement_roleURI:
		stipped_uri = get_role_path(uri)
		if any(s in stipped_uri.replace("_", "").replace("-", "").lower() for s in terms['avoid']): 
			continue
		if not contains_no_numbers(stipped_uri): 
			continue
		if any(b in stipped_uri.replace("_", "").replace("-", "").lower() for b in terms[statement]): 
			return uri
	
	# final check will look through all but skip numbers
	for uri in statement_roleURI:
		stipped_uri = get_role_path(uri)
		if not contains_no_numbers(uri): 
			continue
		if any(b in stipped_uri.replace("_", "").replace("-", "").lower() for b in terms[statement]): 
			return uri
	
	# final check will look through all
	for uri in statement_roleURI:
		stipped_uri = get_role_path(uri)
		if any(b in stipped_uri.replace("_", "").replace("-", "").lower() for b in terms[statement]): 
			return uri

	print("Statement roleURI not found.")
	assert False, f"{terms[statement]} not found."

# loops throught the string that is split into multiple sections. It will only pick up the tag
def get_tag(ticker:str, full_tag:str) -> str:
	ticker = ticker.lower()
	split = full_tag.split('_')
	tag = None
	for i in range(len(split)):
		# for "us-gaap_tag" format. e.g. us-gaap_CashAndCashEquivalents
		if split[i] == 'us-gaap' or split[i] == ticker:
			tag = split[i]+':'+split[i+1]
			break

		# for "us-gaptag" format. e.g. us-gaapCashAndCashEquivalents
		elif split[i][:7] == 'us-gaap':
			tag = 'us-gaap:'+split[i][7:]
			break
		elif split[i][:len(ticker)] == ticker:
			tag = ticker+':'+split[i][len(ticker):]
			break

	#The xlink:to might be the tag only without the company name.
	# xlink:to="CashAndCashEquivalentsAtCarryingValue"
	if len(split) == 1:
		tag = "us-gaap:"+ split[i]

	# Worst case scenario when we can't parse to get the tag, we will go from back and get the first split[i] that does not contain a number
	# and assume that it is the tag
	if tag is None:
		for i in range(len(split)-1,-1,-1):
			if any(char.isdigit() for char in split[i]):
				continue
			tag = f"{split[i-1]}:{split[i]}"
			break
	
	# Another way we can get the tag is find the index of us-gaap. As long as they are consistent, they will be good.

	if __debug__:
		assert tag is not None, "Could not parse tag. Look into it as it has a wierd way of presenting."
	
	return tag

# Given the file and the the tags to find, it will find all of the tags we want
def soup_get_all_of(file, to_find):
	soup = BeautifulSoup(file, 'html.parser')
	return soup.find_all(to_find)

# Given the Link (presentationLink or calculationLink), the tags to find, and the fs_URI, we return the entire object of fs_URI
def find_all_arc(fs_URI, Link, to_find):
	all_link_arc = None
	for link in Link:
		if link.attrs['xlink:role'] == fs_URI:
			all_link_arc = link.find_all(to_find)
			break
	return all_link_arc

# Given the ticker, it will return the the tag in "us-gaap:tag" or "ticker:tag" format
def get_arc_tag(arc, ticker):
	full_tag = arc.get('xlink:to')
	return get_tag(ticker,full_tag)

# Given the ticker, it will return the the tag in "us-gaap:tag" or "ticker:tag" format of the parent
def get_arc_parent(arc, ticker):
	parent_full_tag = arc.get('xlink:from')
	return get_tag(ticker,parent_full_tag)

def get_pre_tags(ticker, all_presentation_arc, fs_fields):
	for presentation_arc in all_presentation_arc:
		tag = None
    	# getting the tag
		tag = get_arc_tag(presentation_arc, ticker)
		if tag is None: continue

		fs_fields[tag] = XBRLNode(tag)

	return fs_fields

# Given the URI, we go through the pre file and find all the elements in the specified financial statement
# We want this to run first since the order of the tags is proper
# get_parent field will get the parent of the tag if it is set to True. It is False by default. 
def pre_data(ticker:str, file_pre:str, fs_URI:str, fs_fields:dict, get_parent=False) -> list:
	ticker = ticker.lower()
	presentationLink = soup_get_all_of(file_pre, ['link:presentationlink','presentationlink'])
	arcs = ['link:presentationarc','presentationarc']
	all_presentation_arc = find_all_arc(fs_URI, presentationLink, arcs)
	
	assert all_presentation_arc != None, "pre_data not found"

	lineup = 0
	for presentation_arc in all_presentation_arc:
		tag, parent = None, None

    	# getting the tag
		tag = get_arc_tag(presentation_arc, ticker)
		if tag is None: continue
    	# getting the parent
		parent = get_arc_parent(presentation_arc, ticker)

		if tag in fs_fields:
			if fs_fields[tag].parent is None:
				fs_fields[tag].parent = parent
		else:
			fs_fields[tag] = XBRLNode(tag)
			if get_parent:
				fs_fields[tag].parent = parent
		
		fs_fields[tag].lineup = lineup
		lineup += 1
	
	#assert fs_fields != {}, "pre_data parsed no information."
	return fs_fields

# Gets the information from the cal file (order and the weight) and stores it with the tags
# Cal file gives the info for parent, order, and weight
# This might be better to take the presedence over pre_data since cal_data does the parent child relationship better
def cal_data(ticker:str, file_cal:str, fs_URI:str, fs_fields):
	calculationLink = soup_get_all_of(file_cal, ['link:calculationlink','calculationlink'])
	arcs = ['link:calculationarc','calculationarc']
	all_calculation_arc = find_all_arc(fs_URI, calculationLink, arcs)
	
	# Fail case for DELL dell-20220128_cal IS
	if all_calculation_arc is None:
		print("cal data not right. URI might not be loaded right.")
		return fs_fields

	assert all_calculation_arc != None, "cal_data not found"
	for calculation_arc in all_calculation_arc:
		tag, parent = None, None
		# getting the tag
		tag = get_arc_tag(calculation_arc, ticker)
		if tag is None: continue
		# getting the parent
		parent = get_arc_parent(calculation_arc, ticker)

		# if XBRLNode(tag) exists, add the tag to it, else create the node
		if tag not in fs_fields:
			fs_fields[tag] = XBRLNode(tag)
		fs_fields[tag].parent = parent

		# I JUST COMMENTED OUT THE LINE ABOVE AND MADE IT THE ONE BELOW CAUSE FOR MSFT, THE ORDER WAS A HUGE ASS FLOAT
		# LIKE order="10310.00" SO I CHANGED IT.
		if type(calculation_arc.get('order')) is int:
			fs_fields[tag].order = int(calculation_arc.get('order'))
		elif type(calculation_arc.get('order')) is float:
			fs_fields[tag].order = float(calculation_arc.get('order'))
		else:
			# this is done for when type could be str. MRC is an example
			fs_fields[tag].order = float(calculation_arc.get('order'))

		fs_fields[tag].weight = float(calculation_arc.get('weight'))

	return fs_fields

def tags_without_parent(fs_fields):
	skip = ['Items','Axis','Member','Domain','Table','Abstract']
	no_parent_tags = []
	for tag in fs_fields:
		xbrl_node = fs_fields[tag]
		if xbrl_node.parent is None and not any(s in tag for s in skip):
			no_parent_tags.append(tag)
	return no_parent_tags

# If a tag has no parent tag from the first run, we will run through the entire cal file and see if we can find the tag. 
# The criteria to get the tag's parent is checking if that parent tag we find is within the elements we know that are in the fs.
def cal_data_again(ticker:str, file_cal:str, fs_URI:str, fs, fs_fields, no_parent_tags):
	BS = ['balancesheet','financialposition','financialcondition']
	IS = ['incomestatement','statementsofoperation','statementsofinccome','statementofincome','statementsofincome','statementsofoperations','consolidatedoperations']
	CF = ['statementsofcashflows','statementofcashflows','cashflow']
	terms = {
		'bs': BS,
		'is': IS,
		'cf': CF,
	}

	potential_URI = []
	calculationLink = soup_get_all_of(file_cal, ['link:calculationlink','calculationlink'])
	for link in calculationLink:
		if link is None: continue

		role_URI = link.attrs['xlink:role'].replace("_", "").replace("-", "").lower()
		if any(b in role_URI for b in terms[fs]): 
			if role_URI != fs_URI:
				potential_URI.append(link)
				
	# First we look through the roleURI that might be more similar to the fs
	for link in potential_URI:
		all_calculation_arc = link.find_all(['link:calculationarc','calculationarc'])
		if all_calculation_arc is None: continue

		for calculation_arc in all_calculation_arc:
			tag = get_arc_tag(calculation_arc, ticker)
			if tag is None or tag not in no_parent_tags:
				continue
			parent = get_arc_parent(calculation_arc, ticker)
			
			if parent in fs_fields:
				fs_fields[tag].parent = parent
				fs_fields[tag].weight = float(calculation_arc.get('weight'))
				try:
					fs_fields[tag].order = fs_fields[parent].order + 1.0
				except:
					fs_fields[tag].order = None
	
	# We will check again if all tags are filled and if not, we will run through all roleURI
	no_parent_tags = tags_without_parent(fs_fields)
	if no_parent_tags != []:
		for link in calculationLink:
			all_calculation_arc = link.find_all(['link:calculationarc','calculationarc'])
			if all_calculation_arc is None: continue

			for calculation_arc in all_calculation_arc:
				tag = get_arc_tag(calculation_arc, ticker)
				if tag is None or tag not in no_parent_tags:
					continue
				parent = get_arc_parent(calculation_arc, ticker)
				
				if parent in fs_fields:
					fs_fields[tag].parent = parent
					fs_fields[tag].weight = float(calculation_arc.get('weight'))

					try:
						fs_fields[tag].order = fs_fields[parent].order + 1.0
					except:
						fs_fields[tag].order = None

	return fs_fields

def get_fs_fields(ticker:str, fs, cfiles):
	statement_roleURI = get_statement_URI(cfiles.xsd)
	fs_URI = statement_URI(statement_roleURI, fs)
	fs_fields = {}
	fs_fields = pre_data(ticker, cfiles.pre, fs_URI, fs_fields)
	fs_fields = cal_data(ticker, cfiles.cal, fs_URI, fs_fields)

	no_parent_tags = tags_without_parent(fs_fields)
	if no_parent_tags != []:
		cal_data_again(ticker, cfiles.cal, fs_URI, fs, fs_fields, no_parent_tags)
	fs_fields = pre_data(ticker, cfiles.pre, fs_URI, fs_fields, True)

	assert fs_fields != {}, "fs_fields is empty"
	return fs_fields

def get_disclosure_fields(ticker:str, disclosure, cfiles):
	statement_roleURI = get_disclosure_URI(cfiles.xsd)	
	fs_URI = statement_URI(statement_roleURI, disclosure)
	
	assert fs_fields != {}, "fs_fields is empty"
	return fs_fields

def get_common_shares_outstanding(htm_xml):
	soup = BeautifulSoup(htm_xml, "xml")
	sharesOutstanding = soup.find("dei:EntityCommonStockSharesOutstanding")
	return sharesOutstanding.get_text()

if __name__ == "__main__":
	ticker = sys.argv[1]
	form_type = sys.argv[2]
	directory = find_latest_form_dir(ticker,form_type)
	
	cfiles = read_forms_from_dir(directory)

	fs = 'bs'
	fs_fields = get_fs_fields(ticker, fs, cfiles)

	for key in fs_fields:
		print(fs_fields[key])
		print()


