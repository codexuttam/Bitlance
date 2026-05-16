from src.scraper.ceo_scraper import CEOScraper
from src.manager.excel_manager import ExcelManager
import pandas as pd
import os

def main():
    print("🚀 Module 1: Starting CEO Data Extraction & Excel Storage...")

    # 1. Initialize Scraper and Run Pipeline
    scraper = CEOScraper()
    # Scrape 50 CEOs as per Step S3
    df = scraper.run_full_pipeline(limit=50)
    
    if df.empty:
        print("❌ Data extraction failed.")
        return

    # 2. Save to Excel
    # The ExcelManager now defaults to data/ceo_data.xlsx as requested
    manager = ExcelManager()
    manager.save_leads(df)

    print("\n📊 Extraction Summary:")
    print(f"Total CEOs Extracted: {len(df)}")
    print(f"Valid Emails Found: {df['Is_Email_Valid'].sum() if 'Is_Email_Valid' in df.columns else 'N/A'}")
    
    print("\n✅ Module 1 Complete: data/ceo_data.xlsx is ready.")
    print("Time remaining to Deadline: ~68 Hours.")

if __name__ == "__main__":
    main()
