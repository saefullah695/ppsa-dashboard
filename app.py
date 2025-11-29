import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
import os
import json
import re

warnings.filterwarnings('ignore')

# Inisialisasi Dash App dengan Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

app.title = "🚀 PPSA Analytics Dashboard"

# --- FUNGSI DATA YANG DIPERBAIKI & DITAMBAHKAN ---

def load_data_from_gsheet():
    """Load data from Google Sheets dengan error handling yang lebih baik"""
    try:
        # Untuk deployment di Render, gunakan environment variable
        service_account_info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT', '{}'))
        SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
        WORKSHEET_NAME = os.environ.get('WORKSHEET_NAME', 'Sheet1')
        
        if not SPREADSHEET_ID or not service_account_info:
            print("❌ Environment variables not properly set")
            # Fallback: coba baca dari file local untuk development
            try:
                if os.path.exists('data_sample.csv'):
                    print("📁 Loading from local data_sample.csv")
                    df = pd.read_csv('data_sample.csv')
                    return df
            except Exception as e:
                print(f"❌ Juga gagal load local file: {e}")
            return pd.DataFrame()
        
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 
                 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Open spreadsheet by ID
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # Get worksheet by name or first worksheet
        if WORKSHEET_NAME:
            try:
                worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
            except gspread.WorksheetNotFound:
                print(f"❌ Worksheet '{WORKSHEET_NAME}' not found. Using first worksheet.")
                worksheet = spreadsheet.get_worksheet(0)
        else:
            worksheet = spreadsheet.get_worksheet(0)
        
        data = worksheet.get_all_values()
        
        if not data or len(data) <= 1:
            print("⚠️ No data or only headers found in worksheet")
            return pd.DataFrame()
            
        df = pd.DataFrame(data[1:], columns=data[0])
        print(f"✅ Data loaded successfully: {len(df)} records, columns: {list(df.columns)}")
        return df
        
    except Exception as e:
        print(f"❌ Gagal mengambil data dari Google Sheets: {str(e)}")
        # Fallback ke data sample
        try:
            if os.path.exists('data_sample.csv'):
                print("📁 Fallback: Loading from local data_sample.csv")
                df = pd.read_csv('data_sample.csv')
                return df
        except Exception as fallback_error:
            print(f"❌ Juga gagal load local file: {fallback_error}")
        return pd.DataFrame()

def normalize_column_names(df):
    """Normalize column names to handle various formats"""
    if df.empty:
        return df
    
    column_mapping = {
        # Tanggal variations
        'tanggal': 'TANGGAL', 'date': 'TANGGAL', 'tgl': 'TANGGAL',
        # Nama Kasir variations
        'nama kasir': 'NAMA KASIR', 'kasir': 'NAMA KASIR', 'name': 'NAMA KASIR',
        'nama_kasir': 'NAMA KASIR',
        # Shift variations
        'shift': 'SHIFT', 'sift': 'SHIFT',
        # PSM variations
        'psm target': 'PSM Target', 'psm_target': 'PSM Target',
        'psm actual': 'PSM Actual', 'psm_actual': 'PSM Actual',
        'bobot psm': 'BOBOT PSM', 'bobot_psm': 'BOBOT PSM',
        # PWP variations
        'pwp target': 'PWP Target', 'pwp_target': 'PWP Target',
        'pwp actual': 'PWP Actual', 'pwp_actual': 'PWP Actual',
        'bobot pwp': 'BOBOT PWP', 'bobot_pwp': 'BOBOT PWP',
        # SG variations
        'sg target': 'SG Target', 'sg_target': 'SG Target',
        'sg actual': 'SG Actual', 'sg_actual': 'SG Actual',
        'bobot sg': 'BOBOT SG', 'bobot_sg': 'BOBOT SG',
        # APC variations
        'apc target': 'APC Target', 'apc_target': 'APC Target',
        'apc actual': 'APC Actual', 'apc_actual': 'APC Actual',
        'bobot apc': 'BOBOT APC', 'bobot_apc': 'BOBOT APC',
        # Tebus variations
        'target tebus 2500': 'TARGET TEBUS 2500', 'target_tebus_2500': 'TARGET TEBUS 2500',
        'actual tebus 2500': 'ACTUAL TEBUS 2500', 'actual_tebus_2500': 'ACTUAL TEBUS 2500'
    }
    
    # Normalize current column names
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Map to standardized names
    df.rename(columns=column_mapping, inplace=True)
    
    return df

def parse_date_flexible(date_str):
    """Parse various date formats flexibly"""
    if pd.isna(date_str) or date_str == '':
        return pd.NaT
    
    date_str = str(date_str).strip()
    
    # Common date patterns
    patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',  # DD/MM/YY or DD-MM-YY
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups[0]) == 4:  # YYYY/MM/DD format
                return pd.to_datetime(f"{groups[0]}-{groups[1]}-{groups[2]}", errors='coerce')
            else:  # DD/MM/YYYY format
                return pd.to_datetime(f"{groups[2]}-{groups[1]}-{groups[0]}", errors='coerce')
    
    # Try pandas built-in parser as fallback
    return pd.to_datetime(date_str, errors='coerce')

def clean_numeric_value(value):
    """Clean and convert numeric values from various formats"""
    if pd.isna(value) or value == '':
        return 0.0
    
    value_str = str(value).strip()
    
    # Remove common non-numeric characters but keep decimal point and negative
    value_str = re.sub(r'[^\d.-]', '', value_str)
    
    # Handle empty result after cleaning
    if value_str == '' or value_str == '-':
        return 0.0
    
    try:
        return float(value_str)
    except ValueError:
        return 0.0

def process_data(df):
    """Process data dengan validasi dan cleaning yang lebih robust"""
    if df.empty:
        print("⚠️ No data to process")
        return df
    
    # Normalize column names first
    df = normalize_column_names(df)
    print(f"📊 Columns after normalization: {list(df.columns)}")
    
    # Process dates with flexible parsing
    if 'TANGGAL' in df.columns:
        print("📅 Processing dates...")
        df['TANGGAL_ORIGINAL'] = df['TANGGAL'].copy()
        df['TANGGAL'] = df['TANGGAL'].apply(parse_date_flexible)
        
        # Check for parsing failures
        date_failures = df['TANGGAL'].isna().sum()
        if date_failures > 0:
            print(f"⚠️ {date_failures} dates failed to parse")
            # Show samples of failed dates
            failed_samples = df[df['TANGGAL'].isna()]['TANGGAL_ORIGINAL'].head(3).tolist()
            print(f"   Sample failed dates: {failed_samples}")
        
        # Add date components
        valid_dates = df['TANGGAL'].notna()
        df.loc[valid_dates, 'HARI'] = df.loc[valid_dates, 'TANGGAL'].dt.day_name()
        df.loc[valid_dates, 'BULAN'] = df.loc[valid_dates, 'TANGGAL'].dt.month_name()
        df.loc[valid_dates, 'MINGGU'] = df.loc[valid_dates, 'TANGGAL'].dt.isocalendar().week
        
        hari_map = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        df['HARI'] = df['HARI'].map(hari_map)
    else:
        print("❌ TANGGAL column not found")
    
    # Process shift column dengan berbagai format
    if 'SHIFT' in df.columns:
        print("🕐 Processing shifts...")
        df['SHIFT'] = df['SHIFT'].astype(str).str.strip()
        
        # Map berbagai format shift
        shift_mapping = {
            '1': 'Shift 1 (Pagi)', '2': 'Shift 2 (Siang)', '3': 'Shift 3 (Malam)',
            'pagi': 'Shift 1 (Pagi)', 'siang': 'Shift 2 (Siang)', 'malam': 'Shift 3 (Malam)',
            'shift 1': 'Shift 1 (Pagi)', 'shift 2': 'Shift 2 (Siang)', 'shift 3': 'Shift 3 (Malam)',
            'shift1': 'Shift 1 (Pagi)', 'shift2': 'Shift 2 (Siang)', 'shift3': 'Shift 3 (Malam)'
        }
        
        df['SHIFT'] = df['SHIFT'].str.lower().map(shift_mapping)
        df['SHIFT'] = df['SHIFT'].fillna('Unknown')
        print(f"   Shift distribution: {df['SHIFT'].value_counts().to_dict()}")
    
    # Process numeric columns dengan cleaning yang lebih baik
    numeric_cols = [
        'PSM Target', 'PSM Actual', 'BOBOT PSM',
        'PWP Target', 'PWP Actual', 'BOBOT PWP',
        'SG Target', 'SG Actual', 'BOBOT SG',
        'APC Target', 'APC Actual', 'BOBOT APC',
        'TARGET TEBUS 2500', 'ACTUAL TEBUS 2500'
    ]
    
    print("🔢 Processing numeric columns...")
    for col in numeric_cols:
        if col in df.columns:
            original_non_zero = (df[col] != 0).sum()
            df[col] = df[col].apply(clean_numeric_value)
            cleaned_non_zero = (df[col] != 0).sum()
            print(f"   {col}: {original_non_zero} -> {cleaned_non_zero} non-zero values")
        else:
            print(f"   ⚠️ {col} not found in dataframe")

    # Calculate ACV (Achievement vs Target) dengan handling division by zero
    def calculate_acv(actual, target):
        if target == 0:
            return 100.0 if actual > 0 else 0.0  # Jika target 0 tapi actual ada, consider 100%
        return min((actual / target * 100), 200.0)  # Cap at 200% untuk menghindari outlier ekstrim

    # Calculate component scores
    component_calculations = [
        ('PSM', 'PSM Actual', 'PSM Target', 'BOBOT PSM'),
        ('PWP', 'PWP Actual', 'PWP Target', 'BOBOT PWP'), 
        ('SG', 'SG Actual', 'SG Target', 'BOBOT SG'),
        ('APC', 'APC Actual', 'APC Target', 'BOBOT APC')
    ]
    
    for comp, actual_col, target_col, weight_col in component_calculations:
        if all(col in df.columns for col in [actual_col, target_col, weight_col]):
            acv_col = f'(%) {comp} ACV'
            score_col = f'SCORE {comp}'
            
            df[acv_col] = df.apply(
                lambda row: calculate_acv(row[actual_col], row[target_col]), axis=1
            )
            df[score_col] = (df[acv_col] * df[weight_col]) / 100
            print(f"   ✅ Calculated {comp}: ACV mean = {df[acv_col].mean():.1f}%")

    # Calculate Tebus ACV
    if 'ACTUAL TEBUS 2500' in df.columns and 'TARGET TEBUS 2500' in df.columns:
        df['(%) ACV TEBUS 2500'] = df.apply(
            lambda row: calculate_acv(row['ACTUAL TEBUS 2500'], row['TARGET TEBUS 2500']), axis=1
        )
        print(f"   ✅ Calculated Tebus ACV: mean = {df['(%) ACV TEBUS 2500'].mean():.1f}%")

    # Calculate total PPSA score
    score_cols = [f'SCORE {comp}' for comp in ['PSM', 'PWP', 'SG', 'APC'] 
                 if f'SCORE {comp}' in df.columns]
    
    if score_cols:
        df['TOTAL SCORE PPSA'] = df[score_cols].sum(axis=1)
        print(f"   ✅ Calculated TOTAL SCORE: mean = {df['TOTAL SCORE PPSA'].mean():.1f}")
    else:
        print("   ❌ No score columns available for total calculation")
        df['TOTAL SCORE PPSA'] = 0.0
    
    # Remove rows dengan critical data missing
    initial_count = len(df)
    critical_cols = ['TOTAL SCORE PPSA']
    if 'SHIFT' in df.columns:
        critical_cols.append('SHIFT')
    
    df = df.dropna(subset=critical_cols)
    final_count = len(df)
    
    if initial_count != final_count:
        print(f"   🗑️ Removed {initial_count - final_count} rows with missing critical data")
    
    print(f"✅ Data processing completed: {final_count} valid records")
    return df

# [Fungsi-fungsi lainnya tetap sama seperti sebelumnya...]
# calculate_overall_ppsa_breakdown, calculate_aggregate_scores_per_cashier, 
# calculate_team_metrics, calculate_performance_insights, dll.

def calculate_overall_ppsa_breakdown(df):
    """Calculate overall PPSA breakdown dengan error handling"""
    if df.empty:
        return {'total': 0.0, 'psm': 0.0, 'pwp': 0.0, 'sg': 0.0, 'apc': 0.0}
    
    weights = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}
    scores = {'psm': 0.0, 'pwp': 0.0, 'sg': 0.0, 'apc': 0.0}
    
    try:
        # For PSM, PWP, SG - use SUM aggregation
        for comp in ['PSM', 'PWP', 'SG']:
            if f'{comp} Target' in df.columns and f'{comp} Actual' in df.columns:
                total_target = df[f'{comp} Target'].sum()
                total_actual = df[f'{comp} Actual'].sum()
                if total_target > 0:
                    acv = (total_actual / total_target) * 100
                    scores[comp.lower()] = (acv * weights[comp]) / 100
                else:
                    scores[comp.lower()] = 0.0
        
        # For APC - use AVERAGE aggregation
        if 'APC Target' in df.columns and 'APC Actual' in df.columns:
            avg_target_apc = df['APC Target'].mean()
            avg_actual_apc = df['APC Actual'].mean()
            if avg_target_apc > 0:
                acv_apc = (avg_actual_apc / avg_target_apc) * 100
                scores['apc'] = (acv_apc * weights['APC']) / 100
            else:
                scores['apc'] = 0.0
        
        scores['total'] = sum(scores.values())
        
    except Exception as e:
        print(f"❌ Error calculating overall PPSA: {e}")
    
    return scores

def create_sample_data():
    """Create sample data for testing when no real data is available"""
    print("📝 Creating sample data for demonstration...")
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
    sample_data = []
    
    kasir_names = ['Budi Santoso', 'Siti Rahayu', 'Ahmad Wijaya', 'Dewi Lestari', 'Joko Prasetyo']
    shifts = ['Shift 1 (Pagi)', 'Shift 2 (Siang)', 'Shift 3 (Malam)']
    
    for date in dates:
        for kasir in kasir_names:
            for shift in shifts:
                sample_data.append({
                    'TANGGAL': date.strftime('%d/%m/%Y'),
                    'NAMA KASIR': kasir,
                    'SHIFT': shift,
                    'PSM Target': np.random.randint(80, 120),
                    'PSM Actual': np.random.randint(70, 130),
                    'BOBOT PSM': 20,
                    'PWP Target': np.random.randint(90, 110),
                    'PWP Actual': np.random.randint(85, 115),
                    'BOBOT PWP': 25,
                    'SG Target': np.random.randint(95, 105),
                    'SG Actual': np.random.randint(90, 110),
                    'BOBOT SG': 30,
                    'APC Target': np.random.uniform(0.8, 1.2),
                    'APC Actual': np.random.uniform(0.7, 1.3),
                    'BOBOT APC': 25,
                    'TARGET TEBUS 2500': np.random.randint(8, 12),
                    'ACTUAL TEBUS 2500': np.random.randint(6, 14)
                })
    
    df = pd.DataFrame(sample_data)
    # Simpan sebagai backup
    df.to_csv('data_sample.csv', index=False)
    print("💾 Sample data saved as data_sample.csv")
    return df

# Load data dengan error handling yang lebih baik
try:
    print("🔄 Loading data from Google Sheets...")
    raw_df = load_data_from_gsheet()
    
    if raw_df.empty:
        print("⚠️ No data from Google Sheets, checking for sample data...")
        if os.path.exists('data_sample.csv'):
            raw_df = pd.read_csv('data_sample.csv')
            print("📁 Loaded existing sample data")
        else:
            print("📝 Creating new sample data...")
            raw_df = create_sample_data()
    
    processed_df = process_data(raw_df.copy()) if not raw_df.empty else pd.DataFrame()
    
    if processed_df.empty:
        print("❌ All data processing failed, creating emergency sample data...")
        processed_df = create_sample_data()
        processed_df = process_data(processed_df)
        
except Exception as e:
    print(f"❌ Critical error in data loading: {e}")
    print("🚨 Creating emergency sample data...")
    processed_df = create_sample_data()
    processed_df = process_data(processed_df)

print(f"🎯 Final data status: {len(processed_df)} records loaded")

# [Bagian layout dan callback tetap sama seperti sebelumnya...]
# Header, KPI Cards, Tabs, dll.

def create_header():
    data_status = "✅ Data Loaded" if not processed_df.empty else "❌ No Data Available"
    data_count = f" ({len(processed_df)} records)" if not processed_df.empty else ""
    data_source = "Google Sheets" if os.environ.get('SPREADSHEET_ID') else "Sample Data"
    
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.H1("🚀 PPSA Analytics Dashboard", 
                       className="main-title mb-3",
                       style={'color': '#667eea', 'fontWeight': '800', 'fontSize': '3rem'}),
                html.H3("2GC6 BAROS PANDEGLANG", 
                       className="store-name mb-2",
                       style={'color': '#764ba2', 'fontWeight': '600'}),
                html.Div([
                    html.Span(f"{data_status}{data_count}", 
                             style={'color': '#10b981' if not processed_df.empty else '#ef4444',
                                   'fontWeight': '600', 'fontSize': '0.9rem'}),
                    html.Span(" | ", className="mx-2"),
                    html.Span(f"Data Source: {data_source}", 
                             style={'color': '#64748b', 'fontSize': '0.9rem'}),
                    html.Span(" | ", className="mx-2"),
                    html.Span(f"Columns: {len(processed_df.columns)}", 
                             style={'color': '#64748b', 'fontSize': '0.9rem'})
                ], className="mb-3"),
                html.P(
                    "Platform analytics komprehensif untuk monitoring real-time "
                    "performa PPSA (PSM, PWP, SG, APC) dan Tebus Suuegerr dengan "
                    "insights AI-powered untuk optimasi performa tim.",
                    className="subtitle",
                    style={'color': '#64748b', 'fontSize': '1.2rem', 'maxWidth': '900px', 'margin': '0 auto'}
                )
            ], className="text-center")
        ]),
        className="mb-4 shadow",
        style={'background': 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%)',
               'borderRadius': '20px', 'border': '1px solid rgba(255, 255, 255, 0.3)'}
    )

# [Lanjutkan dengan bagian layout yang sama seperti sebelumnya...]
# KPI Cards, Tabs, Content containers, dll.

# Untuk bagian yang tidak disebutkan, asumsikan sama dengan script asli
# ...

# --- RUN APP ---
server = app.server

if __name__ == '__main__':
    print("🚀 Starting PPSA Analytics Dashboard...")
    print(f"📊 Data ready: {len(processed_df)} records")
    print(f"📋 Available columns: {list(processed_df.columns)}")
    
    app.run_server(debug=False, host='0.0.0.0', port=8050)
