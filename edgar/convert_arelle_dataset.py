from FinancialStatement import Fact, Concept, FinancialStatements
from FinancialStatement import ConceptEnumHandle, PeriodType

from xbrl_parse import get_defenition_URI, statement_URI

#from Arelle.arelle.CntlrCmdLine import parseAndRun
import sys
mypath = "./Arelle"
sys.path.insert(0, mypath)
from arelle.CntlrCmdLine import parseAndRun

# TEMP IMPORTS
from files import read_forms_from_dir

def fill_statement(statement, conceptFacts):
	for Qname in conceptFacts:
		modelInlineFacts = conceptFacts[Qname]
		# Continue to next conceptFact if there is no information to extract
		if len(modelInlineFacts) == 0: continue
		modelInlineFactConcept = modelInlineFacts[0].concept

		# Declare the concept and initilize it with information from modelInlineFact
		concept = Concept(
			name = modelInlineFactConcept.vQname().localName,
			prefix = modelInlineFactConcept.vQname().prefix,
			QName = modelInlineFactConcept.qname,
			label = modelInlineFactConcept.label(),
			abstract = modelInlineFactConcept.isAbstract,
			dates = list(),
			facts = list(),
			balance = ConceptEnumHandle.isBalanceType(modelInlineFactConcept.balance),
			periodType = ConceptEnumHandle.isPeriodType(modelInlineFactConcept.periodType),
			unitRef = ConceptEnumHandle.isCurrency(modelInlineFacts[0].unitID),
			parent = None,
			chilren = list(),
		)
		for modelInlineFact in modelInlineFacts:
			modelInlineFactContext = modelInlineFact.context

			fact = Fact(
				date = modelInlineFactContext.endDate,
				val = modelInlineFact.sValue,
				sign = modelInlineFact.sign,
				decimals = modelInlineFact.decimals,
				scale = modelInlineFact.scale,
				period = {
					'startDate': modelInlineFactContext.startDatetime.now().date() if concept.periodType == PeriodType.DURATION else None,
					'endDate': modelInlineFactContext.endDate
				},
				context = modelInlineFact.contextID
			)

			concept.facts.append(fact)

		statement.Concepts.append(concept)

if __name__ == "__main__":
	cfiles = read_forms_from_dir(f"forms/AAPL/10-K/2023-09-30")
	zip_file = cfiles.zip
	arg = ['-f', zip_file, "--factTable=test.txt"]
	data = parseAndRun(arg)

	statement_roleURI = get_defenition_URI(cfiles.xsd, 'Statement')
	roleURIs = [roleURI for roleURI in statement_roleURI]
	
	financialStatements = FinancialStatements()
	for fs in ('bs', 'is', 'cf'):
		fs_roleURI = statement_URI(roleURIs, fs)
		fs_data = data[fs_roleURI]
		conceptFacts = fs_data["conceptFacts"]

		financialStatement = financialStatements.get_financial_statement(fs)
		financialStatement.set_linkRelationshipSet(fs_data["linkRelationshipSet"])
		fill_statement(financialStatement, conceptFacts)
	
	print()
