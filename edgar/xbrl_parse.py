import os
from bs4 import BeautifulSoup
import sys
from dataclasses import dataclass

from files import read_forms_from_dir, find_latest_form_dir

@dataclass
class XBRLNode:
	tag: str
	parent: str
	child: list
	val: float
	weight: float
	order: float
	date: str
	text: str

	def	__init__(self,tag=None,parent=None,child=[],weight=1):
		self.tag = tag
		self.parent = parent
		self.child = child
		self.val = None
		self.weight = None
		self.order = None
		self.date = None
		self.text = None

	def __str__(self):
		child = []
		if self.child != []:
			child = [c for c in self.child]
		
		return (f"{self.tag},\n" + 
				f"	parent = {self.parent}:\n" +
				f"	child = {child},\n" +
				f"	val = {self.val},\n" +
				f"	weight = {self.weight},\n" +
				f"	order = {self.order},\n" +
				f"	date = {self.date},\n" +
				f"	text = {self.text}\n")


	def __repr__(self):
		return str(self)

# Parses xsd file. It will return a list of all the statement URI.
def get_URI(file_xsd:str) -> list:
	roleURI = list()
	soup = BeautifulSoup(file_xsd, "html.parser")
	roleType = soup.find_all("link:roletype")

	# We specifically look for 'Statement' because balance sheet, income statement, and cash flow statement always have 'Statement' in it
	for e in roleType:
		if 'Statement' in e.get_text():
			roleURI.append(e.get('roleuri'))
	return roleURI

def URI_from_statement(roleURI:str, statement:str) -> str:
	for uri in roleURI:
		if any(s in uri.lower() for s in skip):
			continue
		if any(b in uri.lower() for b in BS):
			return uri
	for uri in roleURI:
		if any(b in uri.lower() for b in BS):
			return uri

# Given the list of URI, we return the URI for balance sheet, income statement, or cash flow
def statement_URI(roleURI:list, statement:str) -> str:
	BS = ['balancesheet','financialposition','financialcondition','consolidatedbalancesheet']
	IS = ['incomestatement','statementsofoperation','statementsofinccome','statementofincome','statementsofincome','statementsofoperations','consolidatedoperations']
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

	# first check will skip the skip and avoid terms
	for uri in roleURI:
		if any(s in uri.replace("_", "").replace("-", "").lower() for s in terms['skip']): 
			continue
		if any(s in uri.replace("_", "").replace("-", "").lower() for s in terms['avoid']): 
			continue
		if any(b in uri.replace("_", "").replace("-", "").lower() for b in terms[statement]): 
			return uri

	# second check won't skip the skip terms
	for uri in roleURI:
		if any(s in uri.replace("_", "").replace("-", "").lower() for s in terms['avoid']): 
			continue
		if any(b in uri.replace("_", "").replace("-", "").lower() for b in terms[statement]): 
			return uri
	
	# final check will look through all
	for uri in roleURI:
		if any(b in uri.replace("_", "").replace("-", "").lower() for b in terms[statement]): 
			return uri


# loops throught the string that is split into multiple sections. It will only pick up the tag
def get_tag(ticker:str, full_tag:str) -> str:
	ticker = ticker.lower()
	split = full_tag.split('_')
	tag = None
	for i in range(len(split)):
		if split[i] == 'us-gaap' or split[i] == ticker:
			tag = split[i]+':'+split[i+1]
			break
		elif split[i][:7] == 'us-gaap':
			tag = 'us-gaap:'+[i][7:]
			break
		elif split[i][:len(ticker)] == ticker:
			tag = ticker+':'+split[i][len(ticker):]
			break
	return tag

# Given the URI, we go through the pre file and find all the elements in the specified financial statement
# We want this to run first since the order of the tags is proper
def pre_data(ticker:str, file_pre:str, fs_URI:str, fs_fields:dict) -> list:
	ticker = ticker.lower()
	soup = BeautifulSoup(file_pre, 'html.parser')
	presentationLink = soup.find_all(['link:presentationlink','presentationlink'])
	all_presentation_arc = None

	for link in presentationLink:
		if link.attrs['xlink:role'] == fs_URI:
			all_presentation_arc = link.find_all(['link:presentationarc','presentationarc'])
	
	assert all_presentation_arc != None, "pre_data not found"

	for presentation_arc in all_presentation_arc:
		tag, parent = None, None

    	# getting the tag
		full_tag = presentation_arc.get('xlink:to')
		tag = get_tag(ticker,full_tag)

    	# getting the parent
		parent_full_tag = presentation_arc.get('xlink:from')
		parent = get_tag(ticker,parent_full_tag)

		if tag is not None:
			if tag in fs_fields:
				if fs_fields[tag].parent is None:
					fs_fields[tag].parent = parent
			else:
				fs_fields[tag] = XBRLNode(tag)
				fs_fields[tag].parent = parent

	return fs_fields


# Gets the information from the cal file (order and the weight) and stores it with the tags
# Cal file gives the info for parent, order, and weight
# This might be better to take the presedence over pre_data since cal_data does the parent child relationship better
def cal_data(ticker:str, file_cal:str, fs_URI:str, fs_fields):
	soup = BeautifulSoup(file_cal, 'html.parser')
	calculationLink = soup.find_all(['link:calculationlink','calculationlink'])

	for link in calculationLink:
		all_calculation_arc = None
		if link.attrs['xlink:role'] in fs_URI:
			all_calculation_arc = link.find_all(['link:calculationarc','calculationarc'])

		if all_calculation_arc is None: continue
		for calculation_arc in all_calculation_arc:
			full_tag = calculation_arc.get('xlink:to')
			tag = get_tag(ticker, full_tag)
			if tag is None:
				continue
			
			parent_full_tag = calculation_arc.get('xlink:from')
			parent = get_tag(ticker, parent_full_tag)

			# if XBRLNode(tag) exists, add the tag to it, else create the node
			if tag not in fs_fields:
				fs_fields[tag] = XBRLNode(tag)

			fs_fields[tag].parent = parent

			# I JUST COMMENTED OUT THE LINE ABOVE AND MADE IT THE ONE BELOW CAUSE FOR MSFT, THE ORDER WAS A HUGE ASS FLOAT
			# LIKE order="10310.00" SO I CHANGED IT.
			if type(calculation_arc.get('order')) is int:
				fs_fields[tag].order = int(calculation_arc.get('order'))
				fs_fields[tag].weight = float(calculation_arc.get('weight'))

			elif type(calculation_arc.get('order')) is float:
				fs_fields[tag].order = float(calculation_arc.get('order'))
				fs_fields[tag].weight = float(calculation_arc.get('weight'))

			else:
				# this is done for when type could be str. MRC is an example
				fs_fields[tag].order = float(calculation_arc.get('order'))
				fs_fields[tag].weight = float(calculation_arc.get('weight'))

	return fs_fields

def get_fs_fields(ticker:str, form_type, fs, cfiles):
	roleURI = get_URI(cfiles.xsd)
	fs_URI = statement_URI(roleURI, fs)
	fs_fields = {}
	fs_fields = pre_data(ticker, cfiles.pre, fs_URI, fs_fields)
	fs_fields = cal_data(ticker, cfiles.cal, fs_URI, fs_fields)
	return fs_fields


if __name__ == "__main__":
	ticker = sys.argv[1]
	form_type = sys.argv[2]
	directory = find_latest_form_dir(ticker,form_type)
	cfiles = read_forms_from_dir(directory)

	fs = 'bs'
	fs_fields = get_fs_fields(ticker, form_type, fs, cfiles)
	#for key in fs_fields:
	#	print(fs_fields[key])
	#	print()


