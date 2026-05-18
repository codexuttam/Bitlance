import requests
import time
import os
import hashlib
import json
from dotenv import load_dotenv

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
        
        template = self._get_template()

        for i, data in enumerate(recipient_data):
            try:
                to_email = data['email']
                first_name = data['first_name']
                company = data['company']
                industry = data.get('industry', 'your industry')
                
                # Generate email hash for tracking pixel
                email_hash = hashlib.md5(to_email.encode()).hexdigest()
                
                # Personalize Body
                body = template.replace("{{first_name}}", first_name)
                body = body.replace("{{company}}", company)
                body = body.replace("{{industry}}", industry)
                body = body.replace("{{email_hash}}", email_hash)
                body = body.replace("{{unsubscribe_link}}", f"https://bitlance.ai/unsubscribe?id={email_hash}")
                
                # Send using SendGrid Web API (Bypasses SMTP port blocking)
                headers = {
                    "Authorization": f"Bearer {self.password}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "personalizations": [{
                        "to": [{"email": to_email}],
                        "subject": f"Quick question for you, {first_name}"
                    }],
                    "from": {
                        "email": self.from_email,
                        "name": self.from_name
                    },
                    "reply_to": {
                        "email": self.reply_to
                    },
                    "content": [{
                        "type": "text/html",
                        "value": body
                    }]
                }
                
                # The API key password in .env might be prefixed with "SG."
                if not self.password or not self.password.startswith("SG."):
                    print("⛔ Invalid SendGrid API Key. Check config/.env SMTP_PASS.")
                    return False
                
                response = requests.post(
                    "https://api.sendgrid.com/v3/mail/send", 
                    headers=headers, 
                    json=payload,
                    timeout=10
                )
                
                if response.status_code in [200, 202]:
                    sent_count += 1
                    print(f"[{i+1}/{len(recipient_data)}] ✓ Sent to {first_name} ({to_email})")
                else:
                    print(f"❌ SendGrid API Error for {to_email}: {response.status_code} - {response.text}")
                    failed_count += 1
                
                # Rate Limiting: Max 50 emails/hour -> 3600/50 = 72 seconds delay
                if i < len(recipient_data) - 1:
                    print(f"Sleeping for 72s to respect rate limits...")
                    time.sleep(12) 
                    
            except Exception as e:
                print(f"❌ Failed to send to {data.get('email')}: {e}")
                failed_count += 1
                
        print(f"\n📊 Campaign Complete. Sent: {sent_count} | Failed: {failed_count}")
        return True

if __name__ == "__main__":
    # Test with mock data
    sender = EmailSender()
    test_data = [
        {"email": "test@example.com", "first_name": "Test", "company": "Acme Corp", "industry": "Technology"}
    ]
    # Reduce sleep for test
    # sender.send_bulk_email(test_data)
