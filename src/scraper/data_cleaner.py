import re
import pandas as pd
import validators

class DataCleaner:
    @staticmethod
    def validate_email(email):
        if not email or pd.isna(email):
            return False
        try:
            return validators.email(email) is True
        except:
            return False

    @staticmethod
    def clean_text(text):
        if not text or pd.isna(text):
            return ""
        # Remove extra whitespace and special characters
        text = re.sub(r'\s+', ' ', str(text)).strip()
        # Remove common Wikipedia artifacts like [1], [note 1], etc.
        text = re.sub(r'\[\d+\]|\[note \d+\]', '', text)
        return text

    @staticmethod
    def standardise_country(country):
        # Placeholder for country mapping if needed
        return DataCleaner.clean_text(country)

    @staticmethod
    def clean_ceo_df(df):
        print("Cleaning and validating data...")
        # Deduplicate
        df = df.drop_duplicates(subset=['Company Name', 'Full Name'], keep='first')
        
        # Clean text fields
        text_cols = ['Full Name', 'Company Name', 'Industry', 'Country', 'LinkedIn URL']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].apply(DataCleaner.clean_text)

        # Validate emails
        if 'Email Address' in df.columns:
            df['Is_Email_Valid'] = df['Email Address'].apply(DataCleaner.validate_email)

        return df
