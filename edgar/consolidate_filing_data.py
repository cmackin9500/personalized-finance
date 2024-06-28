from FinancialStatement import ConsolidatedFinancialStatements
from convert_arelle_dataset import retrieve_FilingFinancialStatements

from edgar_retrieve import download_forms
import files

import datetime

if __name__ == "__main__":
	#ticker = input("Enter ticker: ")
	ticker = "AAPL"
	directories = files.get_parsing_directories(ticker)
	
	consolidatedFinancialStatements = ConsolidatedFinancialStatements()
	for str_date in directories:
		d = str_date.split('-')
		date = datetime.date(int(d[0]),int(d[1]),int(d[2]))

		cfiles = files.read_forms_from_dir(f"forms/{ticker}/10-K/{str_date}")
		filingFinancialStatements = retrieve_FilingFinancialStatements(cfiles)

		consolidatedFinancialStatements.filingFinancialStatements[date] = filingFinancialStatements

	liConsolidatedData = consolidatedFinancialStatements.get_consolidated_fs('bs', override=False)
	print()
		