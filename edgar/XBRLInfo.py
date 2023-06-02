from htmlparse import html_to_facts, Fact
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from files import read_forms_from_dir, find_latest_form_dir
import sys

@dataclass
class XBRLNode:
	tag: str
	child: list
	parent: str
	val: float
	weight: float
	order: float
	date: str
	text: str

	def	__init__(self,tag,child,parent):
		self.tag = tag
		self.child = child
		self.parent = parent
		self.val = None
		self.weight = None
		self.order = None
		self.date = None
		self.text = None

@dataclass
class CompanyData:
	balance_sheet: list()
	income_statement: list()
	cash_flow: list()

@dataclass
class PreData:
	child: str
	parent: str

@dataclass
class CalTags:
	order: int
	weight: int

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

def URI_from_statement(roleURI:str, statement:str, terms:dict) -> str:
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
def find_statement(file_pre:str, ticker:str, fs_URI:str) -> list:
	elements = list()
	ticker = ticker.lower()
	soup = BeautifulSoup(file_pre, 'html.parser')
	presentationLink = soup.find_all(['link:presentationlink','presentationlink'])
	capture = None

	for link in presentationLink:
		if link.attrs['xlink:role'] == fs_URI:
			capture = link.find_all(['link:presentationarc','presentationarc'])

			#if capture is None:

	for e in capture:
		child, parent = None, None

    	# getting the child
		child_tag = e.get('xlink:to')
		child = get_tag(ticker,child_tag)

    	# getting the parent
		parent_tag = e.get('xlink:from')
		parent = get_tag(ticker,parent_tag)

		elements.append(PreData(child,parent))

	return elements


# Gets the information from the cal file (order and the weight) and stores it with the tags
def cal_data(ticker:str, file_cal:str, fs_URI:str):
	cal_map = dict()

	soup = BeautifulSoup(file_cal, 'html.parser')
	calculationLink = soup.find_all(['link:calculationlink','calculationlink'])

	for link in calculationLink:
		capture = None
		if link.attrs['xlink:role'] in fs_URI:
			capture = link.find_all(['link:calculationarc','calculationarc'])

		if capture is None: continue
		for e in capture:
			tag = get_tag(ticker,e.get('xlink:to'))
			#cal_map[tag] = CalTags(int(e.get('order')), float(e.get('weight')))

			# I JUST COMMENTED OUT THE LINE ABOVE AND MADE IT THE ONE BELOW CAUSE FOR MSFT, THE ORDER WAS A HUGE ASS FLOAT
			# LIKE order="10310.00" SO I CHANGED IT.
			if type(e.get('order')) is int:
				cal_map[tag] = CalTags(int(e.get('order')), float(e.get('weight')))
			elif type(e.get('order')) is float:
				cal_map[tag] = CalTags(float(e.get('order')), float(e.get('weight')))
			else:
				# this is done for when type could be str. MRC is an example
				cal_map[tag] = CalTags(float(e.get('order')), float(e.get('weight')))
	return cal_map