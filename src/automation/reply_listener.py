import imaplib
import email
import time
import smtplib
import pandas as pd
import os
import socket
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv
from src.manager.excel_manager import ExcelManager

# Force IPv4 connection to bypass broken IPv6 route to host on some servers
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(*args, **kwargs):
    responses = orig_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = patched_getaddrinfo

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", ".env")
load_dotenv(dotenv_path)

# Configuration
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
EMAIL_USER = os.getenv("REPLY_TO_USER", os.getenv("SMTP_USER", "replies@yourdomain.com"))
EMAIL_PASS = os.getenv("REPLY_TO_PASS", os.getenv("SMTP_PASS", "YOUR_APP_PASSWORD"))
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CEO_DATA_PATH = os.path.join(BASE_DIR, "data", "ceo_data.xlsx")
TEMPLATE_PATH = os.path.join(BASE_DIR, "auto_reply_template.txt")

def decode_str(s):
    if s is None:
        return ""
    decoded_fragments = decode_header(s)
    result = ""
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            result += fragment.decode(encoding or "utf-8")
        else:
            result += fragment
    return result

def log_reply_to_excel(sender_email, sender_name, subject, body):
    """Append replied status + timestamp + reply text to Sheet 3 'Replies Log'"""
    manager = ExcelManager(CEO_DATA_PATH)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply_text = body[:200] + "..." if len(body) > 200 else body
    
    if manager.log_reply(timestamp, sender_name, sender_email, subject, reply_text):
        print(f"[{datetime.now()}] Logged reply from {sender_email} to Excel.")
    else:
        print(f"[{datetime.now()}] Failed to log reply to Excel.")

def get_auto_reply(sender_email, sender_name):
    try:
        df = pd.read_excel(CEO_DATA_PATH)
        # 4. LOOKUP CRM Lookup
        # Cross-reference sender email with ceo_data.xlsx to get CEO's first name + company
        match = df[df["Email Address"].str.lower() == sender_email.lower()] if "Email Address" in df.columns else pd.DataFrame()
        
        if not match.empty:
            full_name = match.iloc[0]["Full Name"] if "Full Name" in match.columns else sender_name
            first_name = full_name.split()[0] if full_name else sender_name
            company = match.iloc[0]["Company Name"] if "Company Name" in match.columns else "your company"
        else:
            first_name = sender_name.split()[0] if sender_name else "there"
            company = "your company"

        # 5. COMPOSE Build Auto-Reply
        # Load auto-reply template and inject {{first_name}}, {{company}}, {{meeting_link}}
        with open(TEMPLATE_PATH, "r") as f:
            template = f.read()
            
        return template.replace("{{first_name}}", first_name) \
                       .replace("{{company}}", company) \
                       .replace("{{meeting_link}}", "https://calendly.com/yourname")
    except Exception as e:
        print(f"Error building auto-reply: {e}")
        return f"Hi {sender_name},\n\nThank you for your reply. I will get back to you soon."

def send_auto_reply(to_email, to_name, original_subject, message_id=None):
    body = get_auto_reply(to_email, to_name)
    
    from_email = EMAIL_USER
    from_name = os.getenv("FROM_NAME", "Uttamraj Singh from Bitlance")
    
    # Construct MIME message
    msg = MIMEMultipart("alternative")
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = f"{to_name} <{to_email}>"
    
    # Strip duplicate "Re:" if already exists
    subject_clean = original_subject
    if subject_clean and not subject_clean.strip().lower().startswith("re:"):
        subject_clean = f"Re: {subject_clean}"
    msg['Subject'] = subject_clean
    
    # Add Threading Headers to keep in the previous chat thread
    if message_id:
        msg['In-Reply-To'] = message_id
        msg['References'] = message_id
    
    # Plain text and HTML versions
    text_part = MIMEText(body, "plain")
    html_part = MIMEText(body.replace("\n", "<br>"), "html")
    msg.attach(text_part)
    msg.attach(html_part)
    
    # Send using robust Gmail SMTP with automatic retry and Port 465 / 587 fallback
    max_retries = 3
    success = False
    
    for attempt in range(1, max_retries + 1):
        # We try port 465 (SSL) and port 587 (STARTTLS)
        for port in [465, 587]:
            try:
                print(f"[{datetime.now()}] Attempting to send auto-reply to {to_email} (Attempt {attempt}/{max_retries}, Port {port})...")
                if port == 465:
                    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20)
                else:
                    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
                    server.starttls()
                
                with server:
                    server.login(EMAIL_USER, EMAIL_PASS)
                    server.sendmail(from_email, to_email, msg.as_string())
                
                print(f"[{datetime.now()}] Sent auto-reply to {to_name} <{to_email}>")
                # Append replied status + timestamp + reply text to Sheet 3 'Replies Log' in Excel
                log_reply_to_excel(to_email, to_name, original_subject, body)
                success = True
                break
            except Exception as e:
                print(f"[{datetime.now()}] Port {port} failed on attempt {attempt}: {e}")
                
        if success:
            break
        if attempt < max_retries:
            print(f"[{datetime.now()}] Retrying SMTP send in 2 seconds...")
            time.sleep(2)
            
    if not success:
        print(f"[{datetime.now()}] ❌ Failed to send auto-reply via Gmail SMTP after all attempts.")

def listen_inbox():
    seen_ids = set()
    print(f"[{datetime.now()}] Auto-reply listener started. Monitoring {EMAIL_USER}...")
    
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select("inbox")
            
            # 1. LISTEN Monitor Inbox
            # Use IMAP / Gmail API to poll replies@yourdomain.com every 60 seconds
            _, ids = mail.search(None, "UNSEEN")
            unseen_count = len(ids[0].split())
            print(f"[{datetime.now()}] Polling inbox... Found {unseen_count} unread emails.")
            
            # 3. CRM FILTER PREPARATION: Read CRM once per polling interval
            crm_emails = set()
            try:
                if os.path.exists(CEO_DATA_PATH):
                    df = pd.read_excel(CEO_DATA_PATH)
                    if "Email Address" in df.columns:
                        crm_emails = set(df["Email Address"].dropna().str.lower().str.strip())
            except Exception as e:
                print(f"[{datetime.now()}] Warning: failed to pre-load CRM emails: {e}")
            
            # Fetch only the 50 most recent unread emails to prevent hanging on 15,000+ old unread spams
            for num in ids[0].split()[-50:]:
                if num in seen_ids:
                    continue
                
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                
                # 3. PARSE Extract Sender
                # Parse sender name + email from the From: header of the incoming reply
                sender_raw = msg.get("From")
                sender_name, sender_email = email.utils.parseaddr(sender_raw)
                
                # Parse subject and check headers for reply detection
                subject = decode_str(msg.get("Subject"))
                in_reply_to = msg.get("In-Reply-To")
                references = msg.get("References")
                
                # 3. CRM FILTER: Check if the sender is actually one of the CEOs whom we sent the mail
                is_in_crm = False
                if crm_emails:
                    is_in_crm = sender_email.lower().strip() in crm_emails
                else:
                    # Fallback to true if CRM list is empty or couldn't load to avoid blocking replies
                    is_in_crm = True
                
                if not is_in_crm:
                    seen_ids.add(num)
                    continue # Silently skip! No logs printed.

                # 2. DETECT Identify Reply
                # Match incoming email Thread-ID, In-Reply-To header, or 'Re:' in the subject
                is_reply = False
                if in_reply_to or references:
                    is_reply = True
                elif subject and (subject.lower().startswith("re:") or "re :" in subject.lower()):
                    is_reply = True

                if not is_reply:
                    seen_ids.add(num)
                    continue
                
                print(f"[{datetime.now()}] Detected reply from {sender_name} <{sender_email}>: {subject}")
                
                # Extract Message-ID to thread the auto-reply inside the same conversation
                message_id = msg.get("Message-ID")
                
                # Send auto-reply
                send_auto_reply(sender_email, sender_name, subject, message_id)
                
                seen_ids.add(num)
                
            mail.logout()
        except Exception as e:
            print(f"Error in listener loop: {e}")
            
        time.sleep(60) # Poll every 60 seconds

if __name__ == "__main__":
    listen_inbox()
