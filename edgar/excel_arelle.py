import os
from bs4 import BeautifulSoup
import sys
from dataclasses import dataclass
from typing import List
import pandas as pd
import json
import openpyxl as xl

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

def main():
	ticker =input("Enter ticker: ")
	download_forms(ticker, True)
	directory_cfiles, directory_cfiles_10K, directory_cfiles_10Q = get_parsing_directories(ticker, 'k')
	
	fs_data = {}
	for i, cur_year in enumerate(directory_cfiles):
		cfiles = read_forms_from_dir(f"forms/{ticker}/10-K/{cur_year}")
		statement_roleURI = get_defenition_URI(cfiles.xsd, 'Statement')
		roleURIs = [roleURI for roleURI in statement_roleURI]
		bs_roleURI = statement_URI(roleURIs, 'bs')
		is_roleURI = statement_URI(roleURIs, 'is')
		cf_roleURI = statement_URI(roleURIs, 'cf')
		fs_roleURIs = [bs_roleURI, is_roleURI, cf_roleURI]

		zip_file = "/Users/caseymackinnon/Desktop/Personalized Finance/edgar/" + cfiles.zip
		#zip_file = "./" + cfiles.zip
		arg = ['-f', zip_file, "--factTable=test.txt"]
		data = parseAndRun(arg)

		fs_data[cur_year] = {}
		fs_data[cur_year]['bs'] = data[bs_roleURI]
		fs_data[cur_year]['is'] = data[is_roleURI]
		fs_data[cur_year]['cf'] = data[cf_roleURI]

	cur_year = directory_cfiles_10K[-1]
	bs_data = fs_data[cur_year]['bs']
	
	relationshipSet = bs_data["relationship"]
	rootConcepts = relationshipSet.rootConcepts
	modelRelationshipsFrom = relationshipSet.modelRelationshipsFrom

	# Get the first root concept and add the rest in the stack
	curConcept = rootConcepts[0]
	stack = rootConcepts[1:]
	# Created visited set to avoid adding the same concept again
	visited = {curConcept}
	while curConcept is not None or stack:
		print(curConcept.qname)

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


if __name__ == "__main__":
    main()