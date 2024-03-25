import openpyxl as xl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
import openpyxl.styles.numbers as format

CUSTOM_FORMAT_CURRENCY_ONE = '_($* #,##0.0_);[Red]_($* (#,##0.0);_($* "-"??_)'
CUSTOM_FORMAT_CURRENCY_TWO = '_($* #,##0.00_);[Red]_($* (#,##0.00);_($* "-"??_)'
CUSTOM_FORMAT_PE = '0.00x'
RISK_SPREAD = '=SWITCH(B6, "Aaa", 0.63%,"AAA",0.63%,"AA",0.78%,"Aa2",0.78%,"A1",0.98%,"A+",0.98%,"A",1.08%,"A2",1.08%,"A3",1.22%,"A-",1.22%,"BBB",1.56%,"Baa2",1.56%,"Ba1",2%,"BB+",2%,"Ba2",2.4%,"BB",2.4%,"B1",3.51%,"B+",3.51%,"B2",4.21%,"B",4.21%,"B3",5.15%,"B-",5.15%,"Caa",8.2%,"CCC",8.2%,"Ca2",8.64%,"CC",8.64%,"C2",11.34%,"C",11.34%,"D2",15.12%,"D",15.12%,"AA+",0.71%,"Aa1",0.71%,"Aa3",0.88%,"AA-",0.88%,"BBB+",1.39%,"Baa1",1.39%,"BBB-",1.78%,"Baa3",1.78%,"BB-",2.96%,"Ba3",2.96%,2%)'
letters = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ'
gv_titles = ["Earnings", "Net Asset Value", "Return on Net Asset Value", "Cost of Equity", "Growth Multiple (x)", "EPV", "Growth Value", 
             "Shares outstanding", "Growth Value Per Share", "Current Share Price", "Upside"]

boldFont = Font(name='Arial',size=10, bold=True, italic=False, vertAlign=None, underline='none', strike=False, color='000000')
textFont  = Font(name='Arial',size=10, bold=False, italic=False, vertAlign=None, underline='none', strike=False, color='000000')

orangeFill = PatternFill(fill_type="solid", start_color='fde599', end_color='fde599')
orangerFill = PatternFill(fill_type="solid", start_color='f6b26b', end_color='f6b26b')
greenFill = PatternFill(fill_type="solid", start_color='b6d7a8', end_color='b6d7a8')
greenerFill = PatternFill(fill_type="solid", start_color='93c47d', end_color='93c47d')
greyFill = PatternFill(fill_type="solid", start_color='ebebeb', end_color='ebebeb')
greyerFill = PatternFill(fill_type="solid", start_color='999997', end_color='999997')
yellowFill = PatternFill(fill_type="solid", start_color='ffff01', end_color='ffff01')
notesFill = PatternFill(fill_type="solid", start_color='fdd966', end_color='fdd966')
titleFill = PatternFill(fill_type="solid", start_color='ebebeb', end_color='ebebeb')

thinBorder = Side(style="thin", color="000000")
thickBorder = Side(style="thick", color="000000")
noBorder = Side(style="none")

def wacc_titles(wb_WACC):
    for col in range(2,10):
        cell = wb_WACC[f"{letters[col]}{2}"]
        cell.border = Border(left=noBorder, top=thinBorder, right=noBorder, bottom=noBorder)
        cell = wb_WACC[f"{letters[col]}{11}"]
        cell.border = Border(left=noBorder, top=noBorder, right=noBorder, bottom=thinBorder)
    for row in range(2,12):
        cell_left = wb_WACC[f"B{row}"]
        cell_right = wb_WACC[f"I{row}"]
        if row == 2:
            cell_left.border = Border(left=thinBorder, top=thinBorder, right=noBorder, bottom=noBorder)
            cell_right.border = Border(left=noBorder, top=thinBorder, right=thinBorder, bottom=noBorder)
        elif row == 11:
            cell_left.border = Border(left=thinBorder, top=noBorder, right=noBorder, bottom=thinBorder)
            cell_right.border = Border(left=noBorder, top=noBorder, right=thinBorder, bottom=thinBorder)
        else:
            cell_left.border = Border(left=thinBorder, top=noBorder, right=noBorder, bottom=noBorder)
            cell_right.border = Border(left=noBorder, top=noBorder, right=thinBorder, bottom=noBorder)


    row = 2
    for col in range(2,10):
        wb_WACC.column_dimensions[letters[col]].width = 15
        cell = wb_WACC[f"{letters[col]}{row}"]
        if col == 2:
            wb_WACC.column_dimensions[letters[col]].width = 30
            wb_WACC.cell(row=row, column=col, value="Debt Breakdown")
            cell.font = boldFont

    row = 3
    for col in range(2,10):
        cell = wb_WACC[f"{letters[col]}{row}"]
        if col == 2:
            wb_WACC.cell(row=row, column=col, value="http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ratings.htm")

    row = 4
    for col in range(2,10):
        cell = wb_WACC[f"{letters[col]}{row}"]
        if col == 2:
            wb_WACC.cell(row=row, column=col, value="Bond Rating")
            cell.font = boldFont
        elif col == 5:
            wb_WACC.cell(row=row, column=col, value="Debt")
            cell.font = boldFont
        
    row = 5
    for col in range(2,10):
        cell = wb_WACC[f"{letters[col]}{row}"]
        if col == 2:
            wb_WACC.cell(row=row, column=col, value=None)
            cell.font = boldFont
        elif col == 5:
            wb_WACC.cell(row=row, column=col, value="Principal")
        elif col == 6:
            wb_WACC.cell(row=row, column=col, value="Term")
        elif col == 7:
            wb_WACC.cell(row=row, column=col, value="Current Year")
        elif col == 8:
            wb_WACC.cell(row=row, column=col, value="Term Left")
        elif col == 9:
            wb_WACC.cell(row=row, column=col, value="Interest Expense")

    row = 6
    for col in range(2,10):
        cell = wb_WACC[f"{letters[col]}{row}"]
        if col == 2:
            wb_WACC.cell(row=row, column=col, value=None)
        elif col == 5:
            wb_WACC.cell(row=row, column=col, value=None)
            cell.fill = yellowFill
        elif col == 6:
            wb_WACC.cell(row=row, column=col, value=None)
            cell.fill = yellowFill
        elif col == 7:
            wb_WACC.cell(row=row, column=col, value=None)
            cell.fill = yellowFill
        elif col == 8:
            wb_WACC.cell(row=row, column=col, value="=F6-G6")
            cell.fill = yellowFill
        elif col == 9:
            wb_WACC.cell(row=row, column=col, value=None)
            cell.fill = yellowFill

    row = 7
    for col in range(2,10):
        cell = wb_WACC[f"{letters[col]}{row}"]
        if col == 2:
            wb_WACC.cell(row=row, column=col, value="Risk Spread")
        elif col == 3:
            wb_WACC.cell(row=row, column=col, value=RISK_SPREAD)
            cell.number_format = format.FORMAT_PERCENTAGE_00
            cell.fill = yellowFill

    row = 7
    for col in range(2,10):
        cell = wb_WACC[f"{letters[col]}{row}"]
        if col == 2:
            wb_WACC.cell(row=row, column=col, value="Risk Spread")
        elif col == 3:
            wb_WACC.cell(row=row, column=col, value=RISK_SPREAD)
            cell.number_format = format.FORMAT_PERCENTAGE_00
            cell.fill = yellowFill