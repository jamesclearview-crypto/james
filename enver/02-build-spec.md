# Enver Wealth Management: annual review system, build spec (PROTOTYPE v2)

Everything here is fake prototype data. Nothing touches Clear View, Poppy or any other sub-account.

## 0. Sub-account
- Name: **Enver Wealth Management (Prototype)**
- Email: reviews@enver-prototype.example
- Phone: none for now
- Timezone: Europe/London
- Address: 1 Example Street, London, EC1A 1AA (fake)

## 1. The cycle

Staff spreadsheet → import to GoHighLevel → review slot booked on the calendar (linked to the client's email) → confirmation and reminder emails → AI call on the day → results saved to the contact → pipeline moves → a person checks → outcome email to the client → Yearly Review Complete → next year's slot books itself → round again.

## 2. Client import (the spreadsheet)

- Template: `Enver-Client-Import-Template.xlsx` (Instructions, Client Import and Field Map tabs). Every column maps to one GoHighLevel field.
- **Email is the unique key.** It joins the contact, the calendar booking and every email. Re-importing the same email updates the client instead of duplicating them.
- Staff fill it in, save as CSV, then import through Contacts > Import, mapping each column as on the Field Map tab, with the tag **enver-review-import**.
- The tag starts **Workflow 0**, which books the slot.
- The agent greets clients by **Title + Last Name** (or Preferred Name if filled in), and follows **Notes for Agent** (e.g. speak slowly). That's why those columns must be right.

## 3. Custom fields (contact)

| Field | Type | Who fills it |
|---|---|---|
| Title | Single option: Mr, Mrs, Miss, Ms, Mx, Dr | Import |
| Preferred Name | Text | Import (optional) |
| Client Reference | Text | Import |
| Adviser Name | Text | Import |
| Adviser Email | Text | Import |
| Review Slot Date | Date | Import |
| Review Slot Time | Text (HH:MM) | Import |
| Last Review Date | Date | Import (optional) |
| Notes for Agent | Large text | Import (optional) |
| Call Type | Single option: First call, Follow-up | Workflows 0, B, C |
| Previous Call Summary | Large text | Workflow B (copied from Review Summary) |
| Open Items | Large text | Agent |
| Review Date | Date | Workflow B, the day the call happens |
| Next Review Date | Date | Workflow C (Review Date + 1 year) |
| Review Attempts | Number | Workflow A (+1 each call) |
| Review Outcome | Single option: COMPLETED, NEEDS_INFO, TIME_TO_THINK, REBOOK, PARTIAL, HANDOVER, CALLBACK_REQUESTED, DECLINED, SECURITY_FAILED, WRONG_PERSON, WRONG_NUMBER, NO_ANSWER | Agent |
| Urgency | Single option: URGENT, CONCERN, NONE | Agent |
| Review Flags | Text | Agent (SENSITIVE, ANSWERS NOT CONFIRMED, ADVICE REQUESTED, COMPLAINT, PREFERRED NAME) |
| Review Summary | Large text | Agent |
| Q1 Contact Details Changed … Q10 Service / Adviser Topics | Large text ×10 | Agent |
| Answers Confirmed | Single option: Yes, No | Agent |
| Client Outcome Email Sent | Single option: Yes, No | Workflow F |

Standard fields used: First Name, Last Name, Email, Phone, Date of Birth, Address, City, Postal Code.

## 4. Pipeline: "Annual Reviews"

| # | Stage | How it gets there |
|---|---|---|
| 1 | Review Scheduled | Workflow 0 after import, or Workflow C rebook |
| 2 | Calling | Workflow A, when the call starts |
| 3 | No Answer - Retrying | Workflow B (NO_ANSWER / WRONG_PERSON, under 3 attempts) |
| 4 | Follow-up Booked | Workflow B (NEEDS_INFO / TIME_TO_THINK / PARTIAL), once the client books the follow-up |
| 5 | Callback Booked | Workflow B (CALLBACK_REQUESTED), a booking on the Callback calendar, or Workflow E |
| 6 | Review Done - Awaiting Check | Workflow B (COMPLETED, urgency NONE) |
| 7 | Concern - Adviser to Review | Workflow B (urgency CONCERN) |
| 8 | Urgent - Management | Workflow B (urgency URGENT, SECURITY_FAILED, or 3 failed attempts) |
| 9 | Declined Review | Workflow B (DECLINED, WRONG_NUMBER) |
| 10 | Yearly Review Complete | **Manual only**, by a team member after checking. Triggers Workflows F and C |

## 5. Calendars
1. **Annual Review Calls** (the agent's calendar). Review slots and follow-up slots. Weekdays 09:00-17:00 only, 15-minute slots. Synced to Outlook (connect Enver's Outlook under Settings > Calendars > Connections when real). Booked against the contact, so the client's email is on the booking.
2. **Review Callback** (the booking link for a person). Human callback calls, 20 minutes, weekdays 09:00-17:00.

Booking links go by email only, never SMS.

## 6. Voice AI agent: "Ava - Enver Reviews"
- Prompt: `01-agent-prompt.md` (v2). It reads the contact's fields at the start of every call: name, title, preferred name, adviser, notes, call type, previous call summary, open items and earlier answers.
- **Before a second call:** the agent can't read GoHighLevel notes, but it can read contact fields. So Workflow B copies the summary into **Previous Call Summary** and keeps Q1-Q10 and Open Items. On a follow-up the agent sees where things got to and only asks what's left.
- Language en-US (the only English option; the prompt forces British English, same as Poppy)
- Max call 900s, patience medium, idle reminders on at 8s
- Outbound call disclosures: **OFF**. James's instruction, 19 Oct 2026: every client has signed consent to AI review calls, and the agent only ever calls clients who are expecting it. No AI or recording notice in the opening. If GoHighLevel adds its own outbound disclosure or consent setting, turn it off in the UI.
- Working hours: Mon-Fri 09:00-17:00 Europe/London
- Save call summary as note: on
- Model: **set to Claude in the agent settings** (the API does not expose the model, so this is a UI step)
- Actions:
  - In-call data extraction: Review Outcome, Urgency, Review Flags, Open Items, Answers Confirmed, Q1-Q10
  - Post-call data extraction: Review Summary
  - No SMS actions. All links go by email from Workflow B
  - Call transfer: OFF for the prototype. OPTION for later: in hours, if someone is free, transfer "wants a person" calls live; otherwise email the booking link

## 7. Workflows (built in the GoHighLevel UI; the API can't create workflows)

### Workflow 0: "Import - book review slot"
- Trigger: Tag added **enver-review-import**
- Create/update opportunity: Annual Reviews > **Review Scheduled**
- Set Call Type = First call
- Custom code / webhook: book an Annual Review Calls appointment for this contact at Review Slot Date + Review Slot Time (the GoHighLevel workflow has no native "book appointment" action, so this calls the calendar API)
- Remove the tag (so a re-import can re-trigger it)
- The booking then starts Workflow D (confirmation email) and Workflow A (the call)

### Workflow A: "Review call - start"
- Trigger: Appointment status **Booked/Confirmed**, calendar = Annual Review Calls
- Wait: until appointment start time
- If/Else: day is Mon-Fri and time is 09:00-17:00, otherwise wait until the next weekday 09:00
- If the contact is paused (Workflow E), stop
- Update opportunity: **Calling**
- Math: Review Attempts + 1
- **Voice AI outbound call**: agent Ava, to the contact's phone

### Workflow B: "Review call - result" (agent's Call End workflow)
- Trigger: Voice AI call ended (set as Ava's callEndWorkflow)
- Update fields: Review Date = today (first call only); Previous Call Summary = Review Summary
- If/Else on Review Outcome and Urgency:
  - **Urgency URGENT** (any outcome) → stage **Urgent - Management**, then Workflow G
  - **Urgency CONCERN** → stage **Concern - Adviser to Review**, then Workflow H
  - COMPLETED → stage **Review Done - Awaiting Check**, notification to the adviser
  - NEEDS_INFO / TIME_TO_THINK / PARTIAL → set Call Type = Follow-up, email the client the Annual Review Calls booking link ("choose a time for a short follow-up call"), stage **Follow-up Booked** once they book. No booking within 5 working days → reminder email, then hand to the adviser
  - REBOOK → stage **Review Scheduled**, email the Annual Review Calls booking link
  - CALLBACK_REQUESTED → stage **Callback Booked**, email the Review Callback booking link
  - SECURITY_FAILED → stage **Urgent - Management**, then Workflow G
  - DECLINED / WRONG_NUMBER → stage **Declined Review**
  - NO_ANSWER / WRONG_PERSON:
    - Attempts < 3 → stage **No Answer - Retrying**, wait 1 working day, rebook a slot at a different time of day (morning ↔ afternoon) → loops to Workflow A
    - Attempts = 3 → stage **Urgent - Management**, note "3 attempts, no contact"
- Every branch: email to Adviser Email + reviews@enver-prototype.example with outcome, urgency, flags, Q1-Q10, open items and the summary. Subject: `Annual review - {{contact.name}} - {{contact.review_outcome}}`

### Workflow C: "Yearly review complete - rebook"
- Trigger: Pipeline stage changed to **Yearly Review Complete**
- Next Review Date = **Review Date + 365 days** (from the call date, not the date it was moved)
- Custom code / webhook: book an Annual Review Calls appointment on Next Review Date at the same time as this year's call. Weekend or UK bank holiday → next working day, same time
- Reset: Review Attempts = 0, Call Type = First call, clear Review Outcome, Urgency, Flags, Open Items, Previous Call Summary and Q1-Q10 (this year's answers stay in the notes and emails)
- Update opportunity: back to **Review Scheduled**

### Workflow D: "Booking confirmation and reminders" (email only)
- Trigger: Appointment booked on Annual Review Calls
- Email: booking confirmation (date, time, "we'll call you on the number we hold", reschedule link). Follow-up bookings get "short follow-up call" wording
- Wait until 7 days before → reminder; 1 day before → reminder (follow-ups: 1 day before only)
- Stop if the appointment is cancelled or rescheduled

### Workflow E: "Email replies monitored"
- Trigger: Customer replied (email channel)
- Internal notification + task for the team to read the reply
- If the reply mentions cancel / reschedule / can't make it → pause the contact (tag **review-paused**), stage **Callback Booked**, until a person checks

### Workflow F: "Client outcome email"
The client gets their outcome email **after a person has checked the review, never straight after the call**.
- Trigger: stage changed to **Yearly Review Complete**
- Email to the client: "Your annual review is complete. Thank you. {{adviser_name}} has your answers and will be in touch if anything needs following up. Your next review is due around {{next_review_date}}."
- Set Client Outcome Email Sent = Yes

Other client emails, sent at the time:
- Follow-up needed → follow-up booking link (Workflow B)
- Wants a person → callback booking link (Workflow B)
- Concern or urgent → **no automatic email**. The adviser contacts them personally

### Workflow G: "Urgent alert"
- Trigger: Urgency = URGENT, or stage changed to **Urgent - Management**
- Immediately: email + in-app notification to management and the adviser. Subject: `URGENT - annual review - {{contact.name}}`
- Task: "Call client today - see Review Summary", due today, assigned to the adviser
- Not picked up within 2 working hours → escalate the email to the management inbox again
- Never emails the client automatically

### Workflow H: "Concern summary"
- Trigger: Urgency = CONCERN
- Email to the adviser (not urgent): "Client raised a concern during their review", with the summary and Q10
- Task: "Review and respond", due in 3 working days
- Daily 16:30 digest to management: list of all concerns opened that day

## 8. Email sending
- Dedicated sending domain on LC Email (e.g. reviews.enver-domain), with SPF, DKIM and DMARC set up
- Warm the domain up gradually before full volume
- Daily volume: confirm the actual limit on Enver's GoHighLevel plan (James's working figure is 1,500/day, which covers 100 calls/day with confirmations and reminders)
- Replies go to a monitored inbox (Workflow E)

## 9. Signatures (later)
- For now the review is verbal. Nothing is sent for signing.
- If Enver needs anything signed, GoHighLevel's **Documents & Contracts** can send a document for e-signature by email. A workflow can send it, and a "document signed" event can move the pipeline. To confirm once Enver says what needs signing.

## 10. Fake test clients
See `03-fake-clients.csv` and the example row in the import template. Phones use Ofcom's reserved drama range (07700 900xxx), so they can never ring a real person. Swap one for your own mobile to test a live call.
