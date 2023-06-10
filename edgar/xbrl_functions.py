from htmlparse import html_to_facts, Fact
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from files import read_forms_from_dir, find_latest_form_dir
import sys

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
def find_statement(file_pre:str, ticker:str, uri:str) -> list:
	elements = list()
	ticker = ticker.lower()
	soup = BeautifulSoup(file_pre, 'html.parser')
	presentationLink = soup.find_all(['link:presentationlink','presentationlink'])
	capture = None

	for link in presentationLink:
		if link.attrs['xlink:role'] == uri:
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


# Given the list of classes, that contains the child and parent, it will take the child and return it as a list
def PreData_children(elements:list) -> list:
	children = list()
	# family contains 
	for relation in elements:
		children.append(relation.child)
	return children

# Given the list of all the financial statement elements, we get rid of the unneeded elements
def clean_statement(elements:list) -> list:
	statement = list()
	#skip = ['Abstract','Items','Axis','Member','Domain','Table']
	skip = ['Items','Axis','Member','Domain','Table']
	for relation in elements:
		if relation.child is None or relation.parent is None:
			continue
		else:
			if any(relation.child.endswith(s) for s in skip):
				continue
		statement.append(relation)
	return statement

# Given the table and the elements of the specified financial statement, it will return a percentage match of the table
# This will take the percentage compared to the list elements found from pre file
def percentage(table:list, children:list) -> float:
	if len(children) == 0: return 0
	count = set()
	for tag in table:
		if tag[0].tag in children:
			count.add(tag[0].tag)
	return len(count)/len(children)

# Given the table and the elements of the specified financial statement, it will return a percentage match of the table
# This will take the percentage compared to the list elements found from the table we are looping through in HTML file
def percentage_add(table:list, children:list) -> float:
	#TODO: maybe add something in case the table found has a length of 0. return 0 so we don't have to divide by 0
	count = set()
	for tag in table:
		if tag[0].tag in children:
			count.add(tag[0].tag)
	return len(count)/len(table)

# Returns the table index of best match, percentage of best match, table of best match, and a dictionary of table elements with the percentage matched
def best_statement_percentage(tables,statement):
	best_index, best_percentage = 0, 0
	for index,table in enumerate(tables):
		count = set()
		pTmp = percentage(table,statement)
		if pTmp > best_percentage:
			best_percentage = pTmp
			best_index = index
	return best_index, best_percentage, tables[best_index]

# Remove elements from list of elements that already exist in the table
def trunk_table(statement:list, table:list) -> list:
	full = list()
	for e in table:
		full.append(e[0].tag)
	return list((set(statement)-set(full)))

# Combines the tables if we deem that the the table is split into two separate tables
def combine_table(table: list, statement:list) -> list:
	child = PreData_children(statement)
	index2 = None
	index1, percentage1, table1 = best_statement_percentage(table,child)
	if percentage1 != 1.0:
		trunked = trunk_table(child,table1)
		if len(trunked) != 0:
			index2, percentage2, table2 = best_statement_percentage(table,trunked)
			if percentage1 < percentage2 and percentage_add(table2,trunked) > percentage1:
				if index1 > index2:
					table1 = table2 + table1
				else:
					table1 = table1 + table2
	return table1

def assign_parent(all_facts,fs1):
	for table in all_facts:
		for row in table:
			for f in row:
				for e in fs1:
					if e.child in f.tag:
						f.parent = e.parent
						break
	return

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

	# TODO
#	def __str__(self):
#		return 

def PreData_to_dict(PreData_List):
	hashmap = {}
	for e in PreData_List:
		hashmap[e.child] = e.parent
	return hashmap

def top_node_to_json(node,visited):
	if not node or node.tag in visited:
		return
	else:
		print(node.tag)
		visited.add(node.tag)


	if node.child is not None:
		tmp = []
		for child in node.child:
			tmp.append(child.tag)
		print(tmp)

		for child in node.child:
			top_node_to_json(child,visited)

	return

# This will return the top tag of the financial statement. Each tag will have a node assigned which will consist of its tag, a list of its children node, 
# its parent node, and the value of the node.
def assign_children(fs_elements):
	fs_dict = PreData_to_dict(fs_elements)

	family_dict = {}
	# first loop to get all tags with children
	for child,parent in fs_dict.items():
		if parent in family_dict:
			family_dict[parent].append(child)
		else:
			family_dict[parent] = [child]
	# second loop to get all tags with no children
	for key in fs_dict:
		if key not in family_dict:
			family_dict[key] = []

	top_tag = fs_elements[0].parent if fs_elements[0].parent else fs_elements[0].child

	# top_node will be the very top of the nodes
	# eg) "us-gaap:StatementOfFinancialPositionAbstract" will have pr"us-gaap:AssetsAbstract" and "us-gaap:LiabilitiesAndStockholdersEquityAbstract" as child
	# fs_dict will return the node of the tag given the tag. Just another way to access the nodes easily.
	fs_dict = dict()
	top_node = tag_recursion(top_tag,None,family_dict,fs_dict) 		# top_node and all other nodes does not have any values assiged yet
	
	top_node_to_json(top_node,set())
	
	return top_node, fs_dict

# Starting from the top tag, it will create the Family node and assign all the children and so on
def tag_recursion(tag,parent_node,family_dict,fs_dict):

#TODO: add val, date, and text to the Family dataclass for each node

	cur_node = XBRLNode(tag,None,parent_node)		# create a node for the current tag

	if family_dict[tag] == []:					# BASE CASE: if the current tag has no children, node.child will be none and the node will be returned
		cur_node.child = None
		fs_dict[tag] = cur_node
		return cur_node

	children_nodes = list() 					# children_nodes contains all the children nodes of the current node
	for child in family_dict[tag]:
		children_nodes.append(tag_recursion(child,cur_node,family_dict,fs_dict))

	# once all the children nodes are appended to children_nodes, we set the cur_node.child to the list with all the children nodes
	cur_node.child = children_nodes
	fs_dict[tag] = cur_node
	return cur_node								# finally return the cur_node

# Assign the missing text, date, val, weight, and order in the nodes of the tags 
def assign_node_values(fs_dict,FS,cal_map):
	tmp_dict = {}
	for Facts in FS:
		tmp_dict[Facts[0].tag] = Facts

	for tag,Facts in tmp_dict.items():
		# goes through each node of the tags and assigns val, date, and text from Facts dataclass if it exists
		if tag in fs_dict:
			fs_dict[tag].val = [Facts[i].val for i in range(len(Facts))]
			fs_dict[tag].date = [Facts[i].date for i in range(len(Facts))]
			fs_dict[tag].text = [Facts[i].text for i in range(len(Facts))]

			# goes through each node of the tags and assign weight and order of the tag from CalTags dataclass if it exist
			if tag in cal_map:
				fs_dict[tag].weight = cal_map[tag].weight
				fs_dict[tag].order = cal_map[tag].order

	# First go through and see if there are tags like "us-gaap:Assets" since we can assign that directly to "us-gaap:AssetsAbstract"
	for tag in fs_dict:
		if tag and 'Abstract' in tag:
			tagAbstract = tag[:-len('Abstract')]
			if tagAbstract in fs_dict:
				fs_dict[tag].val = fs_dict[tagAbstract].val
				fs_dict[tag].date = fs_dict[tagAbstract].date
	
	return fs_dict

	# go through each node and assign value
	# no value, we will take the sum of its children value
	# call the same function on children (recursion)
	# if the children node doesn't have a value for some reason, we can just flag it for now (tag, parent, date, etc)

def retrieve_fs_table(ticker:str, fs, cfiles, roleURI):
	fs_URI = statement_URI(roleURI, fs)

	assert_msg = {
		'bs': "Balance sheet URI link is not found...",
		'is': "Income statement URI link is not found...",
		'cf': "Cash flow statement URI link is not found..."
	}
	assert fs_URI != None, assert_msg[fs]

	cal_map = cal_data(ticker, cfiles.cal, fs_URI)		# dictionary of tags in bs, is, and cf with its weight and order
	all_facts = html_to_facts(cfiles.html, cal_map)		# list of all tables in 10-K/10-Q and its elements

	# {fs}_elements contains all the tags including tags such as Abstarct
	# {fs}_top_node points to the top node of the fs
	# {fs}_dict is dict of all nodes of tags. {fs}_dict[tag] will return the node of the tag
	fs_elements = find_statement(cfiles.pre,ticker,fs_URI)
	fs_top_node, fs_dict = assign_children(fs_elements)
	fs_elements = clean_statement(fs_elements)			# cleans the fs_elements with items that have Keywords that are not needed

	assign_parent(all_facts,fs_elements)

	# list (len of FS) of list (len(2)) containing each tags with parent, text, val, date
	FS = combine_table(all_facts,fs_elements)									

	# assign the missing text, date, val, weight, and order in the nodes of the tags
	assign_node_values(fs_dict,FS,cal_map)

	return fs_dict
	

def retrieve_tables(ticker:str, cfiles):
	roleURI = get_URI(cfiles.xsd)

	BS_dict = retrieve_fs_table(ticker, 'bs', cfiles, roleURI)
	print()
	IS_dict = retrieve_fs_table(ticker, 'is', cfiles, roleURI)
	CF_dict = retrieve_fs_table(ticker, 'cf', cfiles, roleURI)

	return CompanyData(BS_dict,IS_dict,CF_dict)

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("USAGE: python3 xbrl_functions.py <ticker> <form type>")
		print("\tex. python3 xbrl_functions.py AAPL 10-K")
		sys.exit(0)

	ticker = sys.argv[1]
	formType = sys.argv[2]
	directory = find_latest_form_dir(ticker,formType)
	cfiles = read_forms_from_dir(directory)

	data = retrieve_tables(ticker,cfiles)
	#print(data.balance_sheet)
