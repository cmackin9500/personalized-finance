from dataclasses import dataclass
from util import file_management as fm
import os
import sys
from typing import List, Dict, Set
from datetime import date

@dataclass
class CompanyFiles:
    html: str
    pre: str
    xsd: str
    cal: str
    htm_xml: str
    zip: str

def find_all_form_dir(ticker, form_type) -> list:
    return os.listdir(f"./forms/{ticker}/{form_type}")

# Retrieves the latest data dir for a company and form type
def get_latest_form_dir(ticker, form_type):
    dirs = find_all_form_dir(ticker, form_type)
    dirs.sort(reverse=True)
    return f"forms/{ticker}/{form_type}/{dirs[0]}"

def get_10k_directories(ticker):
    dir = sorted(find_all_form_dir(ticker, '10-K'))
    return list(filter((".DS_Store").__ne__, dir))

def get_10q_directories(ticker):
    dir = sorted(find_all_form_dir(ticker, '10-Q'))
    return list(filter((".DS_Store").__ne__, dir))

def get_parsing_directories(ticker, parsing_method='k'):
    directory_10K = get_10k_directories(ticker)
    directory_10Q = get_10q_directories(ticker)
    
    # Get paths to every single 10-K and 10-Q filings
    if parsing_method == 'q':
            return sorted(directory_10Q + directory_10K)

    # Get paths to every 10-K and the all of the 10-Q filings past the most recent 10-K
    elif parsing_method == 'r':
        directory = directory_10K + []	# Just adding + [] so it will not be a reference to directory_cfiles_10K
        for i, cfile_10Q in enumerate(directory_10Q):
            if cfile_10Q > directory_10K[-1]:
                directory += directory_10Q[i:]
                break
        return directory

    # Get path to the most recent filing only
    elif parsing_method == 'l':
        return directory_10K[-1:] if directory_10K[-1] > directory_10Q[-1] else directory_10Q[-1:]

    # Otherwise just parse the 10-Ks only
    return directory_10K

# Reads all company forms from a data directory
def read_forms_from_dir(data_dir):
    files = os.listdir(data_dir)
    xsd = ""
    html = ""
    pre = ""
    htm_xml = ""
    cal = ""
    zip = ""

    for file in files:
        if file.endswith(".zip"):
            zip = data_dir + "/" + file
        if file.endswith(".xsd"):
            xsd = fm.read_file(data_dir + "/" + file)
        if file.endswith("pre.xml"):
            pre = fm.read_file(data_dir + "/" + file)
        if file.endswith(".html"):
            html = fm.read_file(data_dir + "/" + file)
        if file.endswith("cal.xml"):
            cal = fm.read_file(data_dir + "/" + file)       
        if file.endswith(".xml") and not any(t in file for t in ["cal", "pre", "def", "lab"]):
            htm_xml = fm.read_file(data_dir + "/" + file)

    return CompanyFiles(html, pre, xsd, cal, htm_xml, zip)


def find_index_form_dir(ticker, form_type, date):
    return f"forms/{ticker}/{form_type}/{date}"

if __name__ == "__main__":
    find_all_form_dir(sys.argv[1], sys.argv[2])