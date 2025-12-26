import os
import io
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import gspread
from PIL import Image

# Scopes required
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

CREDENTIALS_FILE = 'credentials.json'

class GoogleServices:
    def __init__(self, credentials_path=None):
        if credentials_path is None:
            # Look in project root
            credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), CREDENTIALS_FILE)
        
        self.credentials_path = credentials_path
        self.creds = None
        self.sheet_client = None
        self.drive_service = None
        
        if os.path.exists(self.credentials_path):
            self.authenticate()
        else:
            print(f"Warning: {CREDENTIALS_FILE} not found at {self.credentials_path}")

    def authenticate(self):
        try:
            self.creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            # Authenticate gspread
            self.sheet_client = gspread.authorize(self.creds)
            # Authenticate Drive API
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            print("Google Services Authenticated Successfully.")
        except Exception as e:
            print(f"Authentication Failed: {e}")

    def find_folder_id_by_name(self, folder_name):
        """Searches for a folder by name and returns its ID."""
        if not self.drive_service:
            print("Drive Service not authenticated")
            return None
            
        try:
            query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
            results = self.drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = results.get('files', [])
            
            if files:
                print(f"Found folder '{folder_name}' with ID: {files[0]['id']}")
                return files[0]['id']
            else:
                print(f"Folder '{folder_name}' not found.")
                return None
        except Exception as e:
            print(f"Folder searching error: {e}")
            return None

    def upload_image_to_drive(self, file_path, folder_id_or_name=None, transfer_to_email=None):
        """
        Resizes image to max 800px width, uploads to Drive, makes it public, returns ID.
        If folder_id_or_name is provided, tries to resolve it as a name first, then uses it as ID.
        If transfer_to_email is provided, transfers ownership to that email (avoids service account quota).
        """
        if not self.drive_service:
            raise Exception("Drive Service not authenticated")
            
        try:
            folder_id = folder_id_or_name
            # heuristic: if it contains spaces or is 'fabric_library', check if it's a name
            # Or just always try to resolve name first if provided
            if folder_id_or_name:
                resolved_id = self.find_folder_id_by_name(folder_id_or_name)
                if resolved_id:
                    folder_id = resolved_id
                # If not found as name, we assume it IS the ID and proceed.

            # 1. Optimize Image
            img = Image.open(file_path)
            # Resize if width > 800
            if img.width > 800:
                ratio = 800 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((800, new_height), Image.Resampling.LANCZOS)
            
            # Save to byte stream (don't write to disk just for upload)
            img_byte_arr = io.BytesIO()
            # Convert to RGB if RGBA (e.g. png) to save as JPEG safely, or keep format
            fmt = img.format if img.format else 'JPEG'
            img.save(img_byte_arr, format=fmt, quality=85)
            img_byte_arr.seek(0)
            
            file_name = os.path.basename(file_path)
            
            # 2. Prepare Metadata
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaIoBaseUpload(img_byte_arr, mimetype=f'image/{fmt.lower()}', resumable=True)
            
            # 3. Upload
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            
            # 4. Transfer ownership if specified (CRITICAL for service accounts with no quota)
            if transfer_to_email:
                try:
                    # First, add the user as owner
                    self.drive_service.permissions().create(
                        fileId=file_id,
                        body={
                            'role': 'owner',
                            'type': 'user',
                            'emailAddress': transfer_to_email
                        },
                        transferOwnership=True
                    ).execute()
                    print(f"Ownership transferred to: {transfer_to_email}")
                except Exception as transfer_error:
                    print(f"Warning: Could not transfer ownership: {transfer_error}")
                    # Continue anyway - file is uploaded
            
            # 5. Set Permissions (Anyone with link can view)
            self.drive_service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'},
            ).execute()
            
            print(f"Upload successful: {file_id}")
            return file_id
        except Exception as e:
            print(f"Image upload failed: {e}")
            raise  # Re-raise the exception so UI can show exact error

    def initialize_sheet_headers(self, sheet_name):
        """Creates the headers if the sheet is empty."""
        if not self.sheet_client:
             raise Exception("Sheet Client not authenticated")
        
        try:
            sheet = self.sheet_client.open(sheet_name).sheet1
            existing = sheet.get_all_values()
            if not existing:
                headers = [
                    "Fabric_Code", "Supplier", "MoQ", "Category", "Status",
                    "Composition", "Shade", "BW_Weight", "Finish", "Width",
                    "Warp_Shrink", "Weft_Shrink", "Weave", "Stretch", "Growth",
                    "Main_Img_ID", "Wash_Img_IDs"
                ]
                sheet.append_row(headers)
                print("Headers initialized.")
            else:
                print("Sheet already has data.")
        except Exception as e:
            print(f"Sheet initialization failed: {e}")

    def append_fabric_row(self, sheet_name, row_data):
        """Appends a list of values to the sheet."""
        if not self.sheet_client:
             raise Exception("Sheet Client not authenticated")
        
        try:
            sheet = self.sheet_client.open(sheet_name).sheet1
            sheet.append_row(row_data)
            return True
        except Exception as e:
            print(f"Failed to append row: {e}")
            return False

    def get_fabric_details(self, sheet_name, fabric_code):
        """Searches for a fabric code and returns the row as dict."""
        if not self.sheet_client:
             raise Exception("Sheet Client not authenticated")

        try:
            sheet = self.sheet_client.open(sheet_name).sheet1
            records = sheet.get_all_records()
            for record in records:
                if str(record.get("Fabric_Code")) == str(fabric_code):
                    return record
            return None
        except Exception as e:
             print(f"Lookup failed: {e}")
             return None
