from FinancialStatement import Fact, Concept, FilingFinancialStatements, LinkRelationshipSet
from FinancialStatement import ConceptEnumHandle, PeriodType

from xbrl_parse import get_defenition_URI, statement_URI

from dataclasses import dataclass, field
from typing import Dict, Any
import datetime

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
			modelConcept = modelInlineFactConcept,
			hasTotal = False,
			hasAxisMember = False
		)

		for modelInlineFact in modelInlineFacts:
			modelInlineFactContext = modelInlineFact.context
			fact = Fact(
				sConceptQname = f"{concept.prefix}:{concept.name}",
				date = getattr(modelInlineFactContext, 'endDate', None),
				val = getattr(modelInlineFact, 'sValue', None),
				balance = concept.balance,
				sign = getattr(modelInlineFact, 'sign', None),
				decimals = getattr(modelInlineFact, 'decimals', None),
				scale = getattr(modelInlineFact, 'scale', None),
				period = {
					'startDate': modelInlineFactContext.startDatetime.date() if concept.periodType == PeriodType.DURATION else None,
					'endDate': modelInlineFactContext.endDate
				},
				context = modelInlineFact.context,
				dimension = tuple(mem.propertyView for dim,mem in sorted(modelInlineFactContext.qnameDims.items())),
				isTotal = True,
				calParentFact = None,
				calChildrenFacts = list()			)
			
			if fact.date not in concept.dates:
				concept.dates.append(fact.date)
			# Change isTotal to False if Fact dimention is not empty (means it is an Axis/Member breakdown)
			# It also means that the concept has a Axis/Member breakdown amongst the Facts
			if len(fact.dimension) != 0: 
				fact.isTotal = False
				concept.hasAxisMember = True
			# If there is a total fact, change the concept hasTotal attribute to true
			elif len(fact.dimension) == 0 and not concept.hasTotal:
				concept.hasTotal = True

			if fact.date not in concept.facts:
				concept.facts[fact.date] = [fact]
			elif fact not in concept.facts[fact.date]:
					concept.facts[fact.date].append(fact)

		statement.Concepts.append(concept)
		str_qname = f"{prefix}:{name}"
		statement.dConcepts[str_qname] = concept
		

def fill_parent_child(financialStatement):
	linkRelationshipSet = financialStatement.get_linkRelationshipSet()

	Concepts = financialStatement.get_Concepts()
	for Concept in Concepts:
		sQname = Concept.get_sQname()
		Concept_parent = linkRelationshipSet.get_type_parent('cal', sQname, financialStatement.dConcepts)
		if Concept_parent is None:
			Concept_parent = linkRelationshipSet.get_type_parent('dim', sQname, financialStatement.dConcepts)
		Concept.parent = Concept_parent

		liConceptChildren = linkRelationshipSet.get_type_children('cal', sQname, financialStatement.dConcepts)
		Concept.children = liConceptChildren

	return

def fill_AxisMemberFact(financialStatement):
	Concepts = financialStatement.get_Concepts()
	for Concept in Concepts:
		for date in Concept.facts:
			for Fact in Concept.facts[date]:
				if date not in financialStatement.dAxisMemberFacts:
					financialStatement.dAxisMemberFacts[date] = dict()
				dimensions = Fact.dimension
				if len(dimensions) == 0: continue
				for Axis, Member in dimensions:
					if Axis not in financialStatement.dAxisMemberFacts[date]:
						financialStatement.dAxisMemberFacts[date][Axis] = dict()
					if Member not in financialStatement.dAxisMemberFacts[date][Axis]:
						financialStatement.dAxisMemberFacts[date][Axis][Member] = [Fact]
					elif Member in financialStatement.dAxisMemberFacts[date][Axis]:
						financialStatement.dAxisMemberFacts[date][Axis][Member].append(Fact)
	return

def fill_AxisMemberRelationship(financialStatement):
	dimLinkRelationshipSet = financialStatement.get_dimLinkRelationshipSet()
	if dimLinkRelationshipSet is None: 
		return
	rootConcepts = dimLinkRelationshipSet.rootConcepts
	modelRelationshipsFrom = dimLinkRelationshipSet.modelRelationshipsFrom

	# Get the first root concept and add the rest in the stack
	curConcept = (rootConcepts[0], financialStatement.dAxisMemberRelationship)
	stack = [(rootConcept, financialStatement.dAxisMemberRelationship) for rootConcept in rootConcepts[1:]]
	# Created visited set to avoid adding the same concept again
	visited = {curConcept[0]}
	while curConcept is not None or stack:
		concept, dCur = curConcept
		if any(concept.label().endswith(ending) for ending in ["[Axis]", "[Domain]", "[Member]"]):
			sQname = f"{concept.vQname().prefix}:{concept.vQname().localName}"
			
			if len(modelRelationshipsFrom[concept]) == 0:
				dCur[sQname] = "end"
			else:
				dCur[sQname] = {}
				dCur = dCur[sQname]

		# Add the children of the current concept and add it to the front of the stack
		conceptsToAdd = []
		modelRelationshipsFromList = modelRelationshipsFrom[concept]
		for cur_modelRelationshipsFrom in modelRelationshipsFromList:
			toConcept = cur_modelRelationshipsFrom.toModelObject
			if toConcept not in visited:
				conceptsToAdd.append((toConcept, dCur))
				visited.add(toConcept)
		stack = conceptsToAdd + stack

		# Get the first concept in the stack
		if stack:
			curConcept = stack.pop(0)
		else:
			curConcept = None

	return 

def fill_calRelationship(financialStatement):
	calLinkRelationshipSet = financialStatement.get_calLinkRelationshipSet()
	if calLinkRelationshipSet is None: 
		return
	rootConcepts = calLinkRelationshipSet.rootConcepts
	for rootConcept in rootConcepts:
		name = rootConcept.vQname().localName
		prefix = rootConcept.vQname().prefix
		financialStatement.calRootConcepts.append(f"{prefix}:{name}")
	
	modelRelationshipsFrom = calLinkRelationshipSet.modelRelationshipsFrom

	# Get the first root concept and add the rest in the stack
	curConcept = rootConcepts[0]
	stack = [rootConcept for rootConcept in rootConcepts[1:]]
	# Created visited set to avoid adding the same concept again
	visited = {curConcept}
	while curConcept is not None or stack:
		sQname = f"{curConcept.vQname().prefix}:{curConcept.vQname().localName}"

		financialStatement.dCalRelationship[sQname] = list()
		# Add the children of the current concept and add it to the front of the stack
		conceptsToAdd = []
		modelRelationshipsFromList = modelRelationshipsFrom[curConcept]
		for cur_modelRelationshipsFrom in modelRelationshipsFromList:
			toConcept = cur_modelRelationshipsFrom.toModelObject
			name = toConcept.vQname().localName
			prefix = toConcept.vQname().prefix
			financialStatement.dCalRelationship[sQname].append(f"{prefix}:{name}")
			if toConcept not in visited:
				conceptsToAdd.append(toConcept)
				visited.add(toConcept)
		stack = conceptsToAdd + stack

		# Get the first concept in the stack
		if stack:
			curConcept = stack.pop(0)
		else:
			curConcept = None

	return 

def get_Facts_tree(financialStatement):
	Concepts = financialStatement.get_Concepts()
	if financialStatement.get_calLinkRelationshipSet():
		rootConcepts = financialStatement.get_calLinkRelationshipSet().rootConcepts
	elif financialStatement.get_dimLinkRelationshipSet():
		rootConcepts = financialStatement.get_dimLinkRelationshipSet().rootConcepts
	else:
		print("dim and cal linkRelationshipSet does not exist.")
		return None

	for Concept in Concepts:
		for date in Concept.facts:
			TotalFact = Concept.get_total_Fact(date, True)
			print()

def dfs(financialStatement, date, parentFact, curFact, curConcept, sMemberQname, visited):
	if curConcept is None or curFact in visited or curFact is None:
		return
	
	visited.append(curFact)
	sCurQname = f"{curConcept.prefix}:{curConcept.name}"
	curFact.calParentFact = parentFact

	# If the current concept has a total Fact but not Axis-Member breakdown, we will just set the children to curFact.children and dfs
	if curConcept.hasTotal and not curConcept.hasAxisMember:
		for sChildQname in financialStatement.dCalRelationship[sCurQname]:
			childConcept = financialStatement.dConcepts[sChildQname]
			childTotalFact = childConcept.get_total_Fact(date)

			if childTotalFact is not None:
				curFact.calChildrenFacts.append(childTotalFact)

			dfs(financialStatement, date, curFact, childTotalFact, childConcept, None, visited)
	
	# If current concept has a total AND axis memebrs, split them by the different axis members
	elif curConcept.hasTotal and curConcept.hasAxisMember:
		if not sMemberQname:
			liNonTotalFacts = curConcept.get_not_isTotal_facts(date)
			for nonTotalFact in liNonTotalFacts:
				curFact.calChildrenFacts.append(nonTotalFact)
				
				dfs(financialStatement, date, curFact, nonTotalFact, curConcept, nonTotalFact.get_member_Qname(), visited)
		
		elif sMemberQname:
			if financialStatement.dCalRelationship[sCurQname] != []:
				for sChildQname in financialStatement.dCalRelationship[sCurQname]:
					childConcept = financialStatement.dConcepts.get(sChildQname, None)
					if childConcept is None:
						continue
					childMemberFact = childConcept.get_member_fact(date, sMemberQname)

					if childMemberFact is None:
						continue

					curFact.calChildrenFacts.append(childMemberFact)
					if curFact.get_member_Qname() == sMemberQname and financialStatement.dCalRelationship[childMemberFact.sConceptQname] != []:
						dfs(financialStatement, date, curFact, childMemberFact, childConcept, sMemberQname, visited)

	return

def populate_statement(financialStatement, arelle_data, fs_roleURI):
	fs_data = arelle_data[fs_roleURI]['facts']
	conceptFacts = fs_data["conceptFacts"]

	cal = arelle_data[fs_roleURI].get('cal', None)
	pre = arelle_data[fs_roleURI].get('pre', None)
	dim = arelle_data[fs_roleURI].get('dim', None)
	linkRelationshipSet = LinkRelationshipSet(cal, pre, dim)
	financialStatement.set_linkRelationshipSet(linkRelationshipSet)
	fill_AxisMemberRelationship(financialStatement)
	fill_concepts_facts(financialStatement, conceptFacts)
	fill_parent_child(financialStatement)
	fill_AxisMemberFact(financialStatement)

	fill_calRelationship(financialStatement)

	for sRootConceptQname in financialStatement.calRootConcepts:
		curConcept = financialStatement.dConcepts[sRootConceptQname]
		for date in curConcept.dates:
			rootTotalFact = curConcept.get_total_Fact(date)
			if rootTotalFact is None:
				rootTotalFact = curConcept.get_total_Fact(date, True)
				if rootTotalFact is not None:
					curConcept.facts[date].append(rootTotalFact)
					curConcept.hasTotal = True
				else:
					print('rootTotalFact failure.')

			if date not in financialStatement.calRootFacts:
				financialStatement.calRootFacts[date] = [rootTotalFact]
			else:
				financialStatement.calRootFacts[date].append(rootTotalFact)
			dfs(financialStatement, date, None, rootTotalFact, curConcept, None, list())
			print()
	#fill_Fact_parent_child(financialStatement)

def retrieve_FilingFinancialStatements(cfiles):
	arelle_data = parse_filing_with_arelle(cfiles.zip)
	statement_roleURI = get_defenition_URI(cfiles.xsd, 'Statement')
	roleURIs = [roleURI for roleURI in statement_roleURI]
	
	financialStatements = FilingFinancialStatements()
	for fs in ('bs', 'is', 'cf', 'se'):
		financialStatement = financialStatements.get_financial_statement(fs)
		fs_roleURI = statement_URI(roleURIs, fs)
		populate_statement(financialStatement, arelle_data, fs_roleURI)

	return financialStatements

if __name__ == "__main__":
	#cfiles = read_forms_from_dir(f"forms/AAPL/10-K/2023-09-30")
	cfiles = read_forms_from_dir(f"forms/ORCL/10-K/2024-05-31")
	#cfiles = read_forms_from_dir(f"forms/C/10-K/2023-12-31")
	#cfiles = read_forms_from_dir(f"forms/CRWD/10-K/2024-01-31")
	filingFinancialStatements = retrieve_FilingFinancialStatements(cfiles)


	print()
