import sys
from bs4 import BeautifulSoup

from files import read_forms_from_dir, find_latest_form_dir

if __name__ == "__main__":
    ticker = sys.argv[1]
    form_type = sys.argv[2]
    directory = find_latest_form_dir(ticker,form_type)
    cfiles = read_forms_from_dir(directory)
    file_htm_xml = cfiles.htm_xml
    
    
    soup = BeautifulSoup(file_htm_xml, "xml")
    ppe = soup.find("us-gaap:PropertyPlantandCapitalizedSoftwarePropertyPlantandEquipmentTableDetails").text
    
    for line in soup:
        