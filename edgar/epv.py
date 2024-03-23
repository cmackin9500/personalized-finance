import openpyxl as xl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font

titleFont = Font(name='Arial',size=10, bold=True, italic=False, vertAlign=None, underline='none', strike=False, color='000000')
titleFill = PatternFill(fill_type="solid", start_color='dedede', end_color='dedede')

ticker = "DOMI"
path = f"./EPV/{ticker}.xlsx"	

wb = xl.Workbook()
wb.create_sheet("EPV")

row, col = 3, 2
wb_EPV = wb["EPV"]
wb_EPV.cell(row=row, column=col, value="Operating Income")
b3 = wb_EPV['B3']
b3.font = titleFont
b3.fill = titleFill
wb.save(path)