# 🚀 Bitlance CEO Email Automation Campaign

An end-to-end, production-ready email outreach automation system. This project scrapes real CEO data from Fortune 500 companies, stores it in a professionally formatted Excel database, sends bulk personalized emails via SendGrid, and automatically handles incoming replies — all with full CAN-SPAM & GDPR compliance.

---

## 📋 Table of Contents
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Deliverables Checklist](#-deliverables-checklist)
- [Setup Instructions](#-setup-instructions)
- [Configuration](#-configuration)
- [How to Run](#-how-to-run)
- [Compliance & Best Practices](#-compliance--best-practices)
- [Bonus: No-Code Automation](#-bonus-no-code-automation)
- [Disclaimer](#-disclaimer)

---

## ✨ Features

- **Module 1 — Data Scraper**: Scrapes real CEO data from Fortune 500 companies via Wikipedia, enriches with real verified emails using **Hunter.io domain-search API**, and scrapes actual **LinkedIn profile URLs via live Google Search**.
- **Module 2 — Bulk Outreach**: Sends personalized HTML emails via **SendGrid SMTP** with rate-limiting (max 50/hour), open tracking pixels, and a compliant unsubscribe footer.
- **Module 3 — Auto-Reply Listener**: IMAP-based inbox monitor that detects genuine CEO reply threads (via `In-Reply-To` header), cross-references the CRM (Excel), sends a personalized auto-reply, and logs the interaction.
- **Bonus — n8n & Zapier**: No-code automation blueprints for both platforms.

---

## 📂 Project Structure

```text
Bitlance/
├── config/
│   ├── .env                    # ⚠️ Your private credentials (never commit)
│   └── .env.example            # Template for environment variables
├── data/
│   └── ceo_data.xlsx           # Generated Excel database (2 sheets)
├── src/
│   ├── scraper/
│   │   ├── ceo_scraper.py      # Core scraping logic (Wikipedia + Hunter + Google)
│   │   └── data_cleaner.py     # Data validation & cleaning utilities
│   ├── automation/
│   │   ├── email_sender.py     # SendGrid SMTP bulk email dispatcher
│   │   ├── reply_listener.py   # IMAP auto-reply listener
│   │   ├── template.html       # HTML email template (source)
│   │   └── auto_reply_template.txt  # Auto-reply template (source)
│   └── manager/
│       └── excel_manager.py    # Excel CRM manager (2-sheet + formatting)
├── scraper.py                  # ▶ Module 1 Runner
├── bulk_mailer.py              # ▶ Module 2 Runner
├── auto_reply.py               # ▶ Module 3 Runner
├── template.html               # HTML email template
├── auto_reply_template.txt     # Auto-reply plain text template
├── n8n_workflow_blueprint.json # Bonus: n8n workflow blueprint
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 📦 Deliverables Checklist

- [x] **ceo_data.xlsx** — 50–100 CEOs with 10 fields, 2 sheets, professionally formatted with colour-coded email validation.
- [x] **scraper.py** — Live scraper: Wikipedia Fortune 500 → Hunter.io verified emails → Google LinkedIn search.
- [x] **bulk_mailer.py** — Personalised bulk email script with 72s rate-limiting, tracking pixel, and unsubscribe footer.
- [x] **template.html** — Premium responsive HTML email template with all `{{variables}}`.
- [x] **auto_reply.py** — IMAP listener that detects real reply threads and auto-responds within seconds.
- [x] **auto_reply_template.txt** — Plain-text personalised acknowledgement template.
- [x] **README.md** — Complete setup, configuration, and execution documentation.
- [x] **Bonus — No-Code Workflow** — n8n blueprint ([`n8n_workflow_blueprint.json`](n8n_workflow_blueprint.json)) + Zapier guide.

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- A [SendGrid](https://sendgrid.com) account (free tier: 100 emails/day)
- A Gmail account with **App Password** enabled (for IMAP listener)
- A [Hunter.io](https://hunter.io) account (free tier: 25 searches/month)

### 1. Clone the Repository
```bash
git clone https://github.com/codexuttam/Bitlance.git
cd Bitlance
```

### 2. Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp config/.env.example config/.env
# Now edit config/.env with your real credentials
```

---

## ⚙️ Configuration

Edit `config/.env` with your credentials:

```env
# SendGrid SMTP (dedicated sending domain — NOT personal Gmail)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=SG.your_sendgrid_api_key_here

# Outreach Identity
FROM_NAME=Your Name from YourCompany
FROM_EMAIL=outreach@yourdomain.com
REPLY_TO=replies@yourdomain.com

# Gmail IMAP (for Auto-Reply Listener — Module 3)
IMAP_HOST=imap.gmail.com
REPLY_TO_USER=your-email@gmail.com
REPLY_TO_PASS=your_gmail_app_password   # 16-char App Password, not Gmail password

# API Keys
HUNTER_API_KEY=your_hunter_api_key_here
AI_API_KEY=your_gemini_or_openai_key_here

# Scraping Limit
MAX_CEOS=100
```

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

### How to get a Gmail App Password:
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Factor Authentication**
3. Search **"App Passwords"** → Create one for "Mail"
4. Paste the 16-character password into `REPLY_TO_PASS`

---

## ▶️ How to Run

> Always activate the virtual environment first: `source venv/bin/activate`

### 🧪 Small Batch Test (Recommended before full run)
```bash
# Test scraper with 5 records only (no Excel save)
python3 -c "
from src.scraper.ceo_scraper import CEOScraper
scraper = CEOScraper()
df = scraper.run_full_pipeline(limit=5, use_forbes=False)
print(df[['Full Name','Company Name','Email Address','LinkedIn URL']].to_string())
"
```

---

### Module 1: CEO Data Scraper
Scrapes Fortune 500 CEOs, finds real emails via Hunter.io, and scrapes LinkedIn URLs via Google Search.
```bash
python3 scraper.py
```
**Output:**
- `data/ceo_data.xlsx` with 2 sheets:
  - **CEO Master List** — All 100 CEOs with all 10 fields
  - **Email Ready** — Filtered list of CEOs with verified emails only

**Runtime:** ~5–8 minutes (live API calls + Google search scraping with anti-bot delays)

---

### Module 2: Bulk Email Campaign
Reads the `Email Ready` sheet and sends personalized HTML emails via SendGrid.
```bash
python3 bulk_mailer.py
```
**Features:**
- Personalised subject: `Quick question for you, {{first_name}}`
- HTML body with `{{first_name}}`, `{{company}}`, `{{industry}}` variables
- Open tracking pixel (MD5 hash per recipient)
- Unsubscribe footer link (CAN-SPAM compliant)
- **72-second delay** between emails (max 50/hour)
- Prompts `y/n` confirmation before sending

---

### Module 3: Auto-Reply Listener
Monitors your inbox every 60 seconds for genuine CEO reply threads.
```bash
python3 auto_reply.py
```
**How it works:**
1. Connects via IMAP to your configured inbox
2. Scans all unread emails for `In-Reply-To` / `References` headers
3. If a genuine reply is detected → looks up CEO in `ceo_data.xlsx`
4. Sends a personalised auto-reply using `auto_reply_template.txt`
5. Logs the interaction to the **Replies Log** sheet in Excel

Press `Ctrl+C` to stop the listener.

---

## 🔐 Compliance & Best Practices

| Requirement | Implementation |
|------------|----------------|
| **Dedicated sending domain** | SendGrid SMTP (`smtp.sendgrid.net`) — not personal Gmail |
| **Unsubscribe link** | Injected in every email footer via `{{unsubscribe_link}}` |
| **Rate limiting** | 72-second delay = max 50 emails/hour |
| **Reply-To header** | Set to monitored inbox for proper threading |
| **No login-wall scraping** | Only publicly available Wikipedia + Google data |
| **API keys secured** | Stored in `config/.env`, never hardcoded |
| **Small batch testing** | Test with 5 records before full 100-CEO campaign |
| **Physical address** | Included in email footer (CAN-SPAM requirement) |

---

## 🎁 Bonus: No-Code Automation

### n8n (Self-Hosted, Free & Open Source)
A complete workflow blueprint is provided in [`n8n_workflow_blueprint.json`](n8n_workflow_blueprint.json).

**To run it:**
```bash
npx n8n
# Open http://localhost:5678 → Import JSON → Connect Gmail → Activate
```

**Workflow nodes:**
1. **Gmail Trigger** — Polls inbox every minute for unread emails
2. **IF Filter** — Detects genuine replies via `In-Reply-To` header
3. **Gmail — Send Auto-Reply** — Dispatches personalised reply with Calendly link
4. **Google Sheets — Log Reply** — Logs every interaction to a spreadsheet

### Zapier (100 tasks/month Free)
| Step | App | Event |
|------|-----|-------|
| 1 — Trigger | Gmail | New Email (INBOX, unread) |
| 2 — Filter | Filter by Zapier | Subject contains "Re:" |
| 3 — Action | Gmail | Send personalised reply body |

---

## ⚖️ Disclaimer

This tool is built for **educational purposes** as part of an email automation assignment. Always comply with:
- **CAN-SPAM Act** — Include physical address + unsubscribe link in all bulk emails
- **GDPR** — Only email individuals who have given consent or with whom you have a legitimate business interest
- **LinkedIn ToS** — Do not scrape or automate interactions on LinkedIn without explicit permission

Do **NOT** send actual unsolicited commercial emails to real CEOs using this system.
