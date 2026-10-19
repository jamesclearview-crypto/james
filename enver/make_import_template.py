"""Builds Enver-Client-Import-Template.xlsx: the spreadsheet staff fill in and upload to GoHighLevel."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

ARIAL = "Arial"
NAVY = "14284B"
FILL_IN = PatternFill("solid", fgColor="FFF4C2")      # yellow: cells staff fill in
EXAMPLE = PatternFill("solid", fgColor="E8EEF2")      # grey-blue: example row
HEAD = PatternFill("solid", fgColor=NAVY)
thin = Side(style="thin", color="C9D4DC")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

# (header, GHL field, field type, required, what it's used for, example)
COLUMNS = [
    ("Title", "Custom: Title", "Dropdown", "Yes", "How the agent greets them (Mr Holloway)", "Mrs"),
    ("First Name", "Standard: First Name", "Text", "Yes", "Security and records", "Margaret"),
    ("Last Name", "Standard: Last Name", "Text", "Yes", "How the agent greets them", "Holloway"),
    ("Preferred Name", "Custom: Preferred Name", "Text", "No", "If they go by another name (e.g. Maggie). Leave blank to use Title + Last Name", "Maggie"),
    ("Email", "Standard: Email", "Email", "Yes", "Unique key. Booking confirmations, reminders and outcomes go here", "margaret.holloway@example.com"),
    ("Phone", "Standard: Phone", "Text, +44 format", "Yes", "The number the agent calls", "+447700900101"),
    ("Date of Birth", "Standard: Date of Birth", "Date DD/MM/YYYY", "Yes", "Security check on the call", "14/03/1958"),
    ("Address Line 1", "Standard: Address", "Text", "Yes", "Records", "12 Example Road"),
    ("Town / City", "Standard: City", "Text", "Yes", "Records", "St Albans"),
    ("Postcode", "Standard: Postal Code", "Text", "Yes", "Security check on the call", "AL1 3TQ"),
    ("Client Reference", "Custom: Client Reference", "Text", "Yes", "Matches Enver's own system. Must be unique", "EWM-0001"),
    ("Adviser Name", "Custom: Adviser Name", "Text", "Yes", "The agent names their adviser", "Daniel Price"),
    ("Adviser Email", "Custom: Adviser Email", "Email", "Yes", "Where results and alerts go", "daniel.price@enver-prototype.example"),
    ("Review Date", "Custom: Review Slot Date", "Date DD/MM/YYYY", "Yes", "Day of the call. Books the calendar slot", "26/10/2026"),
    ("Review Time", "Custom: Review Slot Time", "Time HH:MM (09:00-16:45)", "Yes", "Time of the call", "10:00"),
    ("Last Review Date", "Custom: Last Review Date", "Date DD/MM/YYYY", "No", "Last year's review, for the records", "28/10/2025"),
    ("Notes for Agent", "Custom: Notes for Agent", "Text", "No", "Anything the agent should know (e.g. hard of hearing, speak slowly)", "Prefers a slower pace"),
]
CHECK_COL = len(COLUMNS) + 1
REQUIRED_IDX = [i for i, c in enumerate(COLUMNS) if c[3] == "Yes"]
MAX_ROWS = 1000

wb = Workbook()

# ---------- Sheet 1: Instructions ----------
ins = wb.active
ins.title = "Instructions"
ins.sheet_view.showGridLines = False
ins.column_dimensions["A"].width = 4
ins.column_dimensions["B"].width = 100
lines = [
    ("Enver Wealth Management: client import template", Font(name=ARIAL, size=16, bold=True, color=NAVY)),
    ("PROTOTYPE. All example data is fake.", Font(name=ARIAL, size=10, italic=True, color="5B6670")),
    ("", None),
    ("How to use it", Font(name=ARIAL, size=12, bold=True, color=NAVY)),
    ("1.  Go to the 'Client Import' tab. Row 2 is an example. Delete it, or leave it (it's ignored on import).", None),
    ("2.  Fill in one row per client, from row 3 down. Yellow cells are the ones you fill in.", None),
    ("3.  Every column marked Required must be filled. The 'Ready?' column shows MISSING until it is.", None),
    ("4.  Email must be unique per client. It links the client to their calendar booking and emails.", None),
    ("5.  Review Time must be on a weekday, between 09:00 and 16:45, in 15-minute steps.", None),
    ("6.  Save as CSV. In GoHighLevel: Contacts > Import > upload the CSV.", None),
    ("7.  Map each column to the GoHighLevel field shown on the 'Field Map' tab. Don't map 'Ready?'.", None),
    ("8.  Add the tag 'enver-review-import' during the import. That tag books each client's review call", None),
    ("     slot and sends the confirmation email automatically.", None),
    ("", None),
    ("Colour key", Font(name=ARIAL, size=12, bold=True, color=NAVY)),
    ("Yellow  =  fill this in", None),
    ("Grey-blue  =  example row, showing the format expected", None),
    ("", None),
    ("Before every import", Font(name=ARIAL, size=12, bold=True, color=NAVY)),
    ("•  Check every 'Ready?' cell says READY.", None),
    ("•  Check phone numbers start +44 and dates are DD/MM/YYYY.", None),
    ("•  Re-importing a client with the same email updates them rather than creating a duplicate.", None),
]
for r, (text, font) in enumerate(lines, start=1):
    c = ins.cell(row=r, column=2, value=text)
    c.font = font or Font(name=ARIAL, size=11)
    c.alignment = Alignment(vertical="center", wrap_text=True)
    ins.row_dimensions[r].height = 22
ins["B16"].fill = FILL_IN
ins["B17"].fill = EXAMPLE

# ---------- Sheet 2: Client Import ----------
ws = wb.create_sheet("Client Import")
ws.freeze_panes = "B2"
for col, (header, ghl, ftype, req, use, ex) in enumerate(COLUMNS, start=1):
    h = ws.cell(row=1, column=col, value=header + (" *" if req == "Yes" else ""))
    h.font = Font(name=ARIAL, bold=True, color="FFFFFF")
    h.fill = HEAD
    h.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    h.border = BOX
    h.comment = Comment(f"{ghl}\n{ftype}\nRequired: {req}\n{use}", "Template")
    e = ws.cell(row=2, column=col, value=ex)
    e.font = Font(name=ARIAL, italic=True, color="5B6670")
    e.fill = EXAMPLE
    e.border = BOX
    width = max(len(header) + 4, min(len(str(ex)) + 3, 38))
    ws.column_dimensions[e.column_letter].width = width
    for r in range(3, MAX_ROWS + 1):
        cell = ws.cell(row=r, column=col)
        cell.fill = FILL_IN
        cell.font = Font(name=ARIAL)
        cell.border = BOX
        cell.number_format = "@"  # keep phones, dates and times exactly as typed
ws.row_dimensions[1].height = 34

chk = ws.cell(row=1, column=CHECK_COL, value="Ready? (don't import)")
chk.font = Font(name=ARIAL, bold=True, color="FFFFFF")
chk.fill = PatternFill("solid", fgColor="1F7A74")
chk.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws.column_dimensions[chk.column_letter].width = 16
req_letters = [ws.cell(row=1, column=i + 1).column_letter for i in REQUIRED_IDX]
for r in range(2, MAX_ROWS + 1):
    blanks = "+".join(f'(TRIM({l}{r})="")' for l in req_letters)
    formula = f'=IF(COUNTA(A{r}:{ws.cell(row=1, column=len(COLUMNS)).column_letter}{r})=0,"",IF({blanks}>0,"MISSING","READY"))'
    c = ws.cell(row=r, column=CHECK_COL, value=formula)
    c.font = Font(name=ARIAL, bold=True)
    c.alignment = Alignment(horizontal="center")
    c.border = BOX

title_dv = DataValidation(type="list", formula1='"Mr,Mrs,Miss,Ms,Mx,Dr"', allow_blank=False)
title_dv.error, title_dv.errorTitle = "Pick a title from the list.", "Title"
ws.add_data_validation(title_dv)
title_dv.add(f"A2:A{MAX_ROWS}")

# ---------- Sheet 3: Field Map ----------
fm = wb.create_sheet("Field Map")
fm.sheet_view.showGridLines = False
heads = ["Spreadsheet column", "GoHighLevel field", "Type", "Required", "What it's used for"]
widths = [22, 30, 26, 11, 70]
for i, (h, w) in enumerate(zip(heads, widths), start=1):
    c = fm.cell(row=1, column=i, value=h)
    c.font = Font(name=ARIAL, bold=True, color="FFFFFF")
    c.fill = HEAD
    c.border = BOX
    c.alignment = Alignment(vertical="center")
    fm.column_dimensions[c.column_letter].width = w
for r, (header, ghl, ftype, req, use, _) in enumerate(COLUMNS, start=2):
    for cidx, v in enumerate([header, ghl, ftype, req, use], start=1):
        c = fm.cell(row=r, column=cidx, value=v)
        c.font = Font(name=ARIAL, bold=(cidx == 1))
        c.border = BOX
        c.alignment = Alignment(vertical="top", wrap_text=True)
        if r % 2 == 1:
            c.fill = PatternFill("solid", fgColor="EEF3F6")
fm.row_dimensions[1].height = 22
note_row = len(COLUMNS) + 3
fm.cell(row=note_row, column=1, value="Fields the system fills in (not in the spreadsheet):").font = Font(name=ARIAL, bold=True, color=NAVY)
auto = ("Review Outcome, Review Flags, Urgency, Q1 to Q10 answers, Answers Confirmed, Review Summary, "
        "Previous Call Summary, Open Items, Call Type (First call / Follow-up), Review Date, Next Review Date, "
        "Review Attempts.")
c = fm.cell(row=note_row + 1, column=1, value=auto)
c.font = Font(name=ARIAL)
c.alignment = Alignment(wrap_text=True, vertical="top")
fm.merge_cells(start_row=note_row + 1, start_column=1, end_row=note_row + 1, end_column=5)
fm.row_dimensions[note_row + 1].height = 34

wb.active = 1
wb.save("Enver-Client-Import-Template.xlsx")
