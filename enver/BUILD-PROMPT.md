Build the Enver Wealth Management annual review PROTOTYPE in GoHighLevel using Claude in Chrome. All data is fake.

Read these files first, in the enver/ folder of this repo (run git pull first):
- 02-build-spec.md (the full spec: fields, pipeline, calendars, agent, 9 workflows)
- 01-agent-prompt.md (the voice agent prompt, v2)
- 03-fake-clients.csv (5 fake test clients)
- Enver-Client-Import-Template.xlsx (import column layout)

Hard rules:
- NEVER touch Clear View Cleaning Contractors, Poppy, SteadyGen or any other existing sub-account. Work only inside the new Enver sub-account.
- Never delete anything. Never send real emails or make real calls; test numbers are 07700 900xxx.
- No SMS anywhere. Email only.
- Outbound call disclosures OFF (clients have signed consent).

Steps, in order:
1. In Chrome (I'm logged into GoHighLevel), Agency view > Sub-Accounts > Create: "Enver Wealth Management (Prototype)", timezone Europe/London, email reviews@enver-prototype.example, address 1 Example Street, London EC1A 1AA.
2. Inside it: Settings > Private Integrations > Create "Claude build", select ALL scopes, save. Copy the key and the location ID.
3. Save the key: create "GHL key - Enver Wealth Management (Prototype).md" in Google Drive > Optimus X > API Keys (same format as "GHL keys (other).md": sub-account, location ID, token, base URL https://services.leadconnectorhq.com, headers Authorization: Bearer <token> and Version: 2021-07-28). Add a line for it in "00 READ ME.md". Also save it locally as enver/.env and add .env to .gitignore. Never commit the key.
4. Using the API with that key, create: all custom fields (section 3), the "Annual Reviews" pipeline with its 10 stages (section 4), the 2 calendars (section 5), and the voice agent "Ava - Enver Reviews" with the v2 prompt and its data-extraction actions (section 6). Import the 5 fake clients.
5. In Chrome, set the agent's model to Claude and make sure outbound disclosures are off.
6. In Chrome, build the 9 workflows (0, A-H) exactly as in section 7. Leave them in DRAFT, not published.
7. Finish with a short checklist of what was built, what's still draft, and anything that couldn't be done, so I can review it.

Ask me before anything that would publish a workflow, send a message, or cost money.
