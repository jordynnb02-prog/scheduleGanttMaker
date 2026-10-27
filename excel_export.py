
from io import BytesIO
from datetime import datetime, date, timedelta

from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Border, Side, Alignment
)
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension
import re


COLORS = [
    "3B82F6",  # Blue
    "8B5CF6",  # Purple
    "F59E0B",  # Orange
    "0D9488",  # Teal
    "EC4899",  # Pink
    "64748B",  # Gray
]

DARK = "1E293B"
LIGHT = "F1F5F9"
GRID = "DCE3EC"
WHITE = "FFFFFF"
def lightenColor(hexColor, amount=0.65):
    rgb = [int(hexColor[i:i+2], 16) for i in (0, 2, 4)]

    lighter = [
        round(channel + (255 - channel) * amount)
        for channel in rgb
    ]

    return "".join(f"{channel:02X}" for channel in lighter)

def formatSectionName(name):
    match = re.search(r"\((\d+)\)\s*$", name)

    if match:
        return f"Section {match.group(1)}"

    return name


def toDate(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def createExcelGantt(selectedGroups, so_number="Project"):

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Gantt Chart"

    sheet.sheet_view.showGridLines = False
    sheet.sheet_view.showOutlineSymbols = True
    sheet.sheet_properties.outlinePr.summaryBelow = False

    # ------------------------------------------
    # PREPARE SCHEDULE DATA
    # ------------------------------------------

    groups = []
    all_dates = []

    for index, (section, tasks) in enumerate(selectedGroups.items()):

        valid = []

        for task in tasks:
            start = toDate(task.get("Start"))
            end = toDate(task.get("End"))

            if start is None or end is None or end < start:
                continue

            valid.append({
                "name": str(task["Phase"]).strip(),
                "start": start,
                "end": end
            })

            all_dates.extend([start, end])

        if valid:
            groups.append({
                "name": formatSectionName(section),
                "color": COLORS[index % len(COLORS)],
                "tasks": sorted(valid, key=lambda t: t["start"])
            })

    if not all_dates:
        raise ValueError("No valid schedule dates found.")

    first = min(all_dates)
    last = max(all_dates)

    # Start the weekly timeline on Monday
    first_week = first - timedelta(days=first.weekday())

    # ------------------------------------------
    # TITLE AND HEADERS
    # ------------------------------------------

    sheet.merge_cells("A1:C2")
    title = sheet["A1"]
    title.value = f"{so_number} - PROJECT GANTT CHART"
    title.font = Font(size=18, bold=True, color=WHITE)
    title.fill = PatternFill("solid", fgColor=DARK)
    title.alignment = Alignment(vertical="center")

    sheet["A3"] = "Schedule Start"
    sheet["B3"] = first
    sheet["B3"].number_format = "mmm d, yyyy"

    sheet["A4"] = "Schedule Finish"
    sheet["B4"] = last
    sheet["B4"].number_format = "mmm d, yyyy"

    headers = {
        "A6": "Activity / Section",
        "B6": "Start",
        "C6": "Finish"
    }

    for cell, value in headers.items():
        sheet[cell] = value

    # ------------------------------------------
    # WEEKLY TIMELINE
    # ------------------------------------------

    current = first_week
    column = 4
    week_number = 1

    while current <= last:

        letter = get_column_letter(column)

        sheet.cell(5, column, f"W{week_number}")
        sheet.cell(6, column, current)
        sheet.cell(6, column).number_format = "mmm d"

        sheet.column_dimensions[letter].width = 11

        for header_row in (5, 6):
            cell = sheet.cell(header_row, column)
            cell.fill = PatternFill("solid", fgColor=DARK)
            cell.font = Font(color=WHITE, bold=True, size=10)
            cell.alignment = Alignment(horizontal="center")

        # Highlight the week containing today
        if current <= date.today() < current + timedelta(days=7):
            for header_row in (5, 6):
                sheet.cell(header_row, column).fill = PatternFill(
                    "solid", fgColor="EAB308"
                )
                sheet.cell(header_row, column).font = Font(
                    color=DARK, bold=True
                )

        current += timedelta(days=7)
        column += 1
        week_number += 1

    last_column = column - 1
    last_letter = get_column_letter(last_column)

    # ------------------------------------------
    # CREATE SECTION AND TASK ROWS
    # ------------------------------------------

    for group in groups:

        color = group["color"]

        # Major section heading
        sheet.append([group["name"].upper()])
        section_row = sheet.max_row

        first_task_row = section_row + 1

        for task in group["tasks"]:
            sheet.append([
                "    " + task["name"],
                task["start"],
                task["end"]
            ])

        last_task_row = sheet.max_row

        # Section dates are calculated from its tasks
        sheet.cell(
            section_row, 2,
            f"=MIN(B{first_task_row}:B{last_task_row})"
        )

        sheet.cell(
            section_row, 3,
            f"=MAX(C{first_task_row}:C{last_task_row})"
        )

        # Section styling
        for col in range(1, last_column + 1):
            cell = sheet.cell(section_row, col)
            cell.fill = PatternFill("solid", fgColor=LIGHT)
            cell.font = Font(
                bold=True,
                color=DARK,
                size=11
            )

        sheet.row_dimensions[section_row].height = 26

        # Task styling
        for row in range(first_task_row, last_task_row + 1):

            sheet.row_dimensions[row].height = 20

            for col in range(1, last_column + 1):
                cell = sheet.cell(row, col)

                if row % 2 == 0:
                    cell.fill = PatternFill(
                        "solid", fgColor="F8FAFC"
                    )

                cell.font = Font(size=10, color=DARK)

        # Collapsible task rows
        sheet.row_dimensions.group(
            first_task_row,
            last_task_row,
            outline_level=1,
            hidden=False
        )

        # --------------------------------------
        # AUTOMATIC GANTT BARS
        # --------------------------------------

        # Apply section-specific conditional
        # formatting so bars update when dates
        # are edited in Excel.

        for row in range(section_row, last_task_row + 1):

            start = sheet.cell(row, 2).value
            finish = sheet.cell(row, 3).value

            # Section summary rows contain formulas, so
            # use the calculated dates from Python instead.
            if row == section_row:
                start = min(task["start"] for task in group["tasks"])
                finish = max(task["end"] for task in group["tasks"])

            start = toDate(start)
            finish = toDate(finish)

            if start is None or finish is None:
                continue

            for col in range(4, last_column + 1):

                week_start = sheet.cell(6, col).value
                week_end = week_start + timedelta(days=7)

                if start < week_end and finish >= week_start:
                    # Use a lighter color for major section bars
                    barColor = lightenColor(color, 0.65) if row == section_row else color

                    sheet.cell(row, col).fill = PatternFill(
                        fill_type="solid",
                        fgColor=barColor
)

            # Add stronger borders to section row
            section_border = Border(
                top=Side(style="medium", color=color),
                bottom=Side(style="thin", color=color)
            )

            for cell in sheet[section_row][:last_column]:
                cell.border = section_border

    # ------------------------------------------
    # FINAL FORMATTING
    # ------------------------------------------

    sheet.column_dimensions["A"].width = 42
    sheet.column_dimensions["B"].width = 17
    sheet.column_dimensions["C"].width = 17

    for row in sheet.iter_rows(
        min_row=6,
        max_row=sheet.max_row,
        min_col=2,
        max_col=3
    ):
        for cell in row:
            if cell.row > 6:
                cell.number_format = "mm/dd/yyyy"
                cell.alignment = Alignment(horizontal="center")

    # Apply light grid borders to timeline
    thin = Side(style="hair", color=GRID)

    for row in sheet.iter_rows(
        min_row=7,
        max_row=sheet.max_row,
        min_col=4,
        max_col=last_column
    ):
        for cell in row:
            if cell.border.top.style != "medium":
                cell.border = Border(
                    left=thin,
                    right=thin,
                    bottom=thin
                )

    # Header styling
    for cell in sheet[6][:3]:
        cell.fill = PatternFill("solid", fgColor=DARK)
        cell.font = Font(color=WHITE, bold=True)
        cell.alignment = Alignment(horizontal="center")

    sheet.freeze_panes = "D7"

    # Print layout
    sheet.sheet_properties.pageSetUpPr.fitToPage = True
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.paperSize = sheet.PAPERSIZE_A3
    sheet.page_setup.fitToWidth = 1
    sheet.page_setup.fitToHeight = 0

    sheet.print_title_rows = "5:6"
    sheet.print_options.horizontalCentered = True
    sheet.print_area = f"A1:{last_letter}{sheet.max_row}"

    # Request formula recalculation in Excel
    try:
        workbook.calculation.fullCalcOnLoad = True
        workbook.calculation.forceFullCalc = True
    except AttributeError:
        pass

    # ------------------------------------------
    # SAVE TO MEMORY
    # ------------------------------------------

    output = BytesIO()
    workbook.save(output)
    workbook.close()

    return output.getvalue()
