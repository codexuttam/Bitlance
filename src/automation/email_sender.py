import yagmail
import os
from dotenv import load_dotenv

load_dotenv("config/.env")

class EmailSender:
    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        
        if self.email_user and self.email_pass:
            try:
                self.yag = yagmail.SMTP(self.email_user, self.email_pass)
                print(f"SMTP connected as {self.email_user}")
            except Exception as e:
                print(f"Failed to connect to SMTP: {e}")
                self.yag = None
        else:
            print("Email credentials not found in .env")
            self.yag = None

    def send_personalized_email(self, to_email, ceo_name, company_name):
        if not self.yag:
            print("SMTP not initialized. Check credentials.")
            return False

        subject = f"Strategic Collaboration Proposal for {company_name}"
        body = f"""
        Dear {ceo_name},

        I hope this email finds you well. 

        I have been following {company_name}'s recent growth and am highly impressed by your leadership. 
        We are reaching out to explore potential synergy between our organizations.

        Would you be open to a brief 10-minute introductory call next week?

        Best regards,
        [Your Name/Company]
        """
        
        try:
            self.yag.send(to=to_email, subject=subject, contents=body)
            print(f"Email sent to {ceo_name} ({to_email})")
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False
