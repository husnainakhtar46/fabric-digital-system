"""
Simple Google Sheets API client for Android
Uses public URL access instead of gspread (which doesn't work on Android)
"""
import requests
import json

class GoogleSheetsClient:
    """Fetch data from a published Google Sheet"""
    
    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        # Uses the public JSON endpoint for published sheets
        self.base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json"
    
    def get_all_data(self, sheet_name="fabric_library"):
        """Fetch all data from the sheet"""
        try:
            url = f"{self.base_url}&sheet={sheet_name}"
            response = requests.get(url, timeout=10)
            
            # Google returns JSONP, need to strip the wrapper
            text = response.text
            # Remove "/*O_o*/\ngoogle.visualization.Query.setResponse(" and ");"
            start = text.find('(') + 1
            end = text.rfind(')')
            json_str = text[start:end]
            
            data = json.loads(json_str)
            return self._parse_table(data)
        except Exception as e:
            print(f"Error fetching sheet: {e}")
            return []
    
    def _parse_table(self, data):
        """Parse Google's visualization format into list of dicts"""
        try:
            table = data.get('table', {})
            cols = [c.get('label', f'col{i}') for i, c in enumerate(table.get('cols', []))]
            rows = []
            
            for row in table.get('rows', []):
                cells = row.get('c', [])
                row_dict = {}
                for i, cell in enumerate(cells):
                    if cell:
                        row_dict[cols[i]] = cell.get('v', '')
                    else:
                        row_dict[cols[i]] = ''
                rows.append(row_dict)
            
            return rows
        except Exception as e:
            print(f"Error parsing: {e}")
            return []
    
    def find_by_code(self, fabric_code, sheet_name="fabric_library"):
        """Find a fabric by its code"""
        all_data = self.get_all_data(sheet_name)
        for row in all_data:
            if row.get('Fabric_Code') == fabric_code:
                return row
        return None
