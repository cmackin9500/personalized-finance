import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
import sys
import json

from html_parse import html_to_facts, HTMLFact
from files import read_forms_from_dir, find_latest_form_dir, find_all_form_dir, find_index_form_dir
from xbrl_parse import XBRLNode, get_fs_fields
import edgar_retrieve as edgar
from util import retreival as re

# Given the list of classes, that contains the child and parent, it will take the child and return it as a list
def XBRLNode_to_fields_list(fs_fields:dict) -> list:
	fields = list()
	for tag in fs_fields:
		fields.append(fs_fields[tag].tag)
	return fields

# Given the list of all the financial statement elements, we get rid of the unneeded elements
def clean_fs_fields(fs_fields:dict) -> dict:
	#skip = ['Abstract','Items','Axis','Member','Domain','Table']
	skip = ['Items','Axis','Member','Domain','Table']
	for tag in list(fs_fields.keys()):
		xbrl_node = fs_fields[tag]
		if any(xbrl_node.tag.endswith(s) for s in skip):
			del fs_fields[tag]
		
	return fs_fields

# Given the table and the elements of the specified financial statement, it will return a percentage match of the table
# This will return the percentage of (HTML table fields in  pre/cal fields)/(fields from pre/cal file)
def fs_fields_match_percentage(html_table:list, fs_fields:list) -> float:
	if len(fs_fields) == 0: return 0
	count = set()
	for tag in html_table:
		if tag[0].tag in fs_fields:
			count.add(tag[0].tag)
	return len(count)/len(fs_fields)

# Given the table and the elements of the specified financial statement, it will return a percentage match of the table
# This will return the percentage of (fields from pre/cal file in HTML table)/(HTML table fields)
def html_table_match_percentage(html_table:list, fs_fields:list) -> float:
	if len(html_table) == 0: return 0
	count = set()
	for tag in html_table:
		if tag[0].tag in fs_fields:
			count.add(tag[0].tag)
	return len(count)/len(html_table)

# Returns the table index of best match, percentage of best match, table of best match, and a dictionary of table elements with the percentage matched
def get_best_macth_table(all_tables, fs_fields):
	best_match_index, best_match_percentage = 0, 0
	for index,table in enumerate(all_tables):

		cur_match_percentage = fs_fields_match_percentage(table, fs_fields)
		if cur_match_percentage > best_match_percentage:
			best_match_percentage = cur_match_percentage
			best_match_index = index

	return best_match_index, best_match_percentage

# Remove elements from list of elements that already exist in the table
def unmatched_fields_in_table(html_table:list, fs_fields:list) -> list:
	already_matched_fields = list()
	for tag in html_table:
		already_matched_fields.append(tag[0].tag)
	return list((set(fs_fields)-set(already_matched_fields)))

# Combines the tables if we deem that the the table is split into two separate tables (e.g. Citi)
def combine_tables(all_tables: list, fs_fields:list) -> list:
	index1, percentage1 = get_best_macth_table(all_tables,fs_fields)
	index2, percentage2 = None, None
	table = all_tables[index1]

	if percentage1 != 1.0:
		unmatched_fields = unmatched_fields_in_table(all_tables[index1],fs_fields)

		if len(unmatched_fields) != 0:
			index2, percentage2 = get_best_macth_table(all_tables,unmatched_fields)

			if percentage1 < percentage2 and html_table_match_percentage(all_tables[index2],unmatched_fields) > percentage1:
				if index1 > index2:
					table = all_tables[index2] + all_tables[index1]
				else:
					table = all_tables[index1] + all_tables[index2]
	return table

def assign_HTMLFact_to_XBRLNode(fs_fields, fs_facts):
	for html_facts in fs_facts:
		html_fact = html_facts[0]
		tag = html_fact.tag

		fs_fields[tag].val = html_fact.val
		fs_fields[tag].date = html_fact.date
		fs_fields[tag].text = html_fact.text
	
	return fs_fields

def assign_child_to_XBRLNode(fs_fields):
	tag_child = {}
	for tag in list(fs_fields.keys()):
		xbrl_node = fs_fields[tag]

		if xbrl_node.parent not in fs_fields:
			fs_fields[xbrl_node.parent] = XBRLNode(xbrl_node.parent)

		if xbrl_node.parent in tag_child:
			tag_child[xbrl_node.parent].append(xbrl_node.tag)
		else:
			tag_child[xbrl_node.parent] = [xbrl_node.tag]

	for tag in tag_child:
		fs_fields[tag].children = tag_child[tag]

	return fs_fields

def top_tags(fs_fields):
	top_tags = []
	for tag in fs_fields:
		if fs_fields[tag].parent == None: top_tags.append(tag)
	return top_tags

def fs_fields_to_json(fs_fields, fs_json, tag):
	if tag in fs_json:
		return fs_json[tag]

	fs_json[tag] = {}
	fs_json[tag]['tag'] = tag
	fs_json[tag]['parent'] = fs_fields[tag].parent
	fs_json[tag]['val'] = fs_fields[tag].val
	fs_json[tag]['weight'] = fs_fields[tag].weight
	fs_json[tag]['order'] = fs_fields[tag].order
	fs_json[tag]['date'] = fs_fields[tag].date
	fs_json[tag]['text'] = fs_fields[tag].text
	fs_json[tag]['lineup'] = fs_fields[tag].lineup
	fs_json[tag]['children'] = {}

	for child_key in fs_fields[tag].children:
		child = fs_fields[child_key]
		fs_json[tag]['children'][child.tag] = {}
		children_fs = fs_fields_to_json(fs_fields, fs_json[tag]['children'][child.tag], child.tag)
		fs_json[tag]['children'][child.tag] = children_fs

	return fs_json[tag]

def ticker_to_json(fs_fields, ticker, form_type, fs, date):
	directory = find_index_form_dir(ticker,form_type,date)
	cfiles = read_forms_from_dir(directory)

	fs_fields = get_fs_fields(ticker,form_type,fs,cfiles)

	all_tables = html_to_facts(cfiles.html, cfiles.htm_xml, fs_fields)

	inx, per = get_best_macth_table(all_tables, fs_fields)
	
	com = combine_tables(all_tables, fs_fields)
	fs_fields = assign_HTMLFact_to_XBRLNode(fs_fields, com)
	fs_fields = assign_child_to_XBRLNode(fs_fields)

	fs_json = {}
	top_node = {'bs': 'us-gaap:StatementOfFinancialPositionAbstract',
	     		'is': 'us-gaap:IncomeStatementAbstract',
		 		'cf': 'us-gaap:StatementOfCashFlowsAbstract'
		 		}
		
	fs_fields_to_json(fs_fields, fs_json, top_node[fs])
	
	#path = f"./store/{ticker}/{fs}"

	path = f"./../backend/store/{ticker}"
	re.mkdir_if_NE(path)
	with open(f"./{path}/{ticker}_{fs}_{date}.json", 'w') as output:
		json.dump(fs_json, output, indent=4)

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print("USAGE: python3 html_process.py <ticker> <form type> <financial statement type>")
		print("\tex. python3 html_process.py AAPL 10-K bs")
		print("bs = balance sheet\nis = income statement\ncf = cashflow staement")
		sys.exit(0)

	ticker = sys.argv[1]
	form_type = sys.argv[2]
	fs = sys.argv[3]

	#CIK = edgar.get_company_CIK(ticker)
	#forms = edgar.get_forms_of_type_xbrl(CIK, form_type, True)
	#edgar.save_all_forms(ticker, form_type, forms)

	directory = find_latest_form_dir(ticker,form_type)
	date = directory.split('/')[-1]
	ticker_to_json({},ticker,form_type,fs,date)


	directory = find_all_form_dir(ticker,form_type)
	for date in directory:
		if date == '.DS_Store': continue
		try:
			ticker_to_json({}, ticker, form_type, fs, date)
			print(f"Parsed for {date}.")
		except:
			print(f"Failed to parse for {date}.")

'''
	directory = find_latest_form_dir(ticker,form_type)
	date = directory.split('/')[-1]
	ticker_to_json({},ticker,form_type,fs,date)
'''