from ofiles import read_forms_from_dir, find_latest_form_dir
from xbrl_functions import retrieve_tables
from otermsmap import load_termsmap
from omretrieve import save_latest, get_company_CIK, save_all_facts
import json

import sys
import pandas as pd

def get_dict(ticker,formType,directory,cfiles,termsmap,mag):
	bs_dict, is_dict, cf_dict = retrieve_tables(ticker,cfiles,termsmap)

	div = 1000
	if mag == 't':
		div = 1000
	elif mag == 'm':
		div = 1000000
	elif div == 'n':
		div = 1

	dates = bs_dict["us-gaap:Assets"].date
	rows_list = []
	for key in bs_dict:
		if bs_dict[key].val is None:
			continue
		text = bs_dict[key].text[0] if bs_dict[key].text else ''
		d = {'Tag': bs_dict[key].tag, 'Text':text, dates[1]: bs_dict[key].val[1]/div, dates[0]: bs_dict[key].val[0]/div}
		rows_list.append(d)
	df1 = pd.DataFrame(rows_list)

	rows_list = []
	for key in is_dict:
		if is_dict[key].val is None:
			continue
		text = is_dict[key].text[0] if is_dict[key].text else ''
		d = {'Tag': is_dict[key].tag, 'Text':text, dates[0]: is_dict[key].val[0]/div, dates[1]: is_dict[key].val[1]/div}
		#d = {'Tag': is_dict[key].tag, 'Text':text, dates[0]: is_dict[key].val[0]/div, dates[1]: is_dict[key].val[1]/div, dates[2]: is_dict[key].val[2]/div}
		rows_list.append(d)
	df2 = pd.DataFrame(rows_list)

	rows_list = []
	for key in cf_dict:
		if cf_dict[key].val is None:
			continue
		text = cf_dict[key].text[0] if cf_dict[key].text else ''
		d = {'Tag': cf_dict[key].tag, 'Text':text, dates[0]: cf_dict[key].val[0]/div, dates[1]: cf_dict[key].val[1]/div}
		rows_list.append(d)
	df3 = pd.DataFrame(rows_list)
	return df1, df2, df3

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
		'PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets',
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
def write_to_csv(BS,IS,CF,TAGS):
	writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
	BS.to_excel(writer, sheet_name='Balance Sheet')
	IS.to_excel(writer, sheet_name='Income Statement')
	CF.to_excel(writer, sheet_name='Cash Flow')
	TAGS.to_excel(writer, sheet_name='Tags')
	writer.save()

def write_to_csv(BS,IS,CF):
	writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
	BS.to_excel(writer, sheet_name='Balance Sheet')
	IS.to_excel(writer, sheet_name='Income Statement')
	CF.to_excel(writer, sheet_name='Cash Flow')
	writer.save()

def write_to_csv(TAGS):
	writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
	TAGS.to_excel(writer, sheet_name='Tags')
	writer.save()


if __name__ == '__main__':
	
	ticker = sys.argv[1]
	formType = sys.argv[2]
	mag = sys.argv[3]
	#CIK = get_company_CIK(ticker)

	retrieved_forms = save_latest(sys.argv[1], sys.argv[2])
	retreieved_facts = save_all_facts(sys.argv[1])

	if not retrieved_forms and not retreieved_facts:
		print("Failed to retrieve both forms and facts Exiting...")
		return

	directory = find_latest_form_dir(ticker,formType)
	cfiles = read_forms_from_dir(directory)
	termsmap = load_termsmap()

	BS,IS,CF = get_dict(ticker,formType,directory,cfiles,termsmap,mag)
	TAGS = getTags(ticker,f"./forms/{ticker}/{ticker}.json")
	write_to_csv(BS,IS,CF,TAGS)
	

	ticker = sys.argv[1]
	formType = sys.argv[2]
	mag = sys.argv[3]
	save_all_facts(sys.argv[1])

	TAGS = getTags(ticker,f"./forms/{ticker}/{ticker}.json")
	write_to_csv(TAGS)
