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
      Paragraph("Prototype overview · 19 October 2026", body), Spacer(1, 4),
      Paragraph("Built in GoHighLevel with an AI voice agent. All data in the prototype is fake.", small),
      PageBreak()]

# 1 Big picture
s += section(1, "The big picture",
             "Every client has a yearly review. The system books it, reminds them by email, "
             "calls them on the day, records their answers, and hands everything to the team to check. "
             "Once the team signs it off, next year's review books itself.")
journey = [
    ["Step", "What happens"],
    ["1. Booked", "Each client is booked into the review calendar at a set time."],
    ["2. Confirmed", "They get a booking confirmation email, then reminder emails. No texts."],
    ["3. Called", "On the day, at the booked time, the calendar triggers the AI agent to call them."],
    ["4. Recorded", "The agent asks the review questions, confirms the answers, and saves a summary."],
    ["5. Sorted", "The pipeline moves the client to the right stage automatically."],
    ["6. Checked", "A team member reads every result. Nothing is final until a person has checked it."],
    ["7. Rebooked", "The team member moves them to Yearly Review Complete, and next year's review books "
                    "itself one year from the call date."],
]
s += [table(journey, [32 * mm, W - 32 * mm]), PageBreak()]

# 2 Calendars
s += section(2, "Calendars", "Two calendars. Both run Monday to Friday, 9am to 5pm, UK time.")
s += [table([
    ["Calendar", "What it is for"],
    ["Annual Review Calls", "Every client's review slot. A booking here is what triggers the AI call on the day. "
                            "Synced with Outlook."],
    ["Review Callback", "For clients who would rather speak to a person. They pick a time from a link "
                        "we email them."],
], [45 * mm, W - 45 * mm]), Spacer(1, 26)]

# 3 Emails
s += section(3, "Emails", "Clients are contacted by email only. They don't get texts from a mobile number.")
s += bullets([
    "<b>Booking confirmation:</b> sent as soon as the review is booked.",
    "<b>Reminders:</b> 7 days before and 1 day before the call.",
    "<b>After the call:</b> a booking link, if they wanted another time or a person.",
    "<b>Replies are monitored:</b> if a client replies to say they can't make it, the team is told "
    "and the call is held until someone checks.",
    "<b>Volume:</b> GoHighLevel email sending, with a working figure of around 1,500 emails a day. "
    "That comfortably covers 100 calls a day.",
    "<b>Summary to Enver:</b> after every call, the results are emailed to the adviser and the team inbox.",
])
s.append(PageBreak())

# 4 Agent
s += section(4, "The AI agent", "A professional, polite voice agent that only asks and records.")
s += [Paragraph("It does", h2), Spacer(1, 8)]
s += bullets([
    "Checks it's speaking to the right person, then runs a quick security check.",
    "Asks if now is a good time to do the review.",
    "Asks the 10 review questions, one at a time.",
    "Reads the answers back once to confirm them.",
    "Saves every answer, a summary and the outcome to the client's record.",
])
s += [Spacer(1, 8), Paragraph("It never", h2), Spacer(1, 8)]
s += bullets([
    "Gives advice, opinions, figures or product information.",
    "Gives out any information held about the client.",
    "Promises changes or moves money.",
    "Strays off the review.",
    "Leaves review details on a voicemail.",
])
s += [Spacer(1, 6), Paragraph("Clients have signed to agree to AI calls, so the agent doesn't open with an "
                              "AI or recording disclosure.", small), PageBreak()]

# 5 Scenarios
s += section(5, "Call scenarios", "What the agent does in each situation.")
s += [table([
    ["Situation", "What the agent does"],
    ["Happy to go ahead", "Runs the full review, confirms the answers, and closes politely."],
    ["Busy right now", "Prompts towards a rebook. A link is emailed so they can choose a new time."],
    ["Wants a person", "Fine. A link to the Review Callback calendar is emailed to them."],
    ["Doesn't want a review", "Accepts it politely and doesn't push. The adviser is told."],
    ["Upset, bereaved or vulnerable", "Slows down, stops the questions, and hands straight to the team."],
    ["Complaint, or wants advice or a change", "Notes it and hands it to the team."],
    ["Someone else answers", "Asks for a better time. Says nothing else."],
    ["Fails the security check", "Ends politely. The team is told."],
    ["No answer or voicemail", "Leaves a short message only. Tries again up to 3 times, then hands to the team."],
], [55 * mm, W - 55 * mm]), PageBreak()]

# 6 Pipeline
s += section(6, "Pipeline: Annual Reviews",
             "Every client sits in one stage. Stages move automatically after each call, except the last one.")
s += [table([
    ["Stage", "What it means"],
    ["Review Scheduled", "Booked in, waiting for the call."],
    ["Calling", "The agent is calling now."],
    ["No Answer - Retrying", "Didn't answer. Another attempt is booked (up to 3)."],
    ["Callback Booked", "Wants a person or another time, or replied to the email to rearrange."],
    ["Review Done - Awaiting Check", "Review completed. A team member needs to check it."],
    ["Handover to Management", "Needs a person: vulnerable, complaint, advice, failed checks, or 3 missed calls."],
    ["Declined Review", "Didn't want a review this year, or wrong number."],
    ["Yearly Review Complete", "<b>Moved by hand</b> after a team member checks it. This books next year's review."],
], [60 * mm, W - 60 * mm]), PageBreak()]

# 7 Workflows
s += section(7, "Workflows", "Five workflows run the whole system.")
s += [card("A. Review call", "the client's review time arrives on the Annual Review Calls calendar.",
           ["Checks it's a weekday between 9am and 5pm.",
            "Moves the client to Calling.",
            "Tells the AI agent to call them."]),
      card("B. Call result", "the call ends.",
           ["Saves today as the Review Date.",
            "Moves the client to the right pipeline stage based on the outcome.",
            "Emails the results to the adviser and the team.",
            "Emails a booking link if they wanted another time or a person.",
            "Books another attempt if there was no answer."]),
      card("C. Yearly rebook", "a team member moves the client to Yearly Review Complete.",
           ["Books next year's review exactly one year from the Review Date, at the same time.",
            "Moves it to the next working day if it lands on a weekend or bank holiday.",
            "Clears this year's answers and puts the client back to Review Scheduled."]),
      card("D. Confirmations and reminders", "a review is booked.",
           ["Sends the booking confirmation email.",
            "Sends reminder emails 7 days and 1 day before.",
            "Stops if the booking is cancelled or moved."]),
      card("E. Email replies", "a client replies to any email.",
           ["Alerts the team to read it.",
            "If they say they can't make it, holds the call and moves them to Callback Booked."]),
      PageBreak()]

# 8 Human check
s += section(8, "Human check and the yearly rebook")
s += bullets([
    "The system is fully automatic, but <b>every result is checked by a person</b>.",
    "Only a team member can move a client to <b>Yearly Review Complete</b>.",
    "The next review is always <b>one year from the call date</b>, not from when the client was moved. "
    "If the team moves them two weeks later, next year's date doesn't change.",
])
s += [Spacer(1, 24)]

# 9 Later
s += section(9, "Options for later")
s += bullets([
    "<b>Live transfer:</b> if a client wants to speak to someone there and then, during working hours, "
    "and someone is free, the agent could put them straight through. Otherwise they get the booking link.",
    "<b>Real data:</b> import Enver's real client list from their current software.",
    "<b>Real questions:</b> swap the 10 test questions for Enver's own.",
    "<b>Scale:</b> designed for many calls a day (100+), with many calls running at once.",
])
s += [Spacer(1, 24)]

# 10 Status
s += section(10, "Prototype status")
s += [table([
    ["Item", "Status"],
    ["Agent script and 10 test questions", "Written"],
    ["Pipeline, fields, calendars, workflows", "Designed, ready to build"],
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
