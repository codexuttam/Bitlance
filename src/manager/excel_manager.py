import pandas as pd
import os

class ExcelManager:
    def __init__(self, file_path="data/ceo_leads.xlsx"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_leads(self, df):
        try:
            df.to_excel(self.file_path, index=False)
            print(f"Leads saved successfully to {self.file_path}")
            return True
        except Exception as e:
            print(f"Error saving leads to Excel: {e}")
            return False

    def load_leads(self):
        try:
            if os.path.exists(self.file_path):
                return pd.read_excel(self.file_path)
            else:
                print(f"File {self.file_path} not found.")
                return None
        except Exception as e:
            print(f"Error loading leads from Excel: {e}")
            return None

    def update_lead_status(self, company_name, status_col, status_val):
        df = self.load_leads()
        if df is not None:
            if company_name in df['Company'].values:
                df.loc[df['Company'] == company_name, status_col] = status_val
                self.save_leads(df)
                return True
        return False
