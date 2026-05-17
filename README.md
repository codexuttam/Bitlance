# Bitlance CEO Email Automation Campaign

An end-to-end automated email outreach system designed to scrape CEO data, perform bulk personalized outreach, and handle incoming replies automatically.

## 🚀 Features

- **Module 1: CEO Data Scraper** - Scrapes Fortune 500 companies, identifies CEOs, and generates/verifies email addresses.
- **Module 2: Bulk Outreach** - Sends personalized HTML emails with rate-limiting and tracking capabilities.
- **Module 3: Auto-Reply Listener** - Monitors inbox for replies, parses sender info, and sends a personalized acknowledgement while logging it to Excel.

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Gmail Account (with App Password enabled)
- (Optional) Hunter.io API Key for verified email finding

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/codexuttam/Bitlance.git
cd Bitlance

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Rename `config/.env.example` to `config/.env` and fill in your credentials:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# IMAP Settings for Auto-Reply
IMAP_HOST=imap.gmail.com
REPLY_TO_USER=your-email@gmail.com
REPLY_TO_PASS=your-app-password

# API Keys
HUNTER_API_KEY=your_key_here
```

---

## 📖 Usage Guide

### Module 1: Scraping & Data Preparation
Run the scraper to generate the `ceo_data.xlsx` file.
```bash
python3 scraper.py
```
*Outputs: `ceo_data.xlsx` with 'CEO Master List' and 'Email Ready' sheets.*

### Module 2: Bulk Email Campaign
Trigger the outreach campaign to the 'Email Ready' list.
```bash
python3 bulk_mailer.py
```
*Features: 72s rate-limiting, personalized HTML templates, and tracking pixels.*

### Module 3: Auto-Reply Automation
Start the background listener to handle incoming replies.
```bash
python3 auto_reply.py
```
*Action: Monitors inbox, sends instant personalized replies, and logs interactions to 'Replies Log' sheet.*

---

## 📂 Project Structure

```text
Bitlance/
├── config/               # Configuration and .env files
├── data/                 # Excel database (ceo_data.xlsx)
├── src/
│   ├── scraper/          # Module 1: Wikipedia scraper & cleaners
│   ├── automation/       # Module 2 & 3: Email sender and listener
│   └── manager/          # Excel utility manager
├── scraper.py            # Module 1 Runner
├── bulk_mailer.py        # Module 2 Runner
├── auto_reply.py         # Module 3 Runner
└── requirements.txt      # Dependency list
```

---

## 📦 Deliverables Checklist

- [x] **ceo_data.xlsx**: 50–100 CEOs with 10 fields and professional formatting.
- [x] **scraper.py**: Fully commented Wikipedia scraper with Hunter.io integration.
- [x] **bulk_mailer.py**: Personalized outreach script with rate-limiting.
- [x] **template.html**: Premium responsive HTML email template.
- [x] **auto_reply.py**: IMAP-based auto-reply listener.
- [x] **auto_reply_template.txt**: Personalized plain-text acknowledgement template.
- [x] **README.md**: Complete setup and execution documentation.

---

## 🎁 Bonus: No-Code Automation

### n8n (Self-Hosted, Free)
A complete workflow blueprint is provided in [`n8n_workflow_blueprint.json`](n8n_workflow_blueprint.json).

To run it:
```bash
npx n8n
# Open http://localhost:5678 → Import the JSON blueprint → Activate
```

Workflow:
1. **Gmail Trigger** — Polls inbox every minute for unread emails.
2. **IF Filter** — Detects genuine replies via `In-Reply-To` / `References` headers.
3. **Gmail Send** — Dispatches personalised auto-reply with Calendly booking link.
4. **Google Sheets** — Logs every interaction to a `Replies Log` sheet.

### Zapier (100 tasks/month Free)
| Step | App | Event |
|------|-----|-------|
| Trigger | Gmail | New Email (INBOX) |
| Filter | Filter by Zapier | Subject contains "Re:" |
| Action | Gmail | Send personalised reply |

---

## ⚖️ Disclaimer
This tool is for educational purposes. Ensure compliance with CAN-SPAM Act and GDPR when performing email outreach.
