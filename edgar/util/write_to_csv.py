# overrides for write_to_csv
def write_to_csv(ticker,NAV,BS,IS,CF,TAGS,EPV):
	writer = pd.ExcelWriter(f"./excel/{ticker}.xlsx", engine='xlsxwriter')
	NAV.to_excel(writer, sheet_name='NAV')
	BS.to_excel(writer, sheet_name='Balance Sheet')
	IS.to_excel(writer, sheet_name='Income Statement')
	CF.to_excel(writer, sheet_name='Cash Flow')
	TAGS.to_excel(writer, sheet_name='Tags')
	EPV.to_excel(writer, sheet_name='EPV')
	writer.save()

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