from bs4 import BeautifulSoup
import bs4
import sys
from dataclasses import dataclass

from util import file_management as fm

# Fundamental information holder
@dataclass
class HTMLFact:
	tag: str
	parent: str
	child: list()
	val: float
	date: str
	text: str

	def __iter__(self):
		yield "tag", self.tag
		yield "parent", self.parent
		yield "val", self.val
		yield "text", self.text

# Converts an HTML cell into a value based upon attributes and text
def cell_to_float(cell, sign):
	text = cell.getText().replace("$", "")
	ix = cell.find("ix:nonfraction")

	# If no ix element
	if ix == -1:
		return 0

	try:
		if sign:
			return sign * round(10 ** float(ix["scale"]) * float(text.replace(",", "")\
				.replace("(", "")\
				.replace(")", "")\
				.replace("\xa0", "")), 3)
	except:
		return 0

	try:
		return round(10 ** float(ix["scale"]) * float(text.replace(",", "")\
				.replace("(", "-")\
				.replace(")", "")\
				.replace("\xa0", "")), 3)
	except:
		return 0


# Converts an HTML table to rows of facts
def tab_to_rows(tab, ctx_map, fs_fields):
	tbody = tab.find("tbody")
	children = tbody if tbody else tab.contents 

	rows = []

	for row in children:
		data = []
		i = 0
		text = ""
		for cell in row:
			if isinstance(cell, bs4.element.NavigableString):
				continue

			if isinstance(cell, str):
				continue

			if i == 0:
				i += 1
				text = cell.getText()
				continue

			ix = cell.find("ix:nonfraction")
			if ix == None or ix == -1:
				continue 

			# Determine sign of cell
			sign = None
			if ix["name"] in fs_fields:
				sign = fs_fields[ix["name"]].weight
			elif "sign" in ix:
				sign = int(ix["sign"] + "1")

			data.append(HTMLFact(ix["name"],
					None,
					[],
					cell_to_float(cell, sign),
					ctx_map[ix["contextref"]],
					text))
			i += 1

		if len(data) == 0:
			continue

		rows.append(data)

	return rows

# xbrli:endDate
# xbrli:instant
def contexts_to_map(context_list):
	ctx_map = {}
	for ctx in context_list:
		end_date = ctx.find("xbrli:enddate")
		instant = ctx.find("xbrli:instant")
		date_elem = end_date if end_date else instant
		#if date_elem == None:
		#	continue

		ctx_map[ctx["id"]] = date_elem.getText()

	return ctx_map

# Returns an list of tables which consists of a list of lists of HTMLFact objects
# Requires the HTML version of the company form submission
# Only the column data (ix:nonfraction) is extracted
def html_to_facts(html,xml,fs_fields):
	dom = BeautifulSoup(html)
	xml_dom = BeautifulSoup(xml)
	tables = dom.find_all("table")

	# Should grab context elems xbrli:context
	contexts = dom.find_all("xbrli:context")
	if contexts is None:
		contexts = xml_dom.find_all("xbrli:context")


	ctx_map = contexts_to_map(xml_dom)
	all_facts = []
	for tab in tables:
		new_facts = tab_to_rows(tab, ctx_map, fs_fields)
		if len(new_facts) == 0:
			continue
		
		all_facts.append(new_facts)
	return all_facts

	
if __name__ == '__main__':
	data = read_file(sys.argv[1])

	facts = html_to_facts(data)
	for i, table in enumerate(facts):
		print("\nTable {}: {} rows".format(i, len(table)))
		for row in table:
			print(row)
			continue
