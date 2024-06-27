from FinancialStatement import Fact, Concept, FilingFinancialStatements, LinkRelationshipSet
from FinancialStatement import ConceptEnumHandle, PeriodType

from xbrl_parse import get_defenition_URI, statement_URI

from dataclasses import dataclass, field
from typing import Dict, Any

#from Arelle.arelle.CntlrCmdLine import parseAndRun
import sys
mypath = "./Arelle"
sys.path.insert(0, mypath)
from arelle.CntlrCmdLine import parseAndRun

# TEMP IMPORTS
from files import read_forms_from_dir

@dataclass
class ArelleData:
	linkRelationshipSet: Dict[str, LinkRelationshipSet]
	facts: dict

# Returns the data that is extracted with Arelle
def parse_filing_with_arelle(zip_file):
	arg = ['-f', zip_file, "--factTable=test.txt"]
	return parseAndRun(arg)

# Fills in the statement concepts and facts
def fill_concepts_facts(statement, conceptFacts):
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
			facts = dict(),
			balance = ConceptEnumHandle.isBalanceType(modelInlineFactConcept.balance),
			periodType = ConceptEnumHandle.isPeriodType(modelInlineFactConcept.periodType),
			unitRef = ConceptEnumHandle.isCurrency(modelInlineFacts[0].unitID),
			parent = None,
			children = list(),
			modelConcept = modelInlineFactConcept
		)

		for modelInlineFact in modelInlineFacts:
			modelInlineFactContext = modelInlineFact.context
			fact = Fact(
				date = getattr(modelInlineFactContext, 'endDate', None),
				val = getattr(modelInlineFact, 'sValue', None),
				sign = getattr(modelInlineFact, 'sign', None),
				decimals = getattr(modelInlineFact, 'decimals', None),
				scale = getattr(modelInlineFact, 'scale', None),
				period = {
					'startDate': modelInlineFactContext.startDatetime.date() if concept.periodType == PeriodType.DURATION else None,
					'endDate': modelInlineFactContext.endDate
				},
				context = modelInlineFact.context,
				dimension = tuple(mem.propertyView for dim,mem in sorted(modelInlineFactContext.qnameDims.items()))
			)

			if fact.date not in concept.facts:
				concept.facts[fact.date] = [fact]
			elif fact not in concept.facts[fact.date]:
					concept.facts[fact.date].append(fact)

		statement.Concepts.append(concept)
		str_qname = f"{prefix}:{name}"
		statement.ConceptsDict[str_qname] = concept

def fill_parent_child(financialStatement):
	linkRelationshipSet = financialStatement.get_linkRelationshipSet()

	Concepts = financialStatement.get_Concepts()
	for Concept in Concepts:
		sQname = Concept.get_sQname()
		Concept_parent = linkRelationshipSet.get_type_parent('cal', sQname, financialStatement.ConceptsDict)
		Concept.parent = Concept_parent

		liConceptChildren = linkRelationshipSet.get_type_children('cal', sQname, financialStatement.ConceptsDict)
		Concept.children = liConceptChildren

	print()
	return

def populate_statement(financialStatement, arelle_data, fs_roleURI):
	fs_data = arelle_data[fs_roleURI]['facts']
	conceptFacts = fs_data["conceptFacts"]

	cal = arelle_data[fs_roleURI].get('cal', None)
	pre = arelle_data[fs_roleURI].get('pre', None)
	dim = arelle_data[fs_roleURI].get('dim', None)
	linkRelationshipSet = LinkRelationshipSet(cal, pre, dim)
	financialStatement.set_linkRelationshipSet(linkRelationshipSet)
	fill_concepts_facts(financialStatement, conceptFacts)
	fill_parent_child(financialStatement)

def retrieve_FilingFinancialStatements(cfiles):
	arelle_data = parse_filing_with_arelle(cfiles.zip)
	statement_roleURI = get_defenition_URI(cfiles.xsd, 'Statement')
	roleURIs = [roleURI for roleURI in statement_roleURI]
	
	financialStatements = FilingFinancialStatements()
	for fs in ('bs', 'is', 'cf', 'se'):
		financialStatement = financialStatements.get_financial_statement(fs)
		try:
			fs_roleURI = statement_URI(roleURIs, fs)
			populate_statement(financialStatement, arelle_data, fs_roleURI)
		except BaseException as error:
			print(f"{fs} not populated: {error}")

	return financialStatements

if __name__ == "__main__":
	#cfiles = read_forms_from_dir(f"forms/AAPL/10-K/2023-09-30")
	cfiles = read_forms_from_dir(f"forms/ORCL/10-K/2024-05-31")
	#cfiles = read_forms_from_dir(f"forms/C/10-K/2023-12-31")
	#cfiles = read_forms_from_dir(f"forms/CRWD/10-K/2024-01-31")
	filingFinancialStatements = retrieve_FilingFinancialStatements(cfiles)


	print()
