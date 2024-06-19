import os
from bs4 import BeautifulSoup
import sys
from dataclasses import dataclass
from typing import List
import pandas as pd
import numpy as np
import json
import openpyxl as xl
from datetime import date

from files import read_forms_from_dir, find_latest_form_dir, find_all_form_dir
from xbrl_parse import get_defenition_URI, statement_URI
from edgar_retrieve import get_company_CIK, get_forms_of_type_xbrl, save_all_facts, save_all_forms, download_forms
from html_parse import html_to_facts
from html_process import derived_fs_table, assign_HTMLFact_to_XBRLNode
from util.write_to_csv import *
from util.file_management import read_file
from excel_model.epv import *
from excel_model.cover import *
from excel_model.gv import *
from excel_model.wacc import *
from excel_model.nav import *

import sys
mypath = "./Arelle"
sys.path.insert(0, mypath)

from arelle.CntlrCmdLine import parseAndRun
#from Arelle.arelleCmdLine import runMain

def get_parsing_directories(ticker, parsing_method):
	directory_cfiles = []
	directory_cfiles_10Q = sorted(find_all_form_dir(ticker,"10-Q"))
	directory_cfiles_10Q = list(filter((".DS_Store").__ne__, directory_cfiles_10Q))
	directory_cfiles_10K = sorted(find_all_form_dir(ticker,"10-K"))
	directory_cfiles_10K = list(filter((".DS_Store").__ne__, directory_cfiles_10K))

	# Parse every single quarter and 10-K
	if parsing_method == 'q':
		directory_cfiles = sorted(directory_cfiles_10Q + directory_cfiles_10K)

	# Parse all 10-Q past the most recent 10-K
	elif parsing_method == 'r':
		directory_cfiles = directory_cfiles_10K + []	# Just adding + [] so it will not be a reference to directory_cfiles_10K
		for i, cfile_10Q in enumerate(directory_cfiles_10Q):
			if cfile_10Q > directory_cfiles_10K[-1]:
				directory_cfiles += directory_cfiles_10Q[i:]
				break
	# Parse the latest only
	# TODO: this will work once epv_info shit is sorted
	elif parsing_method == 'l':
		if directory_cfiles_10K[-1] > directory_cfiles_10Q[-1]:
			directory_cfiles = directory_cfiles_10K[-1:]
		else:
			directory_cfiles = directory_cfiles_10Q[-1:]
	# Only parse 10-K
	else:
		directory_cfiles = directory_cfiles_10K

	return directory_cfiles, directory_cfiles_10K, directory_cfiles_10Q

def convert_data_to_fs_dict(fs_data, fs_dict):
	relationshipSet = fs_data["relationship"]
	rootConcepts = relationshipSet.rootConcepts
	modelRelationshipsFrom = relationshipSet.modelRelationshipsFrom

	# Get the first root concept and add the rest in the stack
	curConcept = rootConcepts[0]
	stack = rootConcepts[1:]
	# Created visited set to avoid adding the same concept again
	visited = {curConcept}
	while curConcept is not None or stack:
		tag = curConcept.vQname().prefix + ':' + curConcept.name
		if tag not in fs_dict:
			fs_dict[tag] = {}
			fs_dict[tag]["facts"] = {}
			fs_dict[tag]["label"] = curConcept.label()
		
		if curConcept.qname in fs_data["facts"]:
			for date in fs_data["facts"][curConcept.qname]:
				val = fs_data["facts"][curConcept.qname][date][0]
				fs_dict[tag]["facts"][date] = val

		# Add the children of the current concept and add it to the front of the stack
		conceptsToAdd = []
		modelRelationshipsFromList = modelRelationshipsFrom[curConcept]
		for cur_modelRelationshipsFrom in modelRelationshipsFromList:
			toConcept = cur_modelRelationshipsFrom.toModelObject
			# Only add the child concept if it has not been added to the parent yet
			# TODO: This could pose an issue in the future when we introduce duplicate tags
			if toConcept not in visited:
				conceptsToAdd.append(toConcept)
				visited.add(toConcept)
		stack = conceptsToAdd + stack

		# Get the first concept in the stack
		if stack:
			curConcept = stack.pop(0)
		else:
			curConcept = None

	return fs_dict

def fs_list_insert_or_add_concept(fs_list, cur_year_fs_dict, bRemoveDuplicateDates=False):
	if fs_list == []:
		for conceptName in cur_year_fs_dict:
			fs_list.append({"tag": conceptName, "label": cur_year_fs_dict[conceptName]["label"], "facts": cur_year_fs_dict[conceptName]["facts"]})
	else:

		if bRemoveDuplicateDates:
			# Remove exisiting dates
			new_dates = set()
			for conceptName in cur_year_fs_dict:
				for date in cur_year_fs_dict[conceptName]["facts"]:
					new_dates.add(date)
			for tag_info in fs_list:
				for new_date in new_dates:
					if new_date in tag_info["facts"]:
						del tag_info["facts"][new_date]

		index = 0
		for conceptName in cur_year_fs_dict:
			for i in range(len(fs_list)):
				next = False
				if conceptName == fs_list[i]["tag"]:
					fs_list[i]["facts"] = fs_list[i]["facts"] | cur_year_fs_dict[conceptName]["facts"]
					index = i+1
					next = True
					break
			if next: continue
			fs_list.insert(index, {"tag": conceptName, "facts": cur_year_fs_dict[conceptName]["facts"]})
	return fs_list

def reorder_and_add_blank_columns(df_fs):
	df_fs = df_fs.reindex(sorted(df_fs.columns), axis=1)
	df_fs = df_fs.iloc[:, ::-1]
	[df_fs.insert(i, '', np.nan, allow_duplicates=True) for i in range(df_fs.shape[1], 1, -1)]
	return df_fs

def fill_ratio_tags(ratio_tags, all_fs_info, bMain=False):
	all_ratio_tags = []
	# Loop through each financial statement concepts
	for fs in ratio_tags:
		fs_info = all_fs_info[fs]
		# Loop through the concepts
		for concept in ratio_tags[fs]:
			if not bMain:
				if concept in ["Goodwill", "Intangible Assets", "SG&A", "CF from Investing Portion"]: continue
			cur_concept = {"concept": concept}
			for tag_info in fs_info:
				tag = tag_info['tag'].split(':')[-1]
				if tag in ratio_tags[fs][concept]:
					for key in tag_info:
						if key == "label" or key == "tag": continue
						val = tag_info[key]
						if concept == "CAPEX" or concept == "Dividend":
							val = -abs(val)
						if key in cur_concept:
							cur_concept[key] += val
						else:
							cur_concept[key] = val
			all_ratio_tags.append(cur_concept)
	return all_ratio_tags

def run_arelle():
	ticker = input("Enter ticker: ")
	scale = input("Enter scale: ")
	
	div = 1000
	if scale == 'm':
		div = 1000000
	elif scale == '':
		div = 1

	download_forms(ticker, False, False)
	directory_cfiles, directory_cfiles_10K, directory_cfiles_10Q = get_parsing_directories(ticker, 'k')
	
	fs_data = {}
	fs_list = {'bs': [], 'is': [], 'cf': []}
	for cur_year in directory_cfiles:
		try:
			cfiles = read_forms_from_dir(f"forms/{ticker}/10-K/{cur_year}")
			zip_file = "/Users/caseymackinnon/Desktop/Personalized Finance/edgar/" + cfiles.zip
			#zip_file = "./" + cfiles.zip
			arg = ['-f', zip_file, "--factTable=test.txt"]
			data = parseAndRun(arg)


			statement_roleURI = get_defenition_URI(cfiles.xsd, 'Statement')
			roleURIs = [roleURI for roleURI in statement_roleURI]
			fs_data[cur_year] = {}
			for fs in ('bs', 'is', 'cf'):
				fs_roleURI = statement_URI(roleURIs, fs)
				fs_data[cur_year][fs] = data[fs_roleURI]
				
				cur_year_fs_data = fs_data[cur_year][fs]
				cur_year_fs_dict = {}
				cur_year_fs_dict = convert_data_to_fs_dict(cur_year_fs_data, cur_year_fs_dict)
				fs_list[fs] = fs_list_insert_or_add_concept(fs_list[fs], cur_year_fs_dict)

		except:
			print(f"Failed to prase for {cur_year}.")
	
	all_fs_info = {'bs': [], 'is': [], 'cf': []}
	for fs in fs_list:
		cur_fs_list = fs_list[fs]

		for tag_info in cur_fs_list:
			dict_to_add = {}
			dict_to_add['tag'] = tag_info['tag']
			if 'label' in tag_info:
				dict_to_add['label'] = tag_info['label']
			else:
				dict_to_add['label'] = tag_info['tag']
			for date in tag_info['facts']:
				str_date = date.strftime('%Y-%m-%d')
				str_val = tag_info['facts'][date]
				if str_val != '(nil)':
					val = float(str_val.replace(',',''))/div
					dict_to_add[str_date] = val
				else:
					dict_to_add[str_date] = tag_info['facts'][date]

			all_fs_info[fs].append(dict_to_add)

	with open('./tags/ratio_tags.json') as f:
		file_contents = f.read()
		ratio_tags = json.loads(file_contents)
	
	all_ratio_tags = fill_ratio_tags(ratio_tags, all_fs_info, True)	
	all_other_ratio_tags = fill_ratio_tags(ratio_tags, all_fs_info)			
			
	writer = pd.ExcelWriter(f"./excel/{ticker}.xlsx", engine='xlsxwriter')
	df_bs = pd.DataFrame(all_fs_info['bs'])
	df_bs = reorder_and_add_blank_columns(df_bs)

	df_is = pd.DataFrame(all_fs_info['is'])
	df_is = reorder_and_add_blank_columns(df_is)

	df_cf = pd.DataFrame(all_fs_info['cf'])
	df_cf = reorder_and_add_blank_columns(df_cf)

	df_concepts = pd.DataFrame(all_ratio_tags)
	df_concepts = reorder_and_add_blank_columns(df_concepts)

	df_other_concepts = pd.DataFrame(all_other_ratio_tags)
	df_other_concepts = reorder_and_add_blank_columns(df_other_concepts)

	df_bs.to_excel(writer, sheet_name='Balance Sheet')
	df_is.to_excel(writer, sheet_name='Income Statement')
	df_cf.to_excel(writer, sheet_name='Cash Flow')
	df_concepts.to_excel(writer, sheet_name='Ratios')
	df_other_concepts.to_excel(writer, sheet_name='Other Ratios')
	writer.save()

if __name__ == "__main__":
    run_arelle()