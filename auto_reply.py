import imaplib
import email
import time
import smtplib
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from src.manager.excel_manager import ExcelManager

# Load configuration
load_dotenv("config/.env")

# Global Configuration (Matches 3.3 Skeleton)
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
EMAIL_USER = os.getenv("REPLY_TO_USER", "replies@yourdomain.com")
EMAIL_PASS = os.getenv("REPLY_TO_PASS", "YOUR_APP_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

def get_auto_reply(sender_email, sender_name):
    """
    Builds the auto-reply body by looking up the sender in the CRM (Excel).
    Matches 3.3 Skeleton logic.
    """
    try:
        df = pd.read_excel("ceo_data.xlsx")
        # Match incoming email to sent emails log
        match = df[df["Email Address"].str.lower() == sender_email.lower()] if "Email Address" in df.columns else pd.DataFrame()
        
        first_name = match.iloc[0]["Full Name"].split()[0] if not match.empty else sender_name
        company = match.iloc[0]["Company Name"] if not match.empty else "your company"
        
        # Load template
        template = open("auto_reply_template.txt").read()
        
        return template.replace("{{first_name}}", first_name) \
                       .replace("{{company}}", company) \
                       .replace("{{meeting_link}}", "https://calendly.com/yourname")
    except Exception as e:
        print(f"Error building auto-reply: {e}")
        return f"Hi {sender_name},\n\nThank you for your reply! I'll follow up soon."

def send_auto_reply(to_email, to_name, original_subject):
    """
    Dispatches the personalized auto-reply.
    Matches 3.3 Skeleton structure.
    """
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
            
        print(f"[{datetime.now()}] Auto-replied to {to_name} <{to_email}>")
        
        # Step 7: Record to Excel (Requirement 3.1)
        manager = ExcelManager("ceo_data.xlsx")
        manager.log_reply(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            to_name,
            to_email,
            original_subject,
            body[:200] + "..."
        )
    except Exception as e:
        print(f"Failed to dispatch reply: {e}")

def listen_inbox():
    """
    Monitors Inbox every 60 seconds for unread replies.
    Matches 3.3 Skeleton loop.
    """
    seen = set()
    print("Auto-reply listener started...")
    
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select("inbox")
            
            _, ids = mail.search(None, "UNSEEN")
            
            for num in ids[0].split():
                if num in seen: 
                    continue
                seen.add(num)
                
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                sender = email.utils.parseaddr(msg["From"]) # Parse sender name + email
                
                # Step 6: Send personalized auto-reply
                send_auto_reply(sender[1], sender[0], msg["Subject"])
                
            mail.logout()
        except Exception as e:
            print(f"Listener error: {e}")
            
        time.sleep(60) # Poll every 60 seconds

if __name__ == "__main__":
    listen_inbox()
