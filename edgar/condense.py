from htmlparse import html_to_facts, Fact
import os
from dataclasses import dataclass
from edgar.files import read_forms_from_dir, find_latest_form_dir
import sys
import xbrl_functions

@dataclass
class XBRLNode:
	tag: str
	child: list
	parent: str
	val: float
	weight: float
	order: float
	date: str
	text: str

	def	__init__(self,tag,child,parent):
		self.tag = tag
		self.child = child
		self.parent = parent
		self.val = None
		self.weight = None
		self.order = None
		self.date = None
		self.text = None
	
def FS_elements(FS):
	all_fields = list()
	for row in FS:
		node = row[0]
		if node.parent and node.parent not in all_fields:
			all_fields.append(node.parent)
		if node.tag and node.tag not in all_fields:
			all_fields.append(node.tag)
	return all_fields