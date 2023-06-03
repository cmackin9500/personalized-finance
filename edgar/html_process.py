import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
import sys

from html_parse import html_to_facts, HTMLFact
from files import read_forms_from_dir, find_latest_form_dir
from xbrl_parse import XBRLNode, get_fs_fields

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

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("USAGE: python3 xbrl_functions.py <ticker> <form type>")
		print("\tex. python3 xbrl_functions.py AAPL 10-K")
		sys.exit(0)

	ticker = sys.argv[1]
	form_type = sys.argv[2]
	directory = find_latest_form_dir(ticker,form_type)
	cfiles = read_forms_from_dir(directory)

	fs_fields = get_fs_fields(ticker,form_type,'bs',cfiles)
	clean_fs_fields(fs_fields)

	all_tables = html_to_facts(cfiles.html, fs_fields)

	inx, per = get_best_macth_table(all_tables, fs_fields)
	
	com = combine_tables(all_tables, fs_fields)
	for c in com:
		print(c)
