# Enver Wealth Management: annual review system, build spec (PROTOTYPE)

Everything here is fake prototype data. Nothing touches Clear View, Poppy or any other sub-account.

## 0. Sub-account
- Name: **Enver Wealth Management (Prototype)**
- Email: reviews@enver-prototype.example
- Phone: none for now
- Timezone: Europe/London
- Address: 1 Example Street, London, EC1A 1AA (fake)

## 1. Custom fields (contact)

| Field | Type | Who fills it |
|---|---|---|
| Adviser Name | Text | Import |
| Adviser Email | Text | Import |
| Date of Birth | Date | Import (used for the security check) |
| Client Reference | Text | Import |
| Review Date | Date | Workflow B, the day the call happens |
| Next Review Date | Date | Workflow C (Review Date + 1 year) |
| Review Attempts | Number | Workflow A (+1 each call) |
| Review Outcome | Single option: COMPLETED, REBOOK, PARTIAL, HANDOVER, CALLBACK_REQUESTED, DECLINED, SECURITY_FAILED, WRONG_PERSON, WRONG_NUMBER, NO_ANSWER | Agent |
| Review Flags | Text | Agent (SENSITIVE, ANSWERS NOT CONFIRMED, ADVICE REQUESTED, COMPLAINT) |
| Review Summary | Large text | Agent |
| Q1 Contact Details Changed | Large text | Agent |
| Q2 Personal Circumstances | Large text | Agent |
| Q3 Employment / Income | Large text | Agent |
| Q4 Upcoming Expenses | Large text | Agent |
| Q5 Retirement Age | Large text | Agent |
| Q6 Attitude to Risk | Large text | Agent |
| Q7 Lump Sums | Large text | Agent |
| Q8 Will / Beneficiaries | Large text | Agent |
| Q9 Protection Cover | Large text | Agent |
| Q10 Service / Adviser Topics | Large text | Agent |
| Answers Confirmed | Single option: Yes, No | Agent |

## 2. Pipeline: "Annual Reviews"

| # | Stage | How it gets there |
|---|---|---|
| 1 | Review Scheduled | Import, or Workflow C rebook |
| 2 | Calling | Workflow A, when the call starts |
| 3 | No Answer - Retrying | Workflow B (NO_ANSWER / WRONG_PERSON, under 3 attempts) |
| 4 | Callback Booked | Workflow B (CALLBACK_REQUESTED) or a booking on the Callback calendar |
| 5 | Review Done - Awaiting Check | Workflow B (COMPLETED) |
| 6 | Handover to Management | Workflow B (HANDOVER, PARTIAL, SECURITY_FAILED, or 3 failed attempts) |
| 7 | Declined Review | Workflow B (DECLINED, WRONG_NUMBER) |
| 8 | Yearly Review Complete | **Manual only**, by a team member after checking. Triggers Workflow C |

## 3. Calendars
1. **Annual Review Calls** (the agent's calendar). One event per client at their review slot. Weekdays 09:00-17:00 only, 15-minute slots. Synced to Outlook (connect Enver's Outlook under Settings > Calendars > Connections when real).
2. **Review Callback** (the booking link). Human callback calls, 20 minutes, weekdays 09:00-17:00. This link goes in the post-call email (never SMS).

## 4. Voice AI agent: "Ava - Enver Reviews"
- Prompt: `01-agent-prompt.md`
- Language en-US (the only English option; the prompt forces British English, same as Poppy)
- Max call 900s, patience medium, idle reminders on at 8s
- Outbound call disclosures: **OFF**. James's instruction, 19 Oct 2026: every client has signed consent to AI review calls, and the agent only ever calls clients who are expecting it. No AI or recording notice in the opening. If GoHighLevel adds its own outbound disclosure or consent setting, turn it off in the UI.
- Working hours: Mon-Fri 09:00-17:00 Europe/London
- Save call summary as note: on
- Post-call email: Adviser + reviews@enver-prototype.example
- Model: **set to Claude in the agent settings** (the API does not expose the model, so this is a UI step)
- Actions:
  - In-call data extraction: Review Outcome, Review Flags, Answers Confirmed, Q1-Q10
  - Post-call data extraction: Review Summary
  - No SMS actions. All links go by email from Workflow B
  - Call transfer: OFF for the prototype. OPTION for later: in hours, if an adviser is free, transfer "wants a person" calls live; otherwise email the booking link

## 5. Workflows (built in the GoHighLevel UI; the API can't create workflows)

### Workflow A: "Review call - start"
- Trigger: Appointment status **Booked/Confirmed**, calendar = Annual Review Calls
- Wait: until appointment start time
- If/Else: day is Mon-Fri and time is 09:00-17:00, otherwise wait until the next weekday 09:00
- Update opportunity: Annual Reviews > **Calling**
- Math: Review Attempts + 1
- **Voice AI outbound call**: agent Ava, to the contact's phone
- (End. Workflow B picks up the result.)

### Workflow B: "Review call - result" (agent's Call End workflow)
- Trigger: Voice AI call ended (set as Ava's callEndWorkflow)
- Update field: Review Date = today
- If/Else on Review Outcome:
  - COMPLETED → stage **Review Done - Awaiting Check**, internal notification to the adviser
  - HANDOVER / PARTIAL / SECURITY_FAILED → stage **Handover to Management**, task for the adviser "Call client - see Review Summary", URGENT if Flags contain SENSITIVE
  - REBOOK → stage **Review Scheduled**, email the Annual Review Calls booking link
  - CALLBACK_REQUESTED → stage **Callback Booked**, email the Review Callback booking link
  - DECLINED / WRONG_NUMBER → stage **Declined Review**
  - NO_ANSWER / WRONG_PERSON:
    - Attempts < 3 → stage **No Answer - Retrying**, wait 1 working day, rebook a new Annual Review Calls slot at a different time of day (morning ↔ afternoon) → loops to Workflow A
    - Attempts = 3 → stage **Handover to Management**, note "3 attempts, no contact"
- Every branch: email to Adviser Email + reviews@enver-prototype.example with outcome, flags, Q1-Q10 and the summary. Subject: `Annual review - {{contact.name}} - {{contact.review_outcome}}`

### Workflow C: "Yearly review complete - rebook"
- Trigger: Pipeline stage changed to **Yearly Review Complete** (Annual Reviews)
- Next Review Date = **Review Date + 365 days** (from the call date, not the date it was moved)
- Custom code / webhook: create an Annual Review Calls appointment on Next Review Date at the same time as this year's call. If it falls on a weekend or UK bank holiday, move it to the next working day, same time.
- Reset: Review Attempts = 0, clear Review Outcome, Flags and Q1-Q10 (this year's answers stay in the note and email)
- Update opportunity: back to **Review Scheduled**

### Workflow D: "Booking confirmation and reminders" (email only, no SMS)
- Trigger: Appointment booked on Annual Review Calls
- Email: booking confirmation (date, time, "we'll call you on the number we hold", reschedule link)
- Wait until 7 days before → reminder email; 1 day before → reminder email
- Skip reminders if the appointment is cancelled or rescheduled

### Workflow E: "Email replies monitored"
- Trigger: Customer replied (email channel)
- Internal notification + task for the team to read the reply
- If the reply mentions cancel / reschedule / can't make it → stage **Callback Booked** and pause Workflow A for that contact until a person checks

## 6. Email sending
- Dedicated sending domain on LC Email (e.g. reviews.enver-domain), with SPF, DKIM and DMARC set up
- Warm the domain up gradually before full volume
- Daily volume: confirm the actual limit on Enver's GoHighLevel plan (James's working figure is 1,500/day, which covers 100 calls/day with confirmations and two reminders each)
- Replies go to a monitored inbox (see Workflow E)

## 7. Fake test clients
See `03-fake-clients.csv`. Phones use Ofcom's reserved drama range (07700 900xxx), so they can never ring a real person. Swap one for your own mobile to test a live call.
