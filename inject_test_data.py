import pandas as pd
from src.manager.excel_manager import ExcelManager, TEST_LEADS

# Read existing scraped data so we append our test emails to the 100 scraped CEOs!
try:
    df_existing = pd.read_excel("data/ceo_data.xlsx", sheet_name="CEO Master List")
    # ExcelManager.save_leads automatically injects TEST_LEADS and ensures they are at the top of 'Email Ready'.
    df = df_existing
    print("🔄 Appending test emails to the existing scraped CEOs...")
except Exception as e:
    # If file doesn't exist, start with empty DataFrame (save_leads will inject TEST_LEADS)
    df = pd.DataFrame()
    print("🆕 Excel file not found. Initializing a new one with test data...")

manager = ExcelManager()
manager.save_leads(df)
print("✅ Test data injected into data/ceo_data.xlsx")

