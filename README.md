# Fabric Digital System

A text-based fabric management system using Google Sheets as a database, with Admin (Windows) and Customer (Mobile) applications.

## Features

- **Admin App (Windows)**: Enter fabric specifications and generate QR codes
- **Mobile App**: Scan QR codes to view fabric details
- **Cloud Storage**: Google Sheets for centralized data
- **Text-Only**: Currently displays specifications without images (images planned for future release)

## Installation

1. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Setup Google Cloud Credentials:**
   - Follow the guide in `google_cloud_setup.md`
   - Place your `credentials.json` in this directory
   - Share your Google Sheet `fabric_library` with the service account email

## Usage

### Admin App (Data Entry)

```powershell
python -m admin_app.main
```

1. Fill in fabric specifications
2. Click "SAVE & GENERATE QR"
3. Data saves to Google Sheets
4. QR code generates locally as `{FabricCode}_QR.png`

### Mobile App (Customer View)

```powershell
python -m mobile_app.main
```

1. Camera opens for QR scanning
2. Present printed QR code to camera
3. View fabric specifications

## File Structure

```
Fabric/
├── admin_app/          # Windows admin application
│   ├── main.py         # Entry point
│   └── ui_style.py     # Dark mode stylesheet
├── backend/            # Shared logic
│   ├── google_services.py  # Sheets/Drive API wrapper
│   └── data_models.py      # Data structures
├── mobile_app/         # Mobile customer application
│   └── main.py         # Kivy app with QR scanner
├── requirements.txt    # Python dependencies
├── credentials.json    # Google service account key (you provide)
└── google_cloud_setup.md  # Setup instructions
```

## Data Schema

The Google Sheet `fabric_library` contains:

| Column | Description |
|--------|-------------|
| Fabric_Code | Primary identifier (required) |
| Supplier | Manufacturer/supplier name |
| MoQ | Minimum order quantity |
| Category | Fabric type (e.g., Denim) |
| Status | Availability status |
| Composition | Material composition |
| Shade | Color/shade |
| BW_Weight | Fabric weight |
| Finish | Finishing treatment |
| Width | Fabric width in inches |
| Warp_Shrink | Warp shrinkage percentage |
| Weft_Shrink | Weft shrinkage percentage |
| Weave | Weave pattern |
| Stretch | Stretch percentage |
| Growth | Growth percentage |
| Main_Img_ID | (Reserved for future use) |
| Wash_Img_IDs | (Reserved for future use) |

## Future Enhancements

- Image upload/display functionality
- Cloud storage integration (AWS S3, Azure Blob, etc.)
- Full database backend (PostgreSQL, MongoDB)
- Multi-user authentication
- Batch data import/export

## Troubleshooting

See `google_cloud_setup.md` for detailed setup instructions and common issues.
