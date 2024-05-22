import webbrowser
import sys

from edgar_retrieve import get_company_CIK

ticker = sys.argv[1]
CIK = get_company_CIK(ticker)
url = f"https://www.sec.gov/edgar/browse/?CIK={CIK}"

# MacOS
chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

webbrowser.get(chrome_path).open(url)