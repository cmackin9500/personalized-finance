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

		name = modelInlineFactConcept.vQname().localName
		prefix = modelInlineFactConcept.vQname().prefix
		# Declare the concept and initilize it with information from modelInlineFact
		concept = Concept(
			name = name,
			prefix = prefix,
			QName = modelInlineFactConcept.qname,
			label = modelInlineFactConcept.label(),
			abstract = modelInlineFactConcept.isAbstract,
			dates = list(),
			facts = list(),
			balance = ConceptEnumHandle.isBalanceType(modelInlineFactConcept.balance),
			periodType = ConceptEnumHandle.isPeriodType(modelInlineFactConcept.periodType),
			unitRef = ConceptEnumHandle.isCurrency(modelInlineFacts[0].unitID),
			parent = None,
			chilren = list()
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
					'startDate': modelInlineFactContext.startDatetime.date() if concept.periodType == PeriodType.DURATION else None,
					'endDate': modelInlineFactContext.endDate
				},
				context = modelInlineFact.context,
				dimension = tuple(mem.propertyView for dim,mem in sorted(modelInlineFactContext.qnameDims.items()))
			)

			if fact not in concept.facts:
				concept.facts.append(fact)

		statement.Concepts.append(concept)
		str_qname = f"{prefix}:{name}"
		statement.ConceptsDict[str_qname] = concept

if __name__ == "__main__":
	#cfiles = read_forms_from_dir(f"forms/AAPL/10-K/2023-09-30")
	cfiles = read_forms_from_dir(f"forms/ORCL/10-K/2024-05-31")
	#cfiles = read_forms_from_dir(f"forms/C/10-K/2023-12-31")
	#cfiles = read_forms_from_dir(f"forms/CRWD/10-K/2024-01-31")

	zip_file = cfiles.zip
	arg = ['-f', zip_file, "--factTable=test.txt"]
	data = parseAndRun(arg)

	statement_roleURI = get_defenition_URI(cfiles.xsd, 'Statement')
	roleURIs = [roleURI for roleURI in statement_roleURI]
	
	financialStatements = FinancialStatements()
	for fs in ('bs', 'is', 'cf', 'se'):
		fs_roleURI = statement_URI(roleURIs, fs)
		fs_data = data[fs_roleURI]
		conceptFacts = fs_data["conceptFacts"]

		financialStatement = financialStatements.get_financial_statement(fs)
		financialStatement.set_linkRelationshipSet(fs_data["linkRelationshipSet"])
		fill_statement(financialStatement, conceptFacts)

		dConceptsInOrder = financialStatement.convert_to_ordered_dict({}, financialStatement.linkRelationshipSet.rootConcepts[0], set(), 0)
		print(dConceptsInOrder)
	print()
