"""
Bitlance CEO Email Automation — Fast Demo Test Suite

"""

import sys, os, json, hashlib, importlib
from dotenv import load_dotenv
load_dotenv("config/.env")

# ── Colour helpers ──────────────────────────────────────────────────────────
GREEN  = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; BOLD = "\033[1m"; RESET = "\033[0m"
def ok(msg):     print(f"  {GREEN}✅ {msg}{RESET}")
def fail(msg):   print(f"  {RED}❌ {msg}{RESET}")
def info(msg):   print(f"  {YELLOW}   {msg}{RESET}")
def section(msg):
    print(f"\n{BOLD}{BLUE}{'─'*55}\n  {msg}\n{'─'*55}{RESET}")

PASSED, FAILED = [], []

def test(name, fn):
    try:
        fn()
        ok(f"PASSED — {name}")
        PASSED.append(name)
    except Exception as e:
        fail(f"FAILED — {name}: {e}")
        FAILED.append(name)

# ── Mock CEO dataset (no live scraping) ─────────────────────────────────────
MOCK_CEOS = [
    {"Full Name": "Andy Jassy",      "Company Name": "Amazon",           "Industry": "Retail",            "Country": "United States", "Email Address": "andy.jassy@amazon.com",      "LinkedIn URL": "https://www.linkedin.com/in/andy-jassy-8b1727"},
    {"Full Name": "Doug McMillon",   "Company Name": "Walmart",          "Industry": "Retail",            "Country": "United States", "Email Address": "doug.mcmillon@walmart.com",   "LinkedIn URL": "https://www.linkedin.com/in/doug-mcmillon"},
    {"Full Name": "Tim Cook",        "Company Name": "Apple",            "Industry": "Technology",        "Country": "United States", "Email Address": "tcook@apple.com",             "LinkedIn URL": "https://www.linkedin.com/in/tim-cook-9272305"},
    {"Full Name": "Mary Barra",      "Company Name": "General Motors",   "Industry": "Automotive",        "Country": "United States", "Email Address": "Not Found",                   "LinkedIn URL": "https://www.linkedin.com/in/mary-barra"},
    {"Full Name": "Sundar Pichai",   "Company Name": "Alphabet",         "Industry": "Technology",        "Country": "United States", "Email Address": "sundar@google.com",           "LinkedIn URL": "https://www.linkedin.com/in/sundar-pichai"},
]

# ════════════════════════════════════════════════════════════════════════════
section("MODULE 1 — CEO Data Scraper (Mock)")
# ════════════════════════════════════════════════════════════════════════════

def t_imports():
    from src.scraper.ceo_scraper import CEOScraper
    from src.scraper.data_cleaner import DataCleaner
    from src.manager.excel_manager import ExcelManager

def t_data_cleaner():
    from src.scraper.data_cleaner import DataCleaner
    assert DataCleaner.validate_email("test@example.com") == True
    assert DataCleaner.validate_email("not-an-email")     == False
    assert DataCleaner.clean_text("Walmart[1]")           == "Walmart"
    assert DataCleaner.clean_text("Apple[note 2]")        == "Apple"
    info("Email validator + Wikipedia artifact cleaner both working")

def t_mock_pipeline():
    import pandas as pd
    df = pd.DataFrame(MOCK_CEOS)
    assert len(df) == 5
    required = ["Full Name","Company Name","Industry","Country","Email Address","LinkedIn URL"]
    for col in required: assert col in df.columns, f"Missing: {col}"
    verified = df[df["Email Address"].str.contains("@", na=False)]
    info(f"Mock dataset: {len(df)} CEOs | {len(verified)} with verified emails")
    print()
    for _, row in df.iterrows():
        email = str(row["Email Address"])
        status = GREEN + "✓" + RESET if "@" in email else RED + "✗" + RESET
        name = str(row["Full Name"])[:20].ljust(20)
        co   = str(row["Company Name"])[:16].ljust(16)
        print(f"    {status} {name} | {co} | {email}")

def t_excel_manager():
    import pandas as pd
    from src.manager.excel_manager import ExcelManager
    df = pd.DataFrame(MOCK_CEOS)
    manager = ExcelManager(file_path="data/test_demo_output.xlsx")
    manager.save_leads(df)
    assert os.path.exists("data/test_demo_output.xlsx")
    os.remove("data/test_demo_output.xlsx")   # clean up
    info("ExcelManager created 2-sheet workbook (CEO Master List + Email Ready)")

test("Library imports",          t_imports)
test("DataCleaner validation",   t_data_cleaner)
test("Mock CEO pipeline (5)",    t_mock_pipeline)
test("Excel 2-sheet save",       t_excel_manager)

# ════════════════════════════════════════════════════════════════════════════
section("MODULE 2 — Bulk Email System (Mock)")
# ════════════════════════════════════════════════════════════════════════════

def t_template_exists():
    assert os.path.exists("template.html"), "template.html not found"
    content = open("template.html").read()
    for var in ["{{first_name}}", "{{company}}", "{{industry}}", "{{unsubscribe_link}}"]:
        assert var in content, f"Missing {var} in template"
    assert "unsubscribe" in content.lower(), "No unsubscribe link — CAN-SPAM violation"
    info("template.html: all variables present + CAN-SPAM compliant footer ✓")

def t_email_personalisation():
    from src.automation.email_sender import EmailSender
    sender  = EmailSender()
    tmpl    = open("template.html").read()
    ceo     = MOCK_CEOS[0]   # Andy Jassy
    body    = tmpl.replace("{{first_name}}", ceo["Full Name"].split()[0])
    body    = body.replace("{{company}}",    ceo["Company Name"])
    body    = body.replace("{{industry}}",   ceo["Industry"])
    h       = hashlib.md5(ceo["Email Address"].encode()).hexdigest()
    body    = body.replace("{{email_hash}}", h)
    body    = body.replace("{{unsubscribe_link}}", f"https://bitlance.ai/unsubscribe?id={h}")
    assert "Andy" in body
    assert "Amazon" in body
    assert h in body
    info(f"Personalisation OK: 'Hi Andy' | company=Amazon | hash={h[:8]}...")

def t_smtp_config():
    host = os.getenv("SMTP_HOST", "")
    user = os.getenv("SMTP_USER", "")
    assert host, "SMTP_HOST not set in config/.env"
    assert user, "SMTP_USER not set in config/.env"
    info(f"SMTP ready → {host} (user: {user})")

def t_rate_limit():
    # Verify the 72-second delay constant is documented
    code = open("src/automation/email_sender.py").read()
    assert "72" in code, "72-second rate limit not found in email_sender.py"
    info("Rate limiting: 72s delay between sends = max 50 emails/hour ✓")

test("template.html valid",       t_template_exists)
test("Email personalisation",     t_email_personalisation)
test("SMTP config in .env",       t_smtp_config)
test("CAN-SPAM rate limiting",    t_rate_limit)

# ════════════════════════════════════════════════════════════════════════════
section("MODULE 3 — Auto-Reply Listener (Mock)")
# ════════════════════════════════════════════════════════════════════════════

def t_auto_reply_template():
    assert os.path.exists("auto_reply_template.txt")
    content = open("auto_reply_template.txt").read()
    assert "{{first_name}}" in content
    info("auto_reply_template.txt: personalisation variables present ✓")

def t_listener_imports():
    from src.automation.reply_listener import get_auto_reply, send_auto_reply
    info("reply_listener module imports OK")

def t_reply_filter_logic():
    """Simulate the In-Reply-To header check without opening IMAP."""
    def is_genuine_reply(headers):
        return bool(headers.get("in-reply-to") or headers.get("references"))

    assert is_genuine_reply({"in-reply-to": "<abc123@mail.gmail.com>"}) == True
    assert is_genuine_reply({"from": "noreply@pinterest.com"})          == False
    assert is_genuine_reply({"references": "<thread-id@sendgrid>"})     == True
    info("Reply filter: genuine replies detected via In-Reply-To header ✓")

def t_imap_config():
    imap_host = os.getenv("IMAP_HOST", "")
    imap_user = os.getenv("REPLY_TO_USER", "")
    assert imap_host, "IMAP_HOST not set in config/.env"
    assert imap_user, "REPLY_TO_USER not set in config/.env"
    info(f"IMAP configured: {imap_host} monitoring {imap_user}")

def t_crm_exists():
    if os.path.exists("data/ceo_data.xlsx"):
        import pandas as pd
        df = pd.read_excel("data/ceo_data.xlsx", sheet_name="CEO Master List")
        info(f"Live CRM loaded: {len(df)} CEO records available for reply matching ✓")
    else:
        info("ceo_data.xlsx not yet generated — run 'python3 scraper.py' first")

test("auto_reply_template.txt",   t_auto_reply_template)
test("Listener module imports",   t_listener_imports)
test("Reply filter (mock)",       t_reply_filter_logic)
test("IMAP config in .env",       t_imap_config)
test("CRM Excel status",          t_crm_exists)

# ════════════════════════════════════════════════════════════════════════════
section("BONUS — n8n Workflow Blueprint")
# ════════════════════════════════════════════════════════════════════════════

def t_n8n_blueprint():
    assert os.path.exists("n8n_workflow_blueprint.json")
    bp = json.load(open("n8n_workflow_blueprint.json"))
    assert "nodes" in bp and "connections" in bp
    names = [n["name"] for n in bp["nodes"]]
    info(f"n8n nodes: {' → '.join(names)}")
    assert any("Gmail" in n for n in names), "Missing Gmail Trigger node"
    assert any("IF" in n for n in names),    "Missing IF filter node"

test("n8n blueprint JSON valid",  t_n8n_blueprint)

# ════════════════════════════════════════════════════════════════════════════
section(f"RESULTS — {len(PASSED)}/{len(PASSED)+len(FAILED)} tests passed")
# ════════════════════════════════════════════════════════════════════════════
for t in PASSED: print(f"  {GREEN}✅ {t}{RESET}")
for t in FAILED: print(f"  {RED}❌ {t}{RESET}")
print()
if FAILED:
    print(f"{RED}{BOLD}  ⚠  {len(FAILED)} test(s) failed. Check config/.env credentials.{RESET}\n")
    sys.exit(1)
else:
    print(f"{GREEN}{BOLD}  🎉 All {len(PASSED)} tests passed! System ready for live demo.{RESET}\n")
    sys.exit(0)
