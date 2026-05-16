import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

class ExcelManager:
    def __init__(self, file_path="data/ceo_data.xlsx"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_leads(self, df):
        try:
            # Reorder columns to match requirement exactly
            required_cols = [
                "Full Name", "Company Name", "Industry", "Country", 
                "Email Address", "Mobile / Contact", "LinkedIn URL", 
                "Net Worth (USD)", "Company Revenue", "Data Source URL"
            ]
            
            # Ensure all columns exist
            for col in required_cols:
                if col not in df.columns:
                    df[col] = "N/A"
            
            df_final = df[required_cols]

            # Save with formatting
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                df_final.to_excel(writer, index=False, sheet_name='CEOs')
                
                # Access the workbook and sheet for formatting
                workbook = writer.book
                worksheet = writer.sheets['CEOs']
                
                # Formatting: Header
                header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")

                # Auto-adjust column width
                for col in worksheet.columns:
                    max_length = 0
                    column = col[0].column_letter
                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column].width = adjusted_width

            print(f"✅ Leads saved successfully to {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving leads to Excel: {e}")
            return False

    def load_leads(self):
        if os.path.exists(self.file_path):
            return pd.read_excel(self.file_path)
        return None
