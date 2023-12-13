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

# Notes:
	# Operating Income = Pretax Income + Interest Expense

	TAGS = [
	# Cash
		'CashAndDueFromBanks', 'CashEquivalentsAtCarryingValue', 'InterestBearingDepositsInBanks',
	# Cash and Cash Equivalents
		'CashCashEquivalentsAndFederalFundsSold', 'CashAndCashEquivalentsAtCarryingValue',
	# Cash + Restricted Cash
		'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents'
	# Accounts Recievables
		'AccountsReceivableNetCurrent',
	# Inventory
		'InventoryNet',
	# Goodwill and Intangible Assets
		'Goodwill', 'IntangibleAssetsNetExcludingGoodwill', 'FiniteLivedIntangibleAssetsNet',
	# Current Assets
		'AssetsCurrent',
	# Short-Term Debt
		'LongTermDebtCurrent', 'CommercialPaper', 'ShortTermBorrowings',
	# Current Liabilities
		'LiabilitiesCurrent',
	# Long-Term Debt
		'LongTermDebtNoncurrent', 'FederalHomeLoanBankAdvancesLongTerm', 'JuniorSubordinatedNotes', 'OtherLongTermDebt', 'JuniorSubordinatedDebentureOwedToUnconsolidatedSubsidiaryTrust',
		'UnsecuredLongTermDebt', 'LongTermDebt',
	# Debt
		'AdvancesFromFederalHomeLoanBanks', 'SubordinatedDebt', 'OtherBorrowings',
	# Common Equity
		'StockholdersEquity', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'
	# Revenues
		'RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues',
	# SG&A
		'SellingGeneralAndAdministrativeExpense', "GeneralAndAdministrativeExpense", "SellingAndMarketingExpense", "MarketingAndAdvertisingExpense",
		'LaborAndRelatedExpense', 'OccupancyNet', 'LegalFees', 'MarketingAndAdvertisingExpense', 'Communication', 'EquipmentExpense',
		'CommunicationsAndInformationTechnology', 'MarketingExpense', 'ProfessionalFees', 'InformationTechnologyAndDataProcessing',
		'SuppliesAndPostageExpense', 'AdvertisingExpense',
	# COGS
		'CostOfGoodsAndServicesSold', 
	# Gross Profit
		'GrossProfit',
	# Interest and Dividend Income
		'InterestAndDividendIncomeOperating',
	# Operating Income
		'OperatingIncomeLoss', 
	# Interest Expense
		'InterestExpense',
	# Net Interest Income
		'InterestIncomeExpenseNet',
	# Non-interest Income
		'NoninterestIncome',
	# Pretax Income
		'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments',
	# Net Income
		'NetIncomeLoss', 'ProfitLoss',
	# Retained Earnings
		'RetainedEarningsAccumulatedDeficit',
	# Depreciation and Amoritization
		'DepreciationAndAmortization','DepreciationDepletionAndAmortization', "Depreciation", "AmortizationOfIntangibleAssets", 'OtherDepreciationAndAmortization',
		'DepreciationAmortizationAndAccretionNet',
	# Stock-Based Compoensation
		'ShareBasedCompensation', 
	# Net Operating Cash Flow
		'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations', 'NetCashProvidedByUsedInOperatingActivities',
	# CF from Investing Portion
		'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations', 'NetCashProvidedByUsedInInvestingActivities',
	# Capex
		'PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'us-gaap:PaymentsToAcquireRealEstate',
	# Dividend
		'PaymentsOfDividends', 'PaymentsOfDividendsCommonStock', 'PaymentsOfDividendsPreferredStockAndPreferenceStock', 'PaymentsOfOrdinaryDividends',


	# Total Assets
		'Assets',
	# Total Liabilities
		'Liabilities'
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
							if any(time in year['fp'] for time in ['Q1','Q2','Q3']):
								continue
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
	dates.reverse()

	print(dates)


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
	mag = sys.argv[2]
	CIK = get_company_CIK(ticker)
	
	# Retrieve facts json
	retreieved_facts = save_all_facts(sys.argv[1])
	if retreieved_facts:
		TAGS = getTags(ticker,f"./forms/{ticker}/{ticker}.json")
		#write_to_csv(ticker,TAGS)
	else:
		print("I have to work on facts from BS. Facts retreival failed as well. look into why.")

	writer = pd.ExcelWriter(f"./excel/{ticker}.xlsx", engine='xlsxwriter')
	TAGS.to_excel(writer, sheet_name='Tags')
	writer.save()
	writer.close()