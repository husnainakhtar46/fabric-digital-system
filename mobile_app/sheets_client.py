"""
Simple Google Sheets client for Android
Fetches data from published Google Sheets via CSV export
"""
import requests
import csv
from io import StringIO

class GoogleSheetsClient:
    """Fetch data from a published Google Sheet"""
    
    def __init__(self, sheet_id):
        """
        sheet_id: The ID from your Google Sheets URL
        e.g., if URL is https://docs.google.com/spreadsheets/d/ABC123/edit
        then sheet_id is ABC123
        """
        self.sheet_id = sheet_id
        # CSV export URL for published sheets
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    def get_all_data(self):
        """Fetch all data from the sheet as list of dicts"""
        try:
            response = requests.get(self.csv_url, timeout=15)
            response.raise_for_status()
            
            # Parse CSV
            reader = csv.DictReader(StringIO(response.text))
            return list(reader)
        except Exception as e:
            print(f"Error fetching sheet: {e}")
            return []
    
    def find_by_code(self, fabric_code):
        """Find a fabric by its Fabric_Code"""
        all_data = self.get_all_data()
        for row in all_data:
            # Check various possible column names
            code = row.get('Fabric_Code') or row.get('fabric_code') or row.get('Code') or ''
            if code.strip().upper() == fabric_code.strip().upper():
                return row
        return None

