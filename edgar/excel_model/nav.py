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
purpleFill = PatternFill(fill_type="solid", start_color='d9d2e9', end_color='d9d2e9')
purplerFill = PatternFill(fill_type="solid", start_color='b4a7d7', end_color='b4a7d7')
blueFill = PatternFill(fill_type="solid", start_color='c9dbf8', end_color='c9dbf8')
bluerFill = PatternFill(fill_type="solid", start_color='a4c2f4', end_color='a4c2f4')
greenFill = PatternFill(fill_type="solid", start_color='b7d7a8', end_color='b7d7a8')
greenerFill = PatternFill(fill_type="solid", start_color='93c47d', end_color='93c47d')

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
    return row

def NAV_assets_data(wb_NAV, assets_info, col, end_row, date):
    wb_NAV.column_dimensions[letters[col]].width = 15
    year = date.split('-')[0]
    # Title Assets
    wb_NAV.cell(row=2, column=col, value=f"FY {year}")
    cell = wb_NAV[f"{letters[col]}2"]
    cell.fill = purplerFill
    cell.font = boldFont
    cell.alignment = Alignment(horizontal="center")
    cell.border = Border(left=thickBorder, top=thickBorder, right=noBorder, bottom=thinBorder)

    # Start of Current Assets (for now, it will also add data for all Non-Current Assets)
    cell = wb_NAV[f"{letters[col]}3"]
    cell.fill = purplerFill
    cell.border = Border(left=thickBorder, top=thinBorder, right=noBorder, bottom=noBorder) 

    row = 4
    for asset_tag_info in assets_info:
        value = asset_tag_info[date] if date in asset_tag_info else 0
        wb_NAV.cell(row=row, column=col, value=value)
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = purpleFill
        cell.border = Border(left=thickBorder, top=noBorder, right=noBorder, bottom=noBorder)
        cell.number_format = CUSTOM_FORMAT_CURRENCY_ONE
        row += 1
    
    for _ in range(row, end_row):
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = purpleFill
        if row == end_row-2:
            cell.border = Border(left=thickBorder, top=thinBorder, right=noBorder, bottom=noBorder)
        else:
            cell.border = Border(left=thickBorder, top=noBorder, right=noBorder, bottom=noBorder)
        row += 1

def NAV_liabilities_data(wb_NAV, liabilities_info, col, start_row, end_row, date):
    wb_NAV.column_dimensions[letters[col]].width = 15
    row = start_row
    # Title Liabilities
    year = str(date.split('-')[0])
    wb_NAV.cell(row=row, column=col, value=f"FY {year}")
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = purplerFill
    cell.font = boldFont
    cell.alignment = Alignment(horizontal="center")
    cell.border = Border(left=thickBorder, top=thickBorder, right=noBorder, bottom=thinBorder)
    row += 1

    # Start of Current Liabilities (for now, it will also add data for all Non-Current Liabilities)
    cell = wb_NAV[f"{letters[col]}{row}"]
    cell.fill = purplerFill
    cell.border = Border(left=thickBorder, top=thinBorder, right=noBorder, bottom=noBorder) 

    row += 1
    for liabilities_tag_info in liabilities_info:
        value = liabilities_tag_info[date] if date in liabilities_tag_info else 0
        wb_NAV.cell(row=row, column=col, value=value)
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = purpleFill
        cell.border = Border(left=thickBorder, top=noBorder, right=noBorder, bottom=noBorder)
        cell.number_format = CUSTOM_FORMAT_CURRENCY_ONE
        row += 1
    
    for _ in range(row, end_row):
        cell = wb_NAV[f"{letters[col]}{row}"]
        cell.fill = purpleFill
        if row == end_row-2:
            cell.border = Border(left=thickBorder, top=thinBorder, right=noBorder, bottom=noBorder)
        else:
            cell.border = Border(left=thickBorder, top=noBorder, right=noBorder, bottom=noBorder)
        row += 1

def fill_NAV(wb_NAV, assets_info, liabilities_info, dates):
    years = [date.split('-')[0] for date in dates]
    wb_NAV.column_dimensions['B'].width = 2
    asset_row = NAV_assets_titiles(wb_NAV, assets_info, years)
    liability_row = NAV_liabilities_titiles(wb_NAV, liabilities_info, asset_row, years)

    for i, date in enumerate(dates):
        NAV_assets_data(wb_NAV, assets_info, 3+i, asset_row, date)
        NAV_liabilities_data(wb_NAV, liabilities_info, 3+i, asset_row, liability_row, date)

