import imaplib
import email
import time
import smtplib
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv
from src.manager.excel_manager import ExcelManager

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
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "auto_reply_template.txt")

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
        # Assuming 'Email' column exists
        match = df[df["Email"].str.lower() == sender_email.lower()] if "Email" in df.columns else pd.DataFrame()
        
        if not match.empty:
            full_name = match.iloc[0]["Full Name"] if "Full Name" in match.columns else sender_name
            first_name = full_name.split()[0] if full_name else sender_name
            company = match.iloc[0]["Company Name"] if "Company Name" in match.columns else "your company"
        else:
            first_name = sender_name.split()[0] if sender_name else "there"
            company = "your company"

        with open(TEMPLATE_PATH, "r") as f:
            template = f.read()
            
        return template.replace("{{first_name}}", first_name) \
                       .replace("{{company}}", company) \
                       .replace("{{meeting_link}}", "https://calendly.com/yourname")
    except Exception as e:
        print(f"Error building auto-reply: {e}")
        return f"Hi {sender_name},\n\nThank you for your reply. I will get back to you soon."

def send_auto_reply(to_email, to_name, original_subject):
    body = get_auto_reply(to_email, to_name)
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = f"Re: {original_subject}"
    
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(EMAIL_USER, EMAIL_PASS)
            s.sendmail(EMAIL_USER, to_email, msg.as_string())
        
        print(f"[{datetime.now()}] Sent auto-reply to {to_name} <{to_email}>")
        log_reply_to_excel(to_email, to_name, original_subject, body)
    except Exception as e:
        print(f"Failed to send auto-reply: {e}")

def listen_inbox():
    seen_ids = set()
    print(f"[{datetime.now()}] Auto-reply listener started. Monitoring {EMAIL_USER}...")
    
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select("inbox")
            
            # Search for unseen messages
            _, ids = mail.search(None, "UNSEEN")
            
            for num in ids[0].split():
                if num in seen_ids:
                    continue
                
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                
                # Parse sender
                sender_raw = msg.get("From")
                sender_name, sender_email = email.utils.parseaddr(sender_raw)
                
                # Parse subject
                subject = decode_str(msg.get("Subject"))
                
                print(f"[{datetime.now()}] Detected reply from {sender_name} <{sender_email}>: {subject}")
                
                # Send auto-reply
                send_auto_reply(sender_email, sender_name, subject)
                
                seen_ids.add(num)
                
            mail.logout()
        except Exception as e:
            print(f"Error in listener loop: {e}")
            
        time.sleep(60) # Poll every 60 seconds

if __name__ == "__main__":
    listen_inbox()
