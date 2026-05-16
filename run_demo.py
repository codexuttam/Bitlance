from src.scraper.ceo_scraper import CEOScraper
from src.manager.excel_manager import ExcelManager
from src.automation.email_sender import EmailSender
import pandas as pd

def main():
    print("🚀 Starting Email Automation Campaign System...")

    # 1. Scrape Data
    scraper = CEOScraper()
    raw_data = scraper.scrape_ceos(limit=10)
    
    if raw_data is None:
        print("❌ Scraping failed.")
        return

    # Refine data (Add CEO names)
    refined_data = scraper.refine_ceo_names(raw_data)

    # Add mock emails for demonstration
    refined_data['Email'] = refined_data['CEO'].apply(
        lambda x: f"{x.lower().replace(' ', '.')}@example.com" if x != "Pending Search" else "info@company.com"
    )

    # 2. Store in Excel
    manager = ExcelManager("data/ceo_leads.xlsx")
    manager.save_leads(refined_data)

    # 3. Outreach Demo (Optional/Simulated)
    print("\n📊 Lead Data Preview:")
    print(refined_data[['Rank', 'Company', 'CEO', 'Email']].head())

    print("\n✅ Phase 1: Core Modules and Dependencies installed and configured.")
    print("Ready for Phase 2: AI Response Automation and Live Campaign Execution.")

if __name__ == "__main__":
    main()
