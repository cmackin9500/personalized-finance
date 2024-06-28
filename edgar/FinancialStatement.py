from __future__ import annotations
from dataclasses import dataclass, field

from typing import List, Dict, Set, Any
from enum import Enum
from datetime import date

import sys
mypath = "./Arelle"
sys.path.insert(0, mypath)
from arelle import ModelRelationshipSet, ModelObject
#from Arelle.arelle import ModelRelationshipSet

class BalanceType(Enum):
    CREDIT = 1
    DEBIT = 2

class PeriodType(Enum):
    DURATION = 1
    INSTANT = 2

class Currency(Enum):
	USD = 1
	CAD = 2

class Sign(Enum):
	POSITIVE = 1
	NEGATIVE = 1

@dataclass
class ConceptEnumHandle:
	def isBalanceType(balanceType: str):
		if balanceType == "credit": return BalanceType.CREDIT
		elif balanceType == "debit": return BalanceType.DEBIT

	def isPeriodType(periodType: str):
		if periodType == "duration": return PeriodType.DURATION
		elif periodType == "instant": return PeriodType.INSTANT 

	def isCurrency(currency: str):
		if currency == "usd": return Currency.USD
		elif currency == "cad": return Currency.CAD

@dataclass
class Fact:
	date: date					# As-of-date of the fact Instant date or period ending date
	val: float					# Value of the fact
	sign: Sign					# Denotes if concept is positive or negative
	decimals: int				# Denotes the number of decminals it is in
	scale: int					# Denotes the scale of the concept
	period: List[date, date]	# Shows the starting date and ending date of the fact if Concept's periodType is DURATION else None
	context: date				# XBRL concept
	dimension: Set				# From and to dimention info if it exists
	isTotal: bool				# Tells us if the Fact is a total fact or not

@dataclass
class Concept:
	name: str					# Name of the concept
	prefix: str					# Prefix of the concept. Either "us-gaap" or ticker
	QName: str					# name + prefix
	label: str					# How the Concept is presented on the documetn
	abstract: bool				# Denotes if the concept is an Abstract or not
	dates: List[date]			# All of the dates that is present in the concept
	facts: Dict[date, Fact]		# All of the Facts associated with the concept
	balance: BalanceType		# Denotes if the concept is DEBIT or CREDIT
	periodType: PeriodType		# Denotes if the concept is DURATION or INSTANT
	unitRef: Currency			# Denotes the currency
	parent: Concept				# Parent Concept. This will be taken from the Calculation Linkbase.
	children: List[Concept]		# Child/children Concept(s)
	modelConcept: ModelObject
	hasTotal: bool				# Tells us if the Concept has a total value fact (meaning it is not broken down into Axis/Member without a total value reported)
	hasAxisMember: bool			# Tells us if the Concept Facts have Axis/Member Breakdown

	def get_sQname(self):
		return f"{self.prefix}:{self.name}"

@dataclass
class LinkRelationshipSet:
	cal: ModelRelationshipSet = None
	pre: ModelRelationshipSet = None
	dim: ModelRelationshipSet = None

	# Return the parent Concept of the specified Conpcet of the type (cal, pre, dim) linkbaseRelationshipSet
	def get_type_parent(self, type, sQname, dConcepts):
		typeLinkRelationshipSet = self.get_typeLinkRelationshipSet(type)
		# If there is no parent in the specified linkbase type, return None
		if typeLinkRelationshipSet is None: return None

		# Look for matching modelConcpet sQname. If matched, take the from object and return the Concept of it.
		for modelConcept, modelRel in typeLinkRelationshipSet.modelRelationshipsTo.items():
			sModelConpcetQname = modelConcept.id.split('_')[0]+':'+modelConcept.id.split('_')[1]
			if sModelConpcetQname != sQname: continue

			fromModelObject = modelRel[0].fromModelObject
			sFromObjectQname = fromModelObject.id.split('_')[0]+':'+fromModelObject.id.split('_')[1]

			return dConcepts.get(sFromObjectQname, None)

		return None
	
	def get_type_children(self, type, sQname, dConcepts):
		typeLinkRelationshipSet = self.get_typeLinkRelationshipSet(type)
		# If there is no parent in the specified linkbase type, return None
		if typeLinkRelationshipSet is None: return None

		# Look for matching modelConcpet sQname. If matched, take the to objects and return the Concepts.
		for modelConcept, modelRels in typeLinkRelationshipSet.modelRelationshipsFrom.items():
			sModelConpcetQname = modelConcept.id.split('_')[0]+':'+modelConcept.id.split('_')[1]
			if sModelConpcetQname != sQname: continue

			toConcepts = list()
			for modelRel in modelRels:
				toModelObject = modelRel.toModelObject
				sToObjectQname = toModelObject.id.split('_')[0]+':'+toModelObject.id.split('_')[1]

				if sToObjectQname in dConcepts:
					toConcepts.append(dConcepts[sToObjectQname])
			return toConcepts
		
		return None

	def get_typeLinkRelationshipSet(self, type):
		if type == 'cal': return self.get_calLinkRelationshipSet()
		elif type == 'pre': return self.get_preLinkRelationshipSet()
		elif type == 'dim': return self.get_dimLinkRelationshipSet()

	def get_preLinkRelationshipSet(self) -> ModelRelationshipSet:
		return self.pre
	
	def get_calLinkRelationshipSet(self) -> ModelRelationshipSet:
		return self.cal
	
	def get_dimLinkRelationshipSet(self) -> ModelRelationshipSet:
		return self.dim
		

@dataclass
class RoleUriLinkRelationshipSet:
	roleUri: str
	linkRelationshipSet: LinkRelationshipSet

@dataclass
class FinancialStatement:
	Concepts: List[Concept] = field(default_factory=list)
	linkRelationshipSet: LinkRelationshipSet = field(default_factory=LinkRelationshipSet)
	dConcepts: Dict[str, Concept] = field(default_factory=dict)
	dAxisMemberRelationship: Dict = field(default_factory=dict)
	dAxisMemberFacts: Dict = field(default_factory=dict)

	# CLASS FUNCTIONS
	def convert_to_ordered_dict(self) -> Dict:
		dConceptsInOrder = {}

		relationshipSet = self.linkRelationshipSet.cal
		modelRelationshipsFrom = relationshipSet.modelRelationshipsFrom
		rootConcepts = relationshipSet.rootConcepts

		# Get the first root concept and add the rest in the stack
		curConcept = (rootConcepts[0], 0)
		stack = [(rootConcept, 0) for rootConcept in rootConcepts[1:]]
		# Created visited set to avoid adding the same concept again
		visited = {curConcept}
		while curConcept is not None or stack:
			concept, depth = curConcept
			sQname = concept.vQname().prefix + ':' + concept.name
			if sQname not in dConceptsInOrder:
				dConceptsInOrder[sQname] = {}
				dConceptsInOrder[sQname]["facts"] = {}
				dConceptsInOrder[sQname]["label"] = concept.label()
				dConceptsInOrder[sQname]["depth"] = depth
			
			if sQname in self.dConcepts: 
				for date, Facts in self.dConcepts[sQname].facts.items():
					for Fact in Facts:
						if isinstance(Fact.val, int) or isinstance(Fact.val, float):
							dConceptsInOrder[sQname]["facts"][date] = max(dConceptsInOrder[sQname]["facts"].get(date,0), Fact.val)
						elif isinstance(Fact.val, str):
							dConceptsInOrder[sQname]["facts"][date] = Fact.val

			# Add the children of the current concept and add it to the front of the stack
			conceptsToAdd = []
			modelRelationshipsFromList = modelRelationshipsFrom[concept]
			for cur_modelRelationshipsFrom in modelRelationshipsFromList:
				toConcept = cur_modelRelationshipsFrom.toModelObject
				# Only add the child concept if it has not been added to the parent yet
				# TODO: This could pose an issue in the future when we introduce duplicate tags
				if toConcept not in visited:
					conceptsToAdd.append((toConcept, depth+1))
					visited.add(toConcept)
			stack = conceptsToAdd + stack

			# Get the first concept in the stack
			if stack:
				curConcept = stack.pop(0)
			else:
				curConcept = None

		return dConceptsInOrder

	# GET FUNCTIONS
	def get_sQname(self, Concept):
		return Concept.QName

	def get_Concepts(self) -> List[Concept]:
		return self.Concepts
	
	def get_concept_from_sQname(self, sQname: str) -> Concept:
		return self.dConcepts[sQname]

	def get_linkRelationshipSet(self) -> LinkRelationshipSet:
		return self.linkRelationshipSet
		
	def get_preLinkRelationshipSet(self) -> ModelRelationshipSet:
		return self.linkRelationshipSet.pre
	
	def get_calLinkRelationshipSet(self) -> ModelRelationshipSet:
		return self.linkRelationshipSet.cal
	
	def get_dimLinkRelationshipSet(self) -> ModelRelationshipSet:
		return self.linkRelationshipSet.dim
	
	# SET FUNCTIONS
	def set_linkRelationshipSet(self, linkRelationshipSet):
		self.linkRelationshipSet = linkRelationshipSet
	
@dataclass
class BalanceSheet(FinancialStatement):
	filingDate: date = None

	# CLASS FUNCTIONS

@dataclass
class IncomeStatement(FinancialStatement):
	filingDate: date = None

@dataclass
class CashFlow(FinancialStatement):
	filingDate: date = None

@dataclass
class ShareholdersEquity(FinancialStatement):
	filingDate: date = None

@dataclass
class FilingFinancialStatements:
	balanceSheet: BalanceSheet = field(default_factory=BalanceSheet)
	incomeStatement: IncomeStatement = field(default_factory=IncomeStatement)
	cashFlow: CashFlow = field(default_factory=CashFlow)
	shareholdersEquity: ShareholdersEquity = field(default_factory=ShareholdersEquity)

	# GET FUNCTIONS
	def get_financial_statement(self, fs: str):
		if fs == 'bs': return self.balanceSheet
		elif fs == 'is': return self.incomeStatement
		elif fs == 'cf': return self.cashFlow
		elif fs == 'se': return self.shareholdersEquity

# Has all of the financial statments divided by filing
@dataclass
class ConsolidatedFinancialStatements:
	filingFinancialStatements: Dict[date, FilingFinancialStatements] = field(default_factory=dict)

	#CLASS FUNCTIONS
	def get_all_filing_dates(self) -> list:
		return list(self.filingFinancialStatements.keys())
	
	def get_consolidated_fs(self, fs, override=False):
		liConsolidatedData = list()
		for date, filingFinancialStatement in self.filingFinancialStatements.items():
			financialStatement = filingFinancialStatement.get_financial_statement(fs)
			dConceptsInOrder = financialStatement.convert_to_ordered_dict()

			if liConsolidatedData == []:
				for sQname in dConceptsInOrder:
					liConsolidatedData.append(
						{
							"Qname": sQname,
							"facts": dConceptsInOrder[sQname]["facts"],
							"label": dConceptsInOrder[sQname]["label"],
							"depth": dConceptsInOrder[sQname]["depth"]
						}
					)

			else:
				index = 0
				for sQname in dConceptsInOrder:
					for i in range(len(liConsolidatedData)):
						next = False
						if sQname == liConsolidatedData[i]["Qname"]:
							liConsolidatedData[i]["facts"] = liConsolidatedData[i]["facts"] | dConceptsInOrder[sQname]["facts"]
							index = i+1
							next = True
							break
					if next: continue
					liConsolidatedData.insert(index, 
						{	
							"Qname": sQname,
							"facts": dConceptsInOrder[sQname]["facts"],
							"label": dConceptsInOrder[sQname]["label"],
							"depth": dConceptsInOrder[sQname]["depth"]
						})
		
		return liConsolidatedData