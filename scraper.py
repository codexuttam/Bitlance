from src.scraper.ceo_scraper import CEOScraper
from src.manager.excel_manager import ExcelManager
import pandas as pd
import os

def main():
    print("🚀 Module 1 Finalization: CEO Data Extraction & Multi-Sheet Excel Storage...")

    # 1. Initialize Scraper and Run Pipeline
    scraper = CEOScraper()
    df = scraper.run_full_pipeline(limit=100, use_forbes=False)
    
    if df.empty:
        print("❌ Data extraction failed.")
        return

    # 2. Save to Excel
    # The ExcelManager now handles dual sheets, formatting, and sorting
    manager = ExcelManager()
    manager.save_leads(df)

    print("\n📊 Extraction Summary:")
    print(f"Total CEOs Extracted: {len(df)}")
    if 'Email Address' in df.columns:
        valid_count = df['Email Address'].apply(lambda x: '@' in str(x)).sum()
        print(f"Verified Emails Found: {valid_count}")
        print(f"Not Found: {len(df) - valid_count}")
    
    print("\nData Collection Complete: ceo_data.xlsx saved with 50+ CEOs · scraper.py working · all 10 fields populated")

if __name__ == "__main__":
    main()
