from __future__ import annotations
from dataclasses import dataclass

from typing import List, Dict
from enum import Enum
from datetime import date

import sys
mypath = "./Arelle"
sys.path.insert(0, mypath)
from arelle import ModelRelationshipSet
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

@dataclass
class Concept:
	name: str					# Name of the concept
	prefix: str					# Prefix of the concept. Either "us-gaap" or ticker
	QName: str					# name + prefix
	label: str					# How the Concept is presented on the documetn
	abstract: bool				# Denotes if the concept is an Abstract or not
	dates: List[date]			# All of the dates that is present in the concept
	facts: List[Fact]			# All of the Facts associated with the concept
	balance: BalanceType		# Denotes if the concept is DEBIT or CREDIT
	periodType: PeriodType		# Denotes if the concept is DURATION or INSTANT
	unitRef: Currency			# Denotes the currency
	parent: Concept				# Parent Concept
	chilren: List[Concept]		# Child/children Concept(s)

@dataclass
class FinancialStatement:
	Concepts: List[Concept]
	linkRelationshipSet: ModelRelationshipSet

	def __init__(
		self,
		Concepts = list(),
		linkRelationshipSet = None
	):
		self.Concepts = Concepts
		self.linkRelationshipSet = linkRelationshipSet

	def set_linkRelationshipSet(self, linkRelationshipSet):
		self.linkRelationshipSet = linkRelationshipSet

@dataclass
class FinancialStatements:
	balanceSheet: FinancialStatement
	incomeStatement: FinancialStatement
	cashFlow: FinancialStatement

	def __init__(
			self,
			balanceSheet = FinancialStatement(),
			incomeStatement = FinancialStatement(),
			cashFlow = FinancialStatement()
		):
		self.balanceSheet = balanceSheet
		self.incomeStatement = incomeStatement
		self.cashFlow = cashFlow
	
	def get_financial_statement(self, fs):
		if fs == 'bs': return self.balanceSheet
		elif fs == 'is': return self.incomeStatement
		elif fs == 'cf': return self.cashFlow
