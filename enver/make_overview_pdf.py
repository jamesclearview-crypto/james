"""Builds Enver-Annual-Review-System-Overview.pdf from the plan agreed with James."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, KeepTogether)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", FONT_DIR + "DejaVuSans-Bold.ttf"))

NAVY = colors.HexColor("#14284b")
TEAL = colors.HexColor("#1f7a74")
SOFT = colors.HexColor("#eef3f6")
LINE = colors.HexColor("#c9d4dc")
INK = colors.HexColor("#1d2329")
MUTED = colors.HexColor("#5b6670")

title = ParagraphStyle("title", fontName="Sans-Bold", fontSize=30, leading=38, textColor=NAVY)
subtitle = ParagraphStyle("subtitle", fontName="Sans", fontSize=15, leading=22, textColor=TEAL)
h1 = ParagraphStyle("h1", fontName="Sans-Bold", fontSize=20, leading=26, textColor=NAVY, spaceAfter=4)
kicker = ParagraphStyle("kicker", fontName="Sans-Bold", fontSize=9, leading=12, textColor=TEAL)
h2 = ParagraphStyle("h2", fontName="Sans-Bold", fontSize=13, leading=18, textColor=NAVY)
body = ParagraphStyle("body", fontName="Sans", fontSize=11, leading=17, textColor=INK, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=body, fontSize=9.5, leading=14, textColor=MUTED)
cell = ParagraphStyle("cell", parent=body, fontSize=10, leading=14.5)
cell_b = ParagraphStyle("cell_b", parent=cell, fontName="Sans-Bold", textColor=NAVY)
head = ParagraphStyle("head", parent=cell, fontName="Sans-Bold", textColor=colors.white)

W = A4[0] - 40 * mm


def section(num, name, intro=None):
    out = [Paragraph(f"SECTION {num}", kicker), Spacer(1, 3), Paragraph(name, h1)]
    if intro:
        out += [Spacer(1, 4), Paragraph(intro, body)]
    out.append(Spacer(1, 14))
    return out


def bullets(items):
    return sum(([Paragraph(f"•&nbsp;&nbsp;{t}", body), Spacer(1, 6)] for t in items), [])


def table(rows, widths, header=True):
    data = []
    for i, r in enumerate(rows):
        if header and i == 0:
            data.append([Paragraph(c, head) for c in r])
        else:
            data.append([Paragraph(r[0], cell_b)] + [Paragraph(c, cell) for c in r[1:]])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for i in range(1 if header else 0, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), SOFT))
    t.setStyle(TableStyle(style))
    return t


def card(name, trigger, steps):
    inner = [Paragraph(name, h2), Spacer(1, 4),
             Paragraph(f"<font color='#1f7a74'><b>Starts when:</b></font> {trigger}", body), Spacer(1, 6)]
    inner += sum(([Paragraph(f"•&nbsp;&nbsp;{s}", cell), Spacer(1, 3)] for s in steps), [])
    t = Table([[inner]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, LINE), ("LINEBEFORE", (0, 0), (0, -1), 4, TEAL),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return KeepTogether([t, Spacer(1, 14)])


def on_page(c, doc):
    if doc.page == 1:
        return
    c.saveState()
    c.setFont("Sans", 8.5)
    c.setFillColor(MUTED)
    c.drawString(20 * mm, 12 * mm, "Enver Wealth Management · Annual Review System · Prototype overview")
    c.drawRightString(A4[0] - 20 * mm, 12 * mm, str(doc.page))
    c.setStrokeColor(LINE)
    c.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
    c.restoreState()


s = []

# Cover
s += [Spacer(1, 60 * mm), Paragraph("Enver Wealth Management", subtitle), Spacer(1, 8),
      Paragraph("Annual Review System", title), Spacer(1, 14),
      Paragraph("How the automated yearly review calls will work", subtitle), Spacer(1, 40 * mm),
      Paragraph("Prototype overview · version 2 · 19 October 2026", body), Spacer(1, 4),
      Paragraph("Built in GoHighLevel with an AI voice agent. All data in the prototype is fake.", small),
      PageBreak()]

# 1 Big picture
s += section(1, "The big picture",
             "One continuous cycle. Staff upload the client list, the system books, reminds, calls, "
             "records and sorts. A person checks every result, and next year's review books itself.")
s += [table([
    ["Step", "What happens"],
    ["1. Upload", "Staff fill in the client spreadsheet and import it into GoHighLevel."],
    ["2. Booked", "Each client is booked into the review calendar, linked to their email."],
    ["3. Confirmed", "They get a booking confirmation email, then reminder emails. No texts."],
    ["4. Called", "On the day, at the booked time, the calendar triggers the AI agent to call."],
    ["5. Recorded", "The agent asks the questions, confirms the answers, and saves everything."],
    ["6. Sorted", "The pipeline moves the client to the right stage. Urgent things alert management straight away."],
    ["7. Checked", "A person reads every result. Nothing is final until it's checked."],
    ["8. Outcome", "Once checked, the client is emailed to say their review is complete."],
    ["9. Rebooked", "Next year's review books itself, one year from the call date."],
], [32 * mm, W - 32 * mm]), PageBreak()]

# 2 Client data
s += section(2, "Client data and the import spreadsheet",
             "The agent has to know exactly who it's calling, so the client details must be right.")
s += bullets([
    "<b>One spreadsheet</b> with a column for every field the system needs. It has instructions, "
    "an example row and a Ready? check that flags missing details.",
    "<b>Staff job:</b> fill it in correctly, then upload it to GoHighLevel. The clients go straight into "
    "the client database.",
    "<b>Email is the key.</b> It links the client to their calendar booking and every email, so "
    "everything matches up.",
    "<b>Names:</b> the agent greets clients by title and surname (e.g. Mrs Holloway), or by a preferred "
    "name if one is given.",
    "<b>Notes for the agent:</b> e.g. hard of hearing or prefers a slower pace. The agent follows them on the call.",
    "<b>Security:</b> date of birth and postcode, so the agent can check it's the right person.",
])
s += [Spacer(1, 10), Paragraph("Columns: Title · First Name · Last Name · Preferred Name · Email · Phone · "
                               "Date of Birth · Address · Town · Postcode · Client Reference · Adviser Name · "
                               "Adviser Email · Review Date · Review Time · Last Review Date · Notes for Agent",
                               small), PageBreak()]

# 3 Calendars
s += section(3, "Calendars", "Two calendars. Both run Monday to Friday, 9am to 5pm, UK time.")
s += [table([
    ["Calendar", "What it is for"],
    ["Annual Review Calls", "Every client's review slot, plus any follow-up calls. A booking here triggers "
                            "the AI call on the day. Synced with Outlook."],
    ["Review Callback", "For clients who'd rather speak to a person. They pick a time from a link we email them."],
], [45 * mm, W - 45 * mm]), Spacer(1, 26)]

# 4 Emails
s += section(4, "Emails", "Clients are contacted by email only. They don't get texts from a mobile number.")
s += [table([
    ["Email", "When it's sent"],
    ["Booking confirmation", "As soon as the review is booked."],
    ["Reminders", "7 days before and 1 day before the call."],
    ["Follow-up link", "Straight after the call, if they need more information or time to think."],
    ["Callback link", "Straight after the call, if they want to speak to a person."],
    ["Review complete", "Only after a person has checked the review. Never straight after the call."],
    ["Results to Enver", "After every call, to the adviser and the team inbox."],
], [45 * mm, W - 45 * mm]), Spacer(1, 12)]
s += bullets(["<b>Replies are monitored.</b> If a client replies to say they can't make it, the team is told "
              "and the call is held.",
              "<b>Volume:</b> a working figure of around 1,500 emails a day, which covers 100 calls a day."])
s.append(PageBreak())

# 5 Agent
s += section(5, "The AI agent", "A professional, polite voice agent that only asks and records.")
s += [Paragraph("It does", h2), Spacer(1, 8)]
s += bullets([
    "Greets the client by their correct name and checks it's the right person.",
    "Runs a quick security check, then asks if now is a good time.",
    "Asks the 10 review questions, one at a time, then reads the answers back once to confirm them.",
    "Saves every answer, a summary, the outcome and how urgent it is.",
])
s += [Spacer(1, 8), Paragraph("It never", h2), Spacer(1, 8)]
s += bullets([
    "Gives advice, opinions, figures or product information.",
    "Gives out any information held about the client.",
    "Promises changes or moves money.",
    "Strays off the review, or leaves review details on a voicemail.",
])
s += [Spacer(1, 6), Paragraph("Clients have signed to agree to AI calls, so the agent doesn't open with an "
                              "AI or recording disclosure.", small), PageBreak()]

# 6 Scenarios
s += section(6, "Call scenarios", "It isn't just done or bad. Every call ends in one of these.")
s += [table([
    ["Situation", "What happens"],
    ["Happy to go ahead", "Full review, answers confirmed, polite close."],
    ["Needs more information", "Carries on with the rest, then emails a link to book a short follow-up call."],
    ["Needs time to think", "No pressure. Emails a link to book a follow-up call when they're ready."],
    ["Busy right now", "Prompts towards a rebook. A link is emailed to choose a new time."],
    ["Wants a person", "Emails a link to book a call with the team."],
    ["Doesn't want a review", "Accepts it politely. The adviser is told."],
    ["Mild concern", "Finishes the review if they're happy to, then flags it for the adviser."],
    ["Urgent or vulnerable", "Slows down, stops the questions, and alerts management straight away."],
    ["Someone else answers", "Asks for a better time. Says nothing else."],
    ["Fails the security check", "Ends politely. Management is alerted."],
    ["No answer", "Short voicemail only. Up to 3 tries, then passed to management."],
], [52 * mm, W - 52 * mm]), PageBreak()]

# 7 Follow-up calls
s += section(7, "Follow-up calls", "When a client needs more information or time to think.")
s += bullets([
    "The client books a follow-up time from the emailed link, on the same review calendar.",
    "On that day, the calendar triggers the agent to call again, just like the first call.",
    "<b>The agent is up to date before it calls.</b> It reads last call's summary, the answers already "
    "given, and what's still to cover.",
    "It opens with \"last time we spoke...\" and only asks what's left, so the client never repeats themselves.",
    "No follow-up booked within 5 working days → a reminder email, then it's passed to the adviser.",
])
s += [Spacer(1, 24)]

# 8 Urgent and concerns
s += section(8, "Bad reviews and urgent issues", "Two levels, so the right people hear at the right speed.")
s += [table([
    ["Level", "Examples", "What happens"],
    ["Urgent", "Bereavement, illness, distress, hardship, wants to move or take out money, serious complaint, "
               "wants to leave, possible scam, failed security, 3 missed calls",
     "Immediate email and alert to management and the adviser. Task to call the client today. "
     "Escalates again if not picked up within 2 hours."],
    ["Concern", "Mildly unhappy, wants a change but no rush, wants advice later, something to go over",
     "Email to the adviser with the summary. Task to respond within 3 working days. "
     "Daily round-up to management."],
], [24 * mm, 70 * mm, W - 94 * mm]), Spacer(1, 10),
    Paragraph("Clients with an urgent issue or a concern don't get an automatic email. The adviser contacts "
              "them personally.", small), PageBreak()]

# 9 Pipeline
s += section(9, "Pipeline: Annual Reviews",
             "Every client sits in one stage. Stages move automatically, except the last one.")
s += [table([
    ["Stage", "What it means"],
    ["Review Scheduled", "Booked in, waiting for the call."],
    ["Calling", "The agent is calling now."],
    ["No Answer - Retrying", "Didn't answer. Another attempt is booked (up to 3)."],
    ["Follow-up Booked", "Needs more information or time to think. A follow-up call is booked."],
    ["Callback Booked", "Wants a person or another time, or replied to rearrange."],
    ["Review Done - Awaiting Check", "Completed with no issues. A person needs to check it."],
    ["Concern - Adviser to Review", "Completed, but something needs the adviser's attention."],
    ["Urgent - Management", "Needs a person today."],
    ["Declined Review", "Didn't want a review this year, or wrong number."],
    ["Yearly Review Complete", "<b>Moved by hand</b> after checking. Sends the client their outcome email "
                               "and books next year."],
], [62 * mm, W - 62 * mm]), PageBreak()]

# 10 Workflows
s += section(10, "Workflows", "Nine workflows run the whole cycle.")
s += [card("0. Import", "staff upload the spreadsheet.",
           ["Adds each client to the pipeline.", "Books their review slot on the calendar."]),
      card("A. Review call", "the review or follow-up time arrives on the calendar.",
           ["Checks it's a weekday, 9am to 5pm.", "Moves the client to Calling.", "Tells the agent to call."]),
      card("B. Call result", "the call ends.",
           ["Saves the date, answers, summary and anything still to cover.",
            "Moves the client to the right stage.",
            "Emails the right link to the client, and the results to Enver.",
            "Books another try if there was no answer."]),
      card("C. Yearly rebook", "a person moves the client to Yearly Review Complete.",
           ["Books next year exactly one year from the call date, at the same time.",
            "Moves it to the next working day if it lands on a weekend or bank holiday.",
            "Clears this year's answers."]),
      card("D. Confirmations and reminders", "a review or follow-up is booked.",
           ["Sends the confirmation email.", "Sends reminders before the call."]),
      card("E. Email replies", "a client replies to any email.",
           ["Alerts the team.", "Holds the call if they can't make it."]),
      card("F. Client outcome email", "a person moves the client to Yearly Review Complete.",
           ["Emails the client to say their review is complete, with roughly when the next one is due."]),
      card("G. Urgent alert", "the agent marks a call as urgent.",
           ["Alerts management and the adviser immediately.", "Creates a task to call the client today.",
            "Escalates if it's not picked up."]),
      card("H. Concern", "the agent marks a concern.",
           ["Emails the adviser.", "Creates a task to respond within 3 days.", "Adds it to the daily round-up."]),
      PageBreak()]

# 11 Human check
s += section(11, "Human check and the yearly rebook")
s += bullets([
    "The system is fully automatic, but <b>every result is checked by a person</b>.",
    "Only a team member can move a client to <b>Yearly Review Complete</b>.",
    "That one move sends the client their outcome email and books next year's review.",
    "The next review is always <b>one year from the call date</b>, not from when the client was moved.",
])
s += [Spacer(1, 24)]

# 12 Later
s += section(12, "Options for later")
s += bullets([
    "<b>Live transfer:</b> if a client wants to speak to someone there and then, during working hours, "
    "and someone is free, the agent could put them straight through. Otherwise they get the booking link.",
    "<b>Signatures:</b> the review is verbal for now. If anything needs signing, GoHighLevel's Documents "
    "& Contracts could send it for e-signature by email, and a signed document could move the pipeline. "
    "To confirm once Enver says what needs signing.",
    "<b>Real data and questions:</b> Enver's client list and their own review questions.",
    "<b>Scale:</b> designed for 100+ calls a day, with several running at once.",
])
s.append(PageBreak())

# 13 Status
s += section(13, "Prototype status")
s += [table([
    ["Item", "Status"],
    ["Agent script (v2) and 10 test questions", "Written"],
    ["Client import spreadsheet", "Ready"],
    ["Pipeline, fields, calendars, 9 workflows", "Designed, ready to build"],
    ["Fake test clients", "Ready"],
    ["GoHighLevel sub-account", "Waiting to be created"],
    ["Real questions, client data, email domain", "Needed from Enver later"],
], [W - 60 * mm, 60 * mm])]

doc = BaseDocTemplate("Enver-Annual-Review-System-Overview.pdf", pagesize=A4,
                      leftMargin=20 * mm, rightMargin=20 * mm, topMargin=22 * mm, bottomMargin=24 * mm,
                      title="Enver Annual Review System", author="Clear View")
doc.addPageTemplates([PageTemplate(frames=[Frame(20 * mm, 24 * mm, W, A4[1] - 46 * mm, id="f")],
                                   onPage=on_page)])
doc.build(s)
