# 🚀 PPSA Analytics Dashboard

Dashboard analytics untuk monitoring performa PPSA (PSM, PWP, SG, APC) dan Tebus Suuegerr.

## 🛠️ Teknologi

- **Framework**: Dash/Plotly
- **Styling**: Bootstrap + Custom CSS
- **Data Source**: Google Sheets
- **Deployment**: Render

## 🔧 Environment Variables

Wajib diatur di Render:

1. **GCP_SERVICE_ACCOUNT**: JSON credentials untuk Google Sheets API
2. **SPREADSHEET_ID**: ID dari Google Spreadsheet (dapat dari URL)
3. **WORKSHEET_NAME**: Nama worksheet/tab (opsional, default: Sheet1)

## 📋 Cara Mendapatkan SPREADSHEET_ID

1. Buka Google Sheets Anda
2. Copy ID dari URL: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
3. Set sebagai environment variable di Render

## 🔐 Setup Google Sheets API

1. Enable Google Sheets API & Google Drive API di Google Cloud Console
2. Buat service account dan download JSON key
3. Share Google Sheet dengan email service account (Editor permission)
4. Copy JSON content ke environment variable `GCP_SERVICE_ACCOUNT`

## 🌐 Deployment di Render

1. Push code ke GitHub
2. Connect repository ke Render
3. Set environment variables:
   - `GCP_SERVICE_ACCOUNT`
   - `SPREADSHEET_ID` 
   - `WORKSHEET_NAME` (optional)
4. Deploy!

## 🐛 Troubleshooting

Jika data tidak muncul:
1. Periksa Config Debug tab
2. Pastikan SPREADSHEET_ID benar
3. Pastikan service account memiliki akses ke sheet
4. Pastikan WORKSHEET_NAME sesuai (case-sensitive)

## 📊 Fitur

- 📈 PPSA Analytics
- 🛒 Tebus Analytics  
- 🔍 Deep Insights
- 🎯 Performance Alerts
- 🕐 Performance Shift
- 📅 Performance Per Hari
- 🔧 Config Debug
