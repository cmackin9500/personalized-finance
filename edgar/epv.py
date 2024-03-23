import openpyxl as xl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font

letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
titles = ["Operating Income", "Depreciation Adjustment", "Depreciation", "CAPEX", "Growth CAPEX", "Option Expense", "Interest Earned on Cash",
          "Cash", "Interest Rate", "Pretax Earnings", "Tax Rate", "Taxes", "Earnings", "Earnings Power Value", "Cash", "Debt",
          "Total EV in Equity", "Shares Outstanding", "EPV/share", "Current Share Price"]

depreciation_adjustment = ["Premises and Equipment", "Current Year Revenue", "Prior Year Revenue", "Change in Revenue", 
                           "Depreciation and Amortization", "CAPEX", "Growth CAPEX", "Zero-growth CAPEX", "Depreciation Adjustment"]

titleFont = Font(name='Arial',size=10, bold=True, italic=False, vertAlign=None, underline='none', strike=False, color='000000')
greyFill = PatternFill(fill_type="solid", start_color='999997', end_color='999997')
titleFill = PatternFill(fill_type="solid", start_color='ebebeb', end_color='ebebeb')
thinBorder = Side(style="thin", color="000000")
thickBorder = Side(style="thick", color="000000")
noBorder = Side(style="none")

ticker = "DOMI"
path = f"./EPV/{ticker}.xlsx"	

wb = xl.Workbook()
wb.create_sheet("EPV")

row, col = 3, 2
wb_EPV = wb["EPV"]

wb_EPV.column_dimensions['B'].width = 30
wb_EPV.cell(row=2, column=2, value="")
cell = wb_EPV["B2"]
cell.fill = greyFill
cell.border = Border(left=thickBorder, top=thickBorder, right=noBorder, bottom=noBorder)

for i, value in enumerate(titles):
    wb_EPV.cell(row=row, column=col, value=value)
    cell = wb_EPV[f"B{row}"]
    cell.font = titleFont
    cell.fill = titleFill
    
    if (row == 4 or row == 7 or row == 20):
        cell.border = Border(left=thickBorder, top=noBorder, right=noBorder, bottom=thinBorder)
    elif (row == 22):
        cell.border = Border(left=thickBorder, top=noBorder, right=noBorder, bottom=thickBorder)
    else:
        cell.border = Border(left=thickBorder, top=noBorder, right=noBorder, bottom=noBorder)
    
    row += 1
wb.save(path)