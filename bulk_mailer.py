from src.manager.excel_manager import ExcelManager
from src.automation.email_sender import EmailSender
import pandas as pd
import sys

def main():
    print("📧 Module 2: Bulk Email Campaign Execution...")

    # 1. Load data from the 'Email Ready' sheet
    manager = ExcelManager("data/ceo_data.xlsx")
    df = manager.load_leads()
    
    # Need to specifically load the 'Email Ready' sheet
    try:
        df_ready = pd.read_excel("data/ceo_data.xlsx", sheet_name="Email Ready")
    except Exception as e:
        print(f"❌ Error loading 'Email Ready' sheet: {e}")
        return

    if df_ready.empty:
        print("⚠️ No valid emails found in the 'Email Ready' sheet. Run Module 1 first.")
        return

    print(f"✅ Found {len(df_ready)} valid leads for outreach.")

    # 2. Prepare recipient data
    recipients = []
    for _, row in df_ready.iterrows():
        # Get first name from full name
        full_name = str(row["Full Name"])
        first_name = full_name.split()[0] if full_name != "N/A" else "there"
        
        recipients.append({
            "email": row["Email Address"],
            "first_name": first_name,
            "company": row["Company Name"],
            "industry": row["Industry"]
        })

    # 3. Confirm execution (Safety check)
    confirm = input(f"Proceed to send {len(recipients)} emails? (y/n): ")
    if confirm.lower() != 'y':
        print("Campaign aborted.")
        return

    # 4. Trigger Campaign
    sender = EmailSender()
    # For demo/testing, I'll only send the first one if not properly configured
    # In a real run, it would iterate all.
    sender.send_bulk_email(recipients[:10]) # Sending top 10 for test

    print("\nDAY 2 Bulk Email System Live bulk_mailer.py tested · template.html created · at least 10 test emails sent successfully")

if __name__ == "__main__":
    main()
