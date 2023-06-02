from dataclasses import dataclass
from util import file_management as fm
import os
import sys

@dataclass
class CompanyFiles:
    html: str
    pre: str
    xsd: str
    cal: str

# Reads all company forms from a data directory
def read_forms_from_dir(data_dir):
    files = os.listdir(data_dir)
    xsd = ""
    html = ""
    pre = ""

    for file in files:
        if file.endswith(".xsd"):
            xsd = fm.read_file(data_dir + "/" + file)
        if file.endswith("pre.xml"):
            pre = fm.read_file(data_dir + "/" + file)
        if file.endswith(".html"):
            html = fm.read_file(data_dir + "/" + file)
        if file.endswith("cal.xml"):
            cal = fm.read_file(data_dir + "/" + file)       

    return CompanyFiles(html, pre, xsd, cal)

def find_all_form_dir(ticker, form_type) -> list():
    return os.listdir(f"forms/{ticker}/{form_type}")


# Retrieves the latest data dir for a company and form type
def find_latest_form_dir(ticker, form_type):
    dirs = find_all_form_dir(ticker, form_type)
    dirs.sort(reverse=True)

    return f"forms/{ticker}/{form_type}/{dirs[0]}"

if __name__ == "__main__":
    find_all_form_dir(sys.argv[1], sys.argv[2])