import smtplib
import time
import os
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load configuration from environment
load_dotenv("config/.env")

# SMTP Configuration (Matches 2.3 Skeleton)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.sendgrid.net")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "apikey")
SMTP_PASS = os.getenv("SMTP_PASS", "YOUR_SENDGRID_API_KEY")
REPLY_TO = os.getenv("REPLY_TO", "replies@yourdomain.com")
FROM_NAME = os.getenv("FROM_NAME", "John Smith")
FROM_EMAIL = os.getenv("FROM_EMAIL", "outreach@yourdomain.com")

def send_email(to_email, first_name, company, industry="your industry"):
    """
    Sends a personalized email using the HTML template.
    Matches the function signature in the 2.3 skeleton.
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Reply-To"] = REPLY_TO
    msg["Subject"] = f"Quick question for you, {first_name}"

    try:
        # Load template (Matches 2.3 logic)
        with open("template.html", "r") as f:
            body = f.read()
        
        # Personalization
        body = body.replace("{{first_name}}", first_name)
        body = body.replace("{{company}}", company)
        body = body.replace("{{industry}}", industry)
        body = body.replace("{{unsubscribe_link}}", f"https://bitlance.ai/unsubscribe?email={to_email}")
        
        # Attach HTML content
        msg.attach(MIMEText(body, "html"))

        # SMTP Connection and Send
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(msg["From"], to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"❌ Failed to send to {to_email}: {e}")
        return False

if __name__ == "__main__":
    print("📧 Module 2: Starting Bulk Mailer Execution...")
    
    # 1. Load Data (Matches 2.3 Skeleton)
    try:
        df = pd.read_excel("ceo_data.xlsx", sheet_name="Email Ready")
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        exit(1)

    sent, failed = [], []

    # 2. Iterate and Send (Matches 2.3 Loop)
    for _, row in df.iterrows():
        try:
            # Extract first name and company
            first_name = str(row["Full Name"]).split()[0]
            company = str(row["Company Name"])
            to_email = str(row["Email Address"])
            industry = str(row.get("Industry", "your industry"))

            # Send personalized email
            if send_email(to_email, first_name, company, industry):
                sent.append(to_email)
                print(f"✓ Sent to {row['Full Name']} <{to_email}>")
            else:
                failed.append({"email": to_email, "error": "SMTP Error"})
                
        except Exception as e:
            failed.append({"email": row.get("Email Address", "Unknown"), "error": str(e)})
            print(f"❌ Error processing row: {e}")

        # Rate Limiting (Matches 2.3 requirement: ~50 emails/hour)
        time.sleep(72)

    print(f"\nDone. Sent: {len(sent)} | Failed: {len(failed)}")
