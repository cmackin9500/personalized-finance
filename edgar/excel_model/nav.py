import openpyxl as xl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
import openpyxl.styles.numbers as format

CUSTOM_FORMAT_CURRENCY_ONE = '_($* #,##0.0_);[Red]_($* (#,##0.0);_($* "-"??_)'
CUSTOM_FORMAT_CURRENCY_TWO = '_($* #,##0.00_);[Red]_($* (#,##0.00);_($* "-"??_)'
letters = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ'

boldFont = Font(name='Arial',size=10, bold=True, italic=False, vertAlign=None, underline='none', strike=False, color='000000')
titleFont = Font(name='Arial',size=14, bold=True, italic=False, vertAlign=None, underline='none', strike=False, color='000000')
headingFont = Font(name='Arial',size=10, bold=True, italic=False, vertAlign=None, underline='single', strike=False, color='000000')
textFont  = Font(name='Arial',size=10, bold=False, italic=False, vertAlign=None, underline='none', strike=False, color='000000')

greyFill = PatternFill(fill_type="solid", start_color='ebebeb', end_color='ebebeb')
greyerFill = PatternFill(fill_type="solid", start_color='999997', end_color='999997')

epvFill = PatternFill(fill_type="solid", start_color="c6e6c1", end_color="c6e6c1")
greenFill = PatternFill(fill_type="solid", start_color='7eab76', end_color='7eab76')
notesFill = PatternFill(fill_type="solid", start_color='fdd966', end_color='fdd966')
greenNotesFill = PatternFill(fill_type="solid", start_color='b6d7a8', end_color='b6d7a8')

depAdjFill = PatternFill(fill_type="solid", start_color="fef2cc", end_color="fef2cc")
depAdjDataFill = PatternFill(fill_type="solid", start_color="cfe2f3", end_color="cfe2f3")

titleFill = PatternFill(fill_type="solid", start_color='ebebeb', end_color='ebebeb')
thinBorder = Side(style="thin", color="000000")
thickBorder = Side(style="thick", color="000000")
noBorder = Side(style="none")

def NAV_assets_titiles(wb_NAV, assets_info, years):
    wb_NAV.column_dimensions['B'].width = 70
    # Title Assets
    wb_NAV.cell(row=2, column=2, value="Assets")
    cell = wb_NAV["B2"]
    cell.fill = greyerFill
    cell.font = titleFont
    cell.alignment = Alignment(horizontal="center")
    cell.border = Border(left=thickBorder, top=thickBorder, right=thickBorder, bottom=thinBorder)

    # Start of Current Assets (for now, it will also add data for all Non-Current Assets)
    wb_NAV.cell(row=3, column=2, value="Current Assets")
    cell = wb_NAV["B3"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=noBorder) 

    row, col = 4, 2
    for asset_tag_info in assets_info:
        wb_NAV.cell(row=row, column=2, value=f"{asset_tag_info['Text']}")
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = greyFill
        cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
        row += 1
    
    # Titles for Non-Current Assets, PPE, and Goodwill
    # Non-Current Assets
    wb_NAV.cell(row=row, column=2, value="Non-Current Assets")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1

    # PPE
    wb_NAV.cell(row=row, column=2, value="PPE")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    for _ in range(5):
        wb_NAV.cell(row=row, column=2, value=None)
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = greyFill
        cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
        row += 1
    
    # Goodwill
    wb_NAV.cell(row=row, column=2, value="Goodwill")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    cur_year = int(years[-1])
    for i in range(len(years)+2):
        wb_NAV.cell(row=row, column=2, value=f"{str(cur_year)} SG&A")
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = greyFill
        if i == 0:
            cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=noBorder)
        else:
            cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
        cur_year -= 1
        row += 1

    wb_NAV.cell(row=row, column=2, value="Average SG&A")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=thinBorder)
    row += 1

    # Total Assets
    wb_NAV.cell(row=row, column=2, value="Total Assets")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = boldFont
    cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=noBorder)
    row += 1
    
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    return row

def NAV_liabilities_titiles(wb_NAV, liabilities_info, row, years):
    # Title Liabilities
    wb_NAV.cell(row=row, column=2, value="Liabilities")
    cell = wb_NAV[f"B{row}"]
    cell.fill = greyerFill
    cell.font = titleFont
    cell.alignment = Alignment(horizontal="center")
    cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=thinBorder)
    row += 1

    # Start of Current Liabilites (for now, it will also add data for all Non-Current Liabilities)
    wb_NAV.cell(row=row, column=2, value="Current Liabilities")
    cell = wb_NAV[f"B{row}"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=noBorder) 
    row += 1

    col = 2
    for asset_tag_info in liabilities_info:
        wb_NAV.cell(row=row, column=2, value=f"{asset_tag_info['Text']}")
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = greyFill
        cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
        row += 1
    
    # Titles for Non-Current Assets, PPE, and Goodwill
    # Non-Current Liabilities
    wb_NAV.cell(row=row, column=2, value="Non-Current Liabilities")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1

    # Contractual Obligations & Off-Balance Sheet Arrangements
    wb_NAV.cell(row=row, column=2, value="Contractual Obligations & Off-Balance Sheet Arrangements")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    for _ in range(3):
        wb_NAV.cell(row=row, column=2, value=None)
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = greyFill
        cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
        row += 1
    
    # Future Option Grants
    wb_NAV.cell(row=row, column=2, value="Future Option Grants")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = headingFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    for i in range(6):
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = greyFill
        if i % 2 == 1:
            wb_NAV.cell(row=row, column=2, value="Weighted Average Exercise Price")
        if i == 0:
            cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=noBorder)
        else:
            cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
        row += 1

    wb_NAV.cell(row=row, column=2, value="Esitmated Option Liability")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=thinBorder)
    row += 1

    # Total Liabilities
    wb_NAV.cell(row=row, column=2, value="Total Liabilities")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = greyFill
    cell.font = boldFont
    cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=thinBorder)
    row += 1

    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.border = Border(left=thickBorder, top=thinBorder, right=thickBorder, bottom=thinBorder)
    row += 1
    
    # Net Asset Value (NAV)
    wb_NAV.cell(row=row, column=2, value="Net Asset Value (NAV)")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.font = boldFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    # Shares Oustanding
    wb_NAV.cell(row=row, column=2, value="Shares Oustanding")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.font = boldFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    # NAV Share Price
    wb_NAV.cell(row=row, column=2, value="NAV Share Price")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.font = boldFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=noBorder)
    row += 1
    # Current Share Price
    wb_NAV.cell(row=row, column=2, value="Current Share Price")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.font = boldFont
    cell.border = Border(left=thickBorder, top=noBorder, right=thickBorder, bottom=thickBorder)

def fill_NAV(wb_NAV, assets_info, liabilities_info, years):
    wb_NAV.column_dimensions['B'].width = 2
    row = NAV_assets_titiles(wb_NAV, assets_info, years)
    NAV_liabilities_titiles(wb_NAV, liabilities_info, row, years)