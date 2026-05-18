import pandas as pd
from src.manager.excel_manager import ExcelManager

test_data = [
    {
        "Full Name": "Test CEO",
        "Company Name": "Bitlance Tech Hub",
        "Industry": "Technology",
        "Country": "Global",
        "Email Address": "ceo@bitlancetechhub.com",
        "Mobile / Contact": "N/A",
        "LinkedIn URL": "https://linkedin.com",
        "Net Worth (USD)": "Billionaire Status",
        "Company Revenue": "N/A",
        "Data Source URL": "N/A",
        "Company Wiki URL": "N/A"
    },
    {
        "Full Name": "Test HR",
        "Company Name": "Bitlance Tech Hub",
        "Industry": "Technology",
        "Country": "Global",
        "Email Address": "hr@bitlancetechhub.com",
        "Mobile / Contact": "N/A",
        "LinkedIn URL": "https://linkedin.com",
        "Net Worth (USD)": "Billionaire Status",
        "Company Revenue": "N/A",
        "Data Source URL": "N/A",
        "Company Wiki URL": "N/A"
    },
    {
        "Full Name": "Test Sashank",
        "Company Name": "Bitlance Tech Hub",
        "Industry": "Technology",
        "Country": "Global",
        "Email Address": "sashanksingh363@gmail.com",
        "Mobile / Contact": "N/A",
        "LinkedIn URL": "https://linkedin.com",
        "Net Worth (USD)": "Billionaire Status",
        "Company Revenue": "N/A",
        "Data Source URL": "N/A",
        "Company Wiki URL": "N/A"
    },
    {
        "Full Name": "Sashank",
        "Company Name": "Bitlance Tech Hub",
        "Industry": "Technology",
        "Country": "Global",
        "Email Address": "sashanksingh12205@gmail.com",
        "Mobile / Contact": "N/A",
        "LinkedIn URL": "https://linkedin.com",
        "Net Worth (USD)": "Billionaire Status",
        "Company Revenue": "N/A",
        "Data Source URL": "N/A",
        "Company Wiki URL": "N/A"
    }
]

df_test = pd.DataFrame(test_data)

# Read existing scraped data so we append our test emails to the 100 scraped CEOs!
try:
    df_existing = pd.read_excel("data/ceo_data.xlsx", sheet_name="CEO Master List")
    # Concatenate both dataframes
    df = pd.concat([df_test, df_existing], ignore_index=True)
    df = df.drop_duplicates(subset=["Email Address"], keep="first")
    print("🔄 Appended test emails to the existing 100 scraped CEOs!")
except Exception as e:
    # If file doesn't exist, just use the test data
    df = df_test
    print("🆕 Excel file not found. Created a new one with test data.")

manager = ExcelManager()
manager.save_leads(df)
print("✅ Test data injected into data/ceo_data.xlsx")
