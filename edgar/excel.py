import os
from bs4 import BeautifulSoup
import sys
from dataclasses import dataclass
from typing import List
import pandas as pd
import json

from files import read_forms_from_dir, find_latest_form_dir, find_all_form_dir
from xbrl_parse import get_fs_fields
from edgar_retrieve import get_company_CIK, get_forms_of_type_xbrl, save_all_facts, save_all_forms
from html_parse import html_to_facts
from html_process import derived_fs_table, assign_HTMLFact_to_XBRLNode

def get_fs_list(fs_fields, mag):
	div = 1000
	if mag == 't':
		div = 1000
	elif mag == 'm':
		div = 1000000
	elif div == 'n':
		div = 1

	date = fs_fields["us-gaap:Assets"].date

	fs_list = []
	for key in fs_fields:
		if fs_fields[key].val is None:
			continue
		text = fs_fields[key].text[0] if fs_fields[key].text else ''
		for i,tag in enumerate(fs_fields[key].text):
			d = {'Tag': fs_fields[key].tag, 'Text':text, date: fs_fields[key].val[i]/div}
			fs_list.append(d)
	return fs_list
	
def getTags(ticker,destination):
	div = 1000
	if mag == 't':
		div = 1000
	elif mag == 'm':
		div = 1000000
	elif div == 'n':
		div = 1

	TAGS = ['CashAndCashEquivalentsAtCarryingValue', 'CashAndDueFromBanks', 
		'PropertyPlantAndEquipmentNet', 'PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization', 
		'LongTermDebtNoncurrent', 'us-gaap:OtherLongTermDebt', 
		'StockholdersEquity', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',

		'InterestIncomeOperating', 'NoninterestIncome',
		'NetIncomeLoss', 'OperatingIncomeLoss','RevenueFromContractWithCustomerExcludingAssessedTax',
		'Revenues',
		'ResearchAndDevelopmentExpense', 
		'SellingGeneralAndAdministrativeExpense', "GeneralAndAdministrativeExpense", "SellingAndMarketingExpense", "MarketingAndAdvertisingExpense",
		'LaborAndRelatedExpense', 'OccupancyNet', 'LegalFees', 'MarketingAndAdvertisingExpense', 'Communication', 'EquipmentExpense'
		"InterestExpense", 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
		'ProvisionForLoanLossesExpensed',
		'EarningsPerShareDiluted', 

		'DepreciationAndAmortization','DepreciationDepletionAndAmortization', "Depreciation", "AmortizationOfIntangibleAssets",
		'ShareBasedCompensation', 
		'PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'us-gaap:PaymentsToAcquireRealEstate',
		'CommonStockDividendsPerShareDeclared'

		]

	with open(destination, 'r') as f:
		data = f.read()
	data = json.loads(data)['facts']['us-gaap']

	dates1 = []
	for tag in TAGS:
		if tag in data: 
			if tag == 'CashAndCashEquivalentsAtCarryingValue':
				rowData = {}
				if 'USD' in data[tag]['units']:
					d = list(data[tag]['units']['USD'])
					for year in d:
						if year['form'] == '10-K':
							if year['end'] not in dates1: dates1.append(year['end'])
	dates1.sort()

	dates2 = []
	for tag in TAGS:
		if tag in data: 
			if tag == 'CashAndDueFromBanks':
				rowData = {}
				if 'USD' in data[tag]['units']:
					d = list(data[tag]['units']['USD'])
					for year in d:
						if year['form'] == '10-K':
							if year['end'] not in dates2: dates2.append(year['end'])
	dates2.sort()

	if len(dates1) > len(dates2):
		dates = dates1
	else:
		dates = dates2

	df = pd.DataFrame(columns = dates)

	for tag in TAGS:
		if tag in data: 
			rowData = {y:0 for y in dates}
			if 'USD' in data[tag]['units']:
				d = list(data[tag]['units']['USD'])
				for year in d:
					if year['form'] == '10-K' and year['end'] in dates:
						rowData[year['end']] = year['val']/div
			appendRow = [rowData[key] for key in rowData]
			df.loc[tag] = appendRow

	#df.to_csv("ticker.csv")
	return df

# overrides for write_to_csv
def write_to_csv(ticker,BS,IS,CF,TAGS):
	writer = pd.ExcelWriter(f"{ticker}.xlsx", engine='xlsxwriter')
	BS.to_excel(writer, sheet_name='Balance Sheet')
	IS.to_excel(writer, sheet_name='Income Statement')
	CF.to_excel(writer, sheet_name='Cash Flow')
	TAGS.to_excel(writer, sheet_name='Tags')
	writer.save()

def write_to_csv(ticker,BS,IS,CF):
	writer = pd.ExcelWriter(f"{ticker}.xlsx", engine='xlsxwriter')
	BS.to_excel(writer, sheet_name='Balance Sheet')
	IS.to_excel(writer, sheet_name='Income Statement')
	CF.to_excel(writer, sheet_name='Cash Flow')
	writer.save()

def write_to_csv(ticker,BS,TAGS):
	writer = pd.ExcelWriter(f"{ticker}.xlsx", engine='xlsxwriter')
	BS.to_excel(writer, sheet_name='Balance Sheet')
	TAGS.to_excel(writer, sheet_name='Tags')
	writer.save()

def write_to_csv(ticker,TAGS):
	writer = pd.ExcelWriter(f"{ticker}.xlsx", engine='xlsxwriter')
	TAGS.to_excel(writer, sheet_name='Tags')
	writer.save()

if __name__ == "__main__":
	ticker = sys.argv[1]
	form_type = sys.argv[2]
	mag = sys.argv[3]
	CIK = get_company_CIK(ticker)

	
	# Retrieve the forms
	all_inline_10k_forms = get_forms_of_type_xbrl(CIK,'10-K', True)
	all_inline_10q_forms = get_forms_of_type_xbrl(CIK,'10-Q', True)
	
	if all_inline_10k_forms != []: retrieved_forms = save_all_forms(ticker,'10-K',all_inline_10k_forms)
	if all_inline_10q_forms != []: retrieved_forms = save_all_forms(ticker,'10-Q',all_inline_10q_forms)

	# Get the directory where the forms are/were stored and sort them in chronological order.
	directory_cfiles = find_all_form_dir(ticker,form_type)
	directory_cfiles.sort(reverse=True)
	
	#TODO: I need to add retrieve both current and previous year bs info. Rn, im only getting the current year.
	# Attempt to parse as much fs info and append them all into all_fs_info
	all_fs_info = []
	for i in range(len(directory_cfiles)):
		cur_year = directory_cfiles[i]
		try:
			cfiles = read_forms_from_dir(f"forms/{ticker}/{form_type}/{directory_cfiles[i]}")
			bs_fields = get_fs_fields(ticker, 'bs', cfiles)
			all_tables = html_to_facts(cfiles.html, cfiles.htm_xml, bs_fields)
			fs_table_from_html = derived_fs_table(all_tables, bs_fields)
			bs_fields = assign_HTMLFact_to_XBRLNode(bs_fields, fs_table_from_html)
			fs_list = get_fs_list(bs_fields, mag)
		except:
			print(f"Could not parse for {directory_cfiles[i]}.")
			continue

		if all_fs_info == []: 
			all_fs_info = fs_list
		else:
			i,j = 0,0
			while i < len(all_fs_info) and j < len(fs_list):
				#If the tags match, add the date and the value to the dict.
				#TODO: for now, we are assuming no repeating tags. Will need to add that.
				if all_fs_info[i]["Tag"] == fs_list[j]["Tag"]:
					all_fs_info[i][cur_year] = fs_list[j][cur_year]
					i += 1
					j += 1
				else:
					all_fs_info.insert(i, fs_list[j])
					j += 1
					i += 1
				
				# If we reached the end of all_fs_info, just append every other tags from fs_fields not added yet.
				if i == len(all_fs_info):
					for i in range(j, len(fs_list)):
						all_fs_info.append(fs_list[j])
					break
				# If we reach the end of fs_list, we have no more tags to add so just break out.
				if j == len(fs_list):
					break
	df = pd.DataFrame(all_fs_info)
			
	#TODO: Work on duplicate tags.
	
	# Retrieve facts json
	retreieved_facts = save_all_facts(sys.argv[1])
	if retreieved_facts:
		TAGS = getTags(ticker,f"./forms/{ticker}/{ticker}.json")
		#write_to_csv(ticker,TAGS)
	else:
		print("I have to work on facts from BS. Facts retreival failed as well. look into why.")

	writer = pd.ExcelWriter(f"./excel/{ticker}.xlsx", engine='xlsxwriter')
	df.to_excel(writer, sheet_name='Balance Sheet')
	TAGS.to_excel(writer, sheet_name='Tags')
	writer.save()
	writer.close()