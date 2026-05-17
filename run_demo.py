from src.scraper.ceo_scraper import CEOScraper
from src.manager.excel_manager import ExcelManager
import pandas as pd
import os

def main():
    print("🚀 Module 1 Finalization: CEO Data Extraction & Multi-Sheet Excel Storage...")

    # 1. Initialize Scraper and Run Pipeline
    scraper = CEOScraper()
    # Scrape 10 CEOs using the Forbes API for real-life data demonstration
    df = scraper.run_full_pipeline(limit=10, use_forbes=True)
    
    if df.empty:
        print("❌ Data extraction failed.")
        return

    # 2. Save to Excel
    # The ExcelManager now handles dual sheets, formatting, and sorting
    manager = ExcelManager()
    manager.save_leads(df)

    print("\n📊 Extraction Summary:")
    print(f"Total CEOs Extracted: {len(df)}")
    if 'Is_Email_Valid' in df.columns:
        valid_count = df['Is_Email_Valid'].sum()
        print(f"Verified Emails (Green): {valid_count}")
        print(f"Unverified Emails (Yellow): {len(df) - valid_count}")
    
    print("\n✅ Module 1 Complete: data/ceo_data.xlsx is finalized with all formatting.")
    print("Sheet 1: 'CEO Master List'")
    print("Sheet 2: 'Email Ready'")
    print("Time remaining to Deadline: ~67 Hours.")

if __name__ == "__main__":
    main()
