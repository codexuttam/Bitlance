import smtplib
import time
import os
import hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import pandas as pd

load_dotenv("config/.env")

class EmailSender:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "smtp.sendgrid.net")
        self.port = int(os.getenv("SMTP_PORT", 587))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")
        
        self.from_name = os.getenv("FROM_NAME", "John from Bitlance")
        self.from_email = os.getenv("FROM_EMAIL", "outreach@yourdomain.com")
        self.reply_to = os.getenv("REPLY_TO", "replies@yourdomain.com")
        
        self.template_path = "template.html"

    def _get_template(self):
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r') as f:
                return f.read()
        return "Hi {{first_name}}, I'm reaching out from {{company}}."

    def send_bulk_email(self, recipient_data):
        """
        recipient_data: list of dicts with {email, first_name, company, industry}
        """
        print(f"🚀 Starting bulk email campaign for {len(recipient_data)} recipients...")
        
        sent_count = 0
        failed_count = 0
        
        try:
            # Using context manager for SMTP connection to handle login once if possible, 
            # though some providers prefer fresh connections for long batches.
            # For 50 emails/hour, we can reconnect or stay open.
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            if self.user and self.password:
                server.login(self.user, self.password)
            
            template = self._get_template()

            for i, data in enumerate(recipient_data):
                try:
                    to_email = data['email']
                    first_name = data['first_name']
                    company = data['company']
                    industry = data.get('industry', 'your industry')
                    
                    msg = MIMEMultipart("alternative")
                    msg["From"] = f"{self.from_name} <{self.from_email}>"
                    msg["To"] = to_email
                    msg["Reply-To"] = self.reply_to
                    msg["Subject"] = f"Quick question for you, {first_name}"
                    
                    # Generate email hash for tracking pixel
                    email_hash = hashlib.md5(to_email.encode()).hexdigest()
                    
                    # Personalize Body
                    body = template.replace("{{first_name}}", first_name)
                    body = body.replace("{{company}}", company)
                    body = body.replace("{{industry}}", industry)
                    body = body.replace("{{email_hash}}", email_hash)
                    body = body.replace("{{unsubscribe_link}}", f"https://bitlance.ai/unsubscribe?id={email_hash}")
                    
                    msg.attach(MIMEText(body, "html"))
                    
                    server.sendmail(self.from_email, to_email, msg.as_string())
                    
                    sent_count += 1
                    print(f"[{i+1}/{len(recipient_data)}] ✓ Sent to {first_name} ({to_email})")
                    
                    # Rate Limiting: Max 50 emails/hour -> 3600/50 = 72 seconds delay
                    if i < len(recipient_data) - 1:
                        print(f"Sleeping for 72s to respect rate limits...")
                        time.sleep(72) 
                        
                except Exception as e:
                    print(f"❌ Failed to send to {data.get('email')}: {e}")
                    failed_count += 1
            
            server.quit()
            
        except Exception as e:
            print(f"⛔ SMTP Connection Error: {e}")
            return False

        print(f"\n📊 Campaign Complete. Sent: {sent_count} | Failed: {failed_count}")
        return True

if __name__ == "__main__":
    print("📧 Running Bulk Mailer deliverable...")
    
    # 1. Load data
    try:
        df_ready = pd.read_excel("ceo_data.xlsx", sheet_name="Email Ready")
    except Exception as e:
        print(f"❌ Error loading 'Email Ready' sheet: {e}. Run scraper.py first.")
        exit(1)

    if df_ready.empty:
        print("⚠️ No valid emails found. Run scraper.py first.")
        exit(1)

    # 2. Prepare recipients
    recipients = []
    for _, row in df_ready.iterrows():
        full_name = str(row["Full Name"])
        first_name = full_name.split()[0] if full_name != "N/A" else "there"
        recipients.append({
            "email": row["Email Address"],
            "first_name": first_name,
            "company": row["Company Name"],
            "industry": row["Industry"]
        })

    # 3. Trigger
    sender = EmailSender()
    confirm = input(f"Proceed to send {len(recipients)} emails? (y/n): ")
    if confirm.lower() == 'y':
        sender.send_bulk_email(recipients[:5]) # Demo limit
        print("\n✅ Campaign execution finished.")
    else:
        print("Campaign aborted.")
