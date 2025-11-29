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
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "theme-color", content": "#667eea"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"}
    ]
)

app.title = "🚀 PPSA Analytics Dashboard"

# CSS Custom untuk Mobile
mobile_css = {
    'custom-css': '''
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --dark-gradient: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #f8f9fa;
            overflow-x: hidden;
        }
        
        .mobile-header {
            background: var(--primary-gradient);
            color: white;
            padding: 1rem;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }
        
        .mobile-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.1);
            transform: rotate(30deg);
        }
        
        .kpi-card-mobile {
            background: white;
            border-radius: 16px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 4px solid;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .kpi-card-mobile:active {
            transform: scale(0.98);
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }
        
        .main-score-card {
            background: var(--primary-gradient);
            color: white;
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .main-score-card::after {
            content: '';
            position: absolute;
            top: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }
        
        .nav-tab-mobile {
            background: white;
            border-radius: 50px;
            padding: 0.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            display: flex;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }
        
        .nav-tab-mobile::-webkit-scrollbar {
            display: none;
        }
        
        .nav-tab-item {
            flex: 0 0 auto;
            padding: 0.75rem 1.25rem;
            margin: 0 0.25rem;
            border-radius: 25px;
            background: transparent;
            color: #64748b;
            font-weight: 600;
            font-size: 0.85rem;
            white-space: nowrap;
            transition: all 0.3s ease;
            border: none;
        }
        
        .nav-tab-item.active {
            background: var(--primary-gradient);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .content-section {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        
        .insight-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 16px;
            padding: 1.25rem;
            margin: 0.75rem 0;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
        }
        
        .floating-action-btn {
            position: fixed;
            bottom: 2rem;
            right: 1rem;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--primary-gradient);
            color: white;
            border: none;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .floating-action-btn:active {
            transform: scale(0.9);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.6);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin: 1rem 0;
        }
        
        .stat-item {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #f1f5f9;
        }
        
        @media (max-width: 768px) {
            .container-fluid {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            .main-title {
                font-size: 1.75rem !important;
            }
            
            .store-name {
                font-size: 1.1rem !important;
            }
        }
        
        .swipe-indicator {
            text-align: center;
            color: #94a3b8;
            font-size: 0.8rem;
            margin: 0.5rem 0;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .performance-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.25rem;
        }
        
        .badge-excellent { background: #10b981; color: white; }
        .badge-good { background: #f59e0b; color: white; }
        .badge-average { background: #ef4444; color: white; }
    '''
}

# --- FUNGSI DATA YANG DIPERBAIKI ---

def load_data_from_gsheet():
    """Load data from Google Sheets dengan error handling yang lebih baik"""
    try:
        service_account_info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT', '{}'))
        SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
        WORKSHEET_NAME = os.environ.get('WORKSHEET_NAME', 'Sheet1')
        
        if not SPREADSHEET_ID or not service_account_info:
            print("❌ Environment variables not properly set")
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
        
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
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
        'tanggal': 'TANGGAL', 'date': 'TANGGAL', 'tgl': 'TANGGAL',
        'nama kasir': 'NAMA KASIR', 'kasir': 'NAMA KASIR', 'name': 'NAMA KASIR',
        'nama_kasir': 'NAMA KASIR',
        'shift': 'SHIFT', 'sift': 'SHIFT',
        'psm target': 'PSM Target', 'psm_target': 'PSM Target',
        'psm actual': 'PSM Actual', 'psm_actual': 'PSM Actual',
        'bobot psm': 'BOBOT PSM', 'bobot_psm': 'BOBOT PSM',
        'pwp target': 'PWP Target', 'pwp_target': 'PWP Target',
        'pwp actual': 'PWP Actual', 'pwp_actual': 'PWP Actual',
        'bobot pwp': 'BOBOT PWP', 'bobot_pwp': 'BOBOT PWP',
        'sg target': 'SG Target', 'sg_target': 'SG Target',
        'sg actual': 'SG Actual', 'sg_actual': 'SG Actual',
        'bobot sg': 'BOBOT SG', 'bobot_sg': 'BOBOT SG',
        'apc target': 'APC Target', 'apc_target': 'APC Target',
        'apc actual': 'APC Actual', 'apc_actual': 'APC Actual',
        'bobot apc': 'BOBOT APC', 'bobot_apc': 'BOBOT APC',
        'target tebus 2500': 'TARGET TEBUS 2500', 'target_tebus_2500': 'TARGET TEBUS 2500',
        'actual tebus 2500': 'ACTUAL TEBUS 2500', 'actual_tebus_2500': 'ACTUAL TEBUS 2500'
    }
    
    df.columns = [col.strip().lower() for col in df.columns]
    df.rename(columns=column_mapping, inplace=True)
    
    return df

def parse_date_flexible(date_str):
    """Parse various date formats flexibly"""
    if pd.isna(date_str) or date_str == '':
        return pd.NaT
    
    date_str = str(date_str).strip()
    
    patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups[0]) == 4:
                return pd.to_datetime(f"{groups[0]}-{groups[1]}-{groups[2]}", errors='coerce')
            else:
                return pd.to_datetime(f"{groups[2]}-{groups[1]}-{groups[0]}", errors='coerce')
    
    return pd.to_datetime(date_str, errors='coerce')

def clean_numeric_value(value):
    """Clean and convert numeric values from various formats"""
    if pd.isna(value) or value == '':
        return 0.0
    
    value_str = str(value).strip()
    value_str = re.sub(r'[^\d.-]', '', value_str)
    
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
    
    df = normalize_column_names(df)
    print(f"📊 Columns after normalization: {list(df.columns)}")
    
    if 'TANGGAL' in df.columns:
        print("📅 Processing dates...")
        df['TANGGAL_ORIGINAL'] = df['TANGGAL'].copy()
        df['TANGGAL'] = df['TANGGAL'].apply(parse_date_flexible)
        
        date_failures = df['TANGGAL'].isna().sum()
        if date_failures > 0:
            print(f"⚠️ {date_failures} dates failed to parse")
        
        valid_dates = df['TANGGAL'].notna()
        df.loc[valid_dates, 'HARI'] = df.loc[valid_dates, 'TANGGAL'].dt.day_name()
        df.loc[valid_dates, 'BULAN'] = df.loc[valid_dates, 'TANGGAL'].dt.month_name()
        df.loc[valid_dates, 'MINGGU'] = df.loc[valid_dates, 'TANGGAL'].dt.isocalendar().week
        
        hari_map = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        df['HARI'] = df['HARI'].map(hari_map)
    
    if 'SHIFT' in df.columns:
        print("🕐 Processing shifts...")
        df['SHIFT'] = df['SHIFT'].astype(str).str.strip()
        
        shift_mapping = {
            '1': 'Shift 1 (Pagi)', '2': 'Shift 2 (Siang)', '3': 'Shift 3 (Malam)',
            'pagi': 'Shift 1 (Pagi)', 'siang': 'Shift 2 (Siang)', 'malam': 'Shift 3 (Malam)',
            'shift 1': 'Shift 1 (Pagi)', 'shift 2': 'Shift 2 (Siang)', 'shift 3': 'Shift 3 (Malam)',
            'shift1': 'Shift 1 (Pagi)', 'shift2': 'Shift 2 (Siang)', 'shift3': 'Shift 3 (Malam)'
        }
        
        df['SHIFT'] = df['SHIFT'].str.lower().map(shift_mapping)
        df['SHIFT'] = df['SHIFT'].fillna('Unknown')
    
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
            df[col] = df[col].apply(clean_numeric_value)

    def calculate_acv(actual, target):
        if target == 0:
            return 100.0 if actual > 0 else 0.0
        return min((actual / target * 100), 200.0)

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

    if 'ACTUAL TEBUS 2500' in df.columns and 'TARGET TEBUS 2500' in df.columns:
        df['(%) ACV TEBUS 2500'] = df.apply(
            lambda row: calculate_acv(row['ACTUAL TEBUS 2500'], row['TARGET TEBUS 2500']), axis=1
        )

    score_cols = [f'SCORE {comp}' for comp in ['PSM', 'PWP', 'SG', 'APC'] 
                 if f'SCORE {comp}' in df.columns]
    
    if score_cols:
        df['TOTAL SCORE PPSA'] = df[score_cols].sum(axis=1)
    else:
        df['TOTAL SCORE PPSA'] = 0.0
    
    initial_count = len(df)
    critical_cols = ['TOTAL SCORE PPSA']
    if 'SHIFT' in df.columns:
        critical_cols.append('SHIFT')
    
    df = df.dropna(subset=critical_cols)
    final_count = len(df)
    
    if initial_count != final_count:
        print(f"🗑️ Removed {initial_count - final_count} rows with missing critical data")
    
    print(f"✅ Data processing completed: {final_count} valid records")
    return df

def calculate_overall_ppsa_breakdown(df):
    """Calculate overall PPSA breakdown"""
    if df.empty:
        return {'total': 0.0, 'psm': 0.0, 'pwp': 0.0, 'sg': 0.0, 'apc': 0.0}
    
    weights = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}
    scores = {'psm': 0.0, 'pwp': 0.0, 'sg': 0.0, 'apc': 0.0}
    
    try:
        for comp in ['PSM', 'PWP', 'SG']:
            if f'{comp} Target' in df.columns and f'{comp} Actual' in df.columns:
                total_target = df[f'{comp} Target'].sum()
                total_actual = df[f'{comp} Actual'].sum()
                if total_target > 0:
                    acv = (total_actual / total_target) * 100
                    scores[comp.lower()] = (acv * weights[comp]) / 100
                else:
                    scores[comp.lower()] = 0.0
        
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

def calculate_aggregate_scores_per_cashier(df):
    """Calculate aggregate scores per cashier"""
    if df.empty or 'NAMA KASIR' not in df.columns:
        return pd.DataFrame()
    
    weights = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}
    
    agg_cols = {
        'PSM Target': 'sum', 'PSM Actual': 'sum',
        'PWP Target': 'sum', 'PWP Actual': 'sum',
        'SG Target': 'sum', 'SG Actual': 'sum',
        'APC Target': 'mean', 'APC Actual': 'mean'
    }
    
    valid_agg_cols = {col: func for col, func in agg_cols.items() if col in df.columns}
    aggregated_df = df.groupby('NAMA KASIR')[list(valid_agg_cols.keys())].agg(valid_agg_cols).reset_index()

    def calculate_score_from_agg(row, comp):
        total_target = row[f'{comp} Target']
        total_actual = row[f'{comp} Actual']
        if total_target == 0:
            return 0.0
        acv = (total_actual / total_target) * 100
        return (acv * weights[comp]) / 100

    for comp in ['PSM', 'PWP', 'SG', 'APC']:
        if f'{comp} Target' in aggregated_df.columns and f'{comp} Actual' in aggregated_df.columns:
            aggregated_df[f'SCORE {comp}'] = aggregated_df.apply(
                lambda row: calculate_score_from_agg(row, comp), axis=1
            )
    
    score_cols = [f'SCORE {comp}' for comp in ['PSM', 'PWP', 'SG', 'APC'] 
                 if f'SCORE {comp}' in aggregated_df.columns]
    if score_cols:
        aggregated_df['TOTAL SCORE PPSA'] = aggregated_df[score_cols].sum(axis=1)
    
    if 'TOTAL SCORE PPSA' in df.columns:
        individual_scores = df.groupby('NAMA KASIR')['TOTAL SCORE PPSA'].agg(['std', 'count']).reset_index()
        individual_scores.columns = ['NAMA KASIR', 'SCORE_STD', 'RECORD_COUNT']
        aggregated_df = aggregated_df.merge(individual_scores, on='NAMA KASIR', how='left')
        aggregated_df['CONSISTENCY'] = aggregated_df['SCORE_STD'].fillna(0)
    
    return aggregated_df.sort_values(by='TOTAL SCORE PPSA', ascending=False).reset_index(drop=True)

def calculate_team_metrics(df):
    """Calculate team-wide metrics for display"""
    if df.empty:
        return {}
    
    metrics = {}
    metrics['total_records'] = len(df)
    
    if 'NAMA KASIR' in df.columns:
        metrics['unique_cashiers'] = df['NAMA KASIR'].nunique()
    else:
        metrics['unique_cashiers'] = 0
    
    metrics['avg_score'] = df['TOTAL SCORE PPSA'].mean()
    metrics['median_score'] = df['TOTAL SCORE PPSA'].median()
    metrics['max_score'] = df['TOTAL SCORE PPSA'].max()
    metrics['min_score'] = df['TOTAL SCORE PPSA'].min()
    
    metrics['above_target'] = (df['TOTAL SCORE PPSA'] >= 100).sum()
    metrics['below_target'] = (df['TOTAL SCORE PPSA'] < 100).sum()
    metrics['achievement_rate'] = (metrics['above_target'] / metrics['total_records']) * 100
    
    components = ['PSM', 'PWP', 'SG', 'APC']
    for comp in components:
        if f'SCORE {comp}' in df.columns:
            metrics[f'avg_{comp.lower()}_score'] = df[f'SCORE {comp}'].mean()
    
    if 'ACTUAL TEBUS 2500' in df.columns and 'TARGET TEBUS 2500' in df.columns:
        total_target = df['TARGET TEBUS 2500'].sum()
        total_actual = df['ACTUAL TEBUS 2500'].sum()
        metrics['tebus_acv'] = (total_actual / total_target * 100) if total_target > 0 else 0
    
    return metrics

def calculate_performance_insights(df):
    """Generate automated insights dari data"""
    insights = []
    
    if df.empty:
        return insights
    
    overall_scores = calculate_overall_ppsa_breakdown(df)
    if overall_scores['total'] >= 100:
        insights.append({
            'type': 'success',
            'title': '🎉 Target Tercapai!',
            'text': f"Total PPSA Score {overall_scores['total']:.1f} telah melampaui target 100."
        })
    else:
        gap = 100 - overall_scores['total']
        insights.append({
            'type': 'warning',
            'title': '⚠️ Gap Performa',
            'text': f"Masih kurang {gap:.1f} poin untuk mencapai target. Fokus pada komponen dengan gap terbesar."
        })
    
    components = {'PSM': overall_scores['psm'], 'PWP': overall_scores['pwp'], 
                 'SG': overall_scores['sg'], 'APC': overall_scores['apc']}
    targets = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}
    
    best_component = max(components, key=lambda x: components[x]/targets[x])
    worst_component = min(components, key=lambda x: components[x]/targets[x])
    
    insights.append({
        'type': 'info',
        'title': f'🏆 Komponen Terbaik: {best_component}',
        'text': f"Achievement {(components[best_component]/targets[best_component]*100):.1f}% dari target."
    })
    
    if components[worst_component] < targets[worst_component]:
        insights.append({
            'type': 'alert',
            'title': f'🎯 Perlu Perbaikan: {worst_component}',
            'text': f"Hanya mencapai {(components[worst_component]/targets[worst_component]*100):.1f}% dari target."
        })
    
    if 'NAMA KASIR' in df.columns:
        cashier_scores = calculate_aggregate_scores_per_cashier(df)
        if not cashier_scores.empty:
            top_performer = cashier_scores.iloc[0]
            insights.append({
                'type': 'success',
                'title': f'🌟 Top Performer: {top_performer["NAMA KASIR"]}',
                'text': f"Dengan total score {top_performer['TOTAL SCORE PPSA']:.1f}"
            })
            
            if 'CONSISTENCY' in cashier_scores.columns:
                most_consistent = cashier_scores.loc[cashier_scores['CONSISTENCY'].idxmin()]
                insights.append({
                    'type': 'info',
                    'title': f'🎯 Paling Konsisten: {most_consistent["NAMA KASIR"]}',
                    'text': f"Dengan variasi performa terendah (std: {most_consistent['CONSISTENCY']:.1f})"
                })
    
    return insights

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

# --- LAYOUT MOBILE-FRIENDLY YANG KEKINIAN ---

# Mobile Header
def create_mobile_header():
    data_status = "✅ Data Loaded" if not processed_df.empty else "❌ No Data"
    data_count = f" ({len(processed_df)} records)" if not processed_df.empty else ""
    data_source = "Google Sheets" if os.environ.get('SPREADSHEET_ID') else "Sample Data"
    
    return html.Div([
        html.Div([
            html.Div([
                html.H1("🚀 PPSA Analytics", 
                       className="main-title mb-2",
                       style={'fontWeight': '800', 'fontSize': '2rem', 'margin': '0'}),
                html.H3("2GC6 BAROS PANDEGLANG", 
                       className="store-name mb-3",
                       style={'fontWeight': '600', 'fontSize': '1.1rem', 'opacity': '0.9'}),
                html.Div([
                    html.Span(f"{data_status}{data_count}", 
                             style={'fontWeight': '600', 'fontSize': '0.8rem', 'background': 'rgba(255,255,255,0.2)', 
                                   'padding': '0.25rem 0.75rem', 'borderRadius': '12px'}),
                    html.Br(),
                    html.Small(f"Source: {data_source}", 
                              style={'opacity': '0.8', 'fontSize': '0.7rem'})
                ], className="mb-2"),
            ], className="text-center")
        ], className="mobile-header"),
        
        # Quick Stats Row
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Small("TEAM MEMBERS", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                        html.H5(f"{processed_df['NAMA KASIR'].nunique() if 'NAMA KASIR' in processed_df.columns else 0}", 
                               style={'fontWeight': '700', 'margin': '0'})
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.Small("ACHIEVEMENT", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                        html.H5(f"{(len(processed_df[processed_df['TOTAL SCORE PPSA'] >= 100])/len(processed_df)*100 if len(processed_df) > 0 else 0):.0f}%", 
                               style={'fontWeight': '700', 'margin': '0'})
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.Small("RECORDS", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                        html.H5(f"{len(processed_df)}", 
                               style={'fontWeight': '700', 'margin': '0'})
                    ], className="text-center")
                ], width=4),
            ])
        ], style={'background': 'rgba(255,255,255,0.1)', 'padding': '0.75rem', 'marginTop': '1rem', 'borderRadius': '12px'})
    ])

# KPI Cards untuk Mobile
def create_mobile_kpi_cards():
    overall_scores = calculate_overall_ppsa_breakdown(processed_df) if not processed_df.empty else {'total': 0.0}
    
    kpi_data = [
        {'title': 'PSM SCORE', 'value': overall_scores.get('psm', 0), 'color': '#667eea', 'icon': '📊'},
        {'title': 'PWP SCORE', 'value': overall_scores.get('pwp', 0), 'color': '#764ba2', 'icon': '🛒'},
        {'title': 'SG SCORE', 'value': overall_scores.get('sg', 0), 'color': '#f093fb', 'icon': '🛡️'},
        {'title': 'APC SCORE', 'value': overall_scores.get('apc', 0), 'color': '#4facfe', 'icon': '⚡'},
    ]
    
    cards = []
    for kpi in kpi_data:
        card = dbc.Col([
            html.Div([
                html.Div([
                    html.Span(kpi['icon'], style={'fontSize': '1.5rem', 'marginBottom': '0.5rem'}),
                    html.Div([
                        html.Small(kpi['title'], style={'fontSize': '0.7rem', 'fontWeight': '700', 
                                                       'color': '#64748b', 'textTransform': 'uppercase'}),
                        html.H5(f"{kpi['value']:.1f}", 
                               style={'color': kpi['color'], 'fontWeight': '800', 'margin': '0', 'fontSize': '1.4rem'})
                    ])
                ], className="text-center")
            ], className="kpi-card-mobile", style={'borderLeftColor': kpi['color']})
        ], width=6, className="mb-2")
        cards.append(card)
    
    return dbc.Row(cards, className="g-2")

# Main Score Card untuk Mobile
def create_main_score_card():
    overall_scores = calculate_overall_ppsa_breakdown(processed_df) if not processed_df.empty else {'total': 0.0}
    gap_value = overall_scores['total'] - 100
    gap_color = '#90EE90' if gap_value >= 0 else '#FFB6C1'
    
    return html.Div([
        html.Div([
            html.Span("🏆 TOTAL PPSA SCORE", 
                     style={'fontSize': '0.9rem', 'fontWeight': '700', 'opacity': '0.9'}),
            html.H2(f"{overall_scores['total']:.1f}", 
                   style={'fontWeight': '900', 'fontSize': '3.5rem', 'margin': '1rem 0'}),
            html.Div([
                html.Span(f"Gap: {gap_value:+.1f}", 
                         style={'color': gap_color, 'fontSize': '1rem', 'fontWeight': '600'})
            ])
        ], className="main-score-card")
    ])

# Mobile Navigation Tabs
def create_mobile_nav():
    tabs = [
        {'id': 'tab-overview', 'icon': '📊', 'label': 'Overview', 'active': True},
        {'id': 'tab-performance', 'icon': '🚀', 'label': 'Performance'},
        {'id': 'tab-tebus', 'icon': '🛒', 'label': 'Tebus'},
        {'id': 'tab-insights', 'icon': '🤖', 'label': 'AI Insights'},
        {'id': 'tab-team', 'icon': '👥', 'label': 'Team'},
        {'id': 'tab-analytics', 'icon': '📈', 'label': 'Analytics'},
    ]
    
    tab_buttons = []
    for tab in tabs:
        tab_buttons.append(
            html.Button([
                html.Span(tab['icon'], style={'marginRight': '0.5rem'}),
                html.Span(tab['label'])
            ], 
            id=tab['id'],
            className=f"nav-tab-item {'active' if tab['active'] else ''}",
            n_clicks=0
            )
        )
    
    return html.Div([
        html.Div(tab_buttons, className="nav-tab-mobile"),
        html.Div("← Swipe untuk lebih →", className="swipe-indicator")
    ])

# Content Sections
def create_content_section(title, children, icon=None):
    return html.Div([
        html.Div([
            html.H4([
                html.Span(icon + " " if icon else ""),
                title
            ], style={'fontWeight': '700', 'marginBottom': '1rem', 'color': '#1e293b'})
        ]),
        *children
    ], className="content-section")

# Team Metrics Grid untuk Mobile
def create_team_metrics_grid():
    team_metrics = calculate_team_metrics(processed_df)
    
    metrics = [
        {'label': 'Avg Score', 'value': f"{team_metrics.get('avg_score', 0):.1f}", 'icon': '⭐'},
        {'label': 'Best Score', 'value': f"{team_metrics.get('max_score', 0):.1f}", 'icon': '🏆'},
        {'label': 'Tebus ACV', 'value': f"{team_metrics.get('tebus_acv', 0):.1f}%", 'icon': '🎯'},
        {'label': 'Consistency', 'value': f"{team_metrics.get('achievement_rate', 0):.0f}%", 'icon': '📊'},
    ]
    
    items = []
    for metric in metrics:
        items.append(
            html.Div([
                html.Div([
                    html.Span(metric['icon'], style={'fontSize': '1.2rem', 'marginBottom': '0.5rem'}),
                    html.Div(metric['value'], style={'fontWeight': '700', 'fontSize': '1.1rem', 'margin': '0.25rem 0'}),
                    html.Small(metric['label'], style={'fontSize': '0.7rem', 'color': '#64748b'})
                ], className="text-center")
            ], className="stat-item")
        )
    
    return html.Div(items, className="stats-grid")

# Performance Badges
def create_performance_badges():
    if processed_df.empty or 'NAMA KASIR' not in processed_df.columns:
        return html.Div()
    
    cashier_scores = calculate_aggregate_scores_per_cashier(processed_df)
    if cashier_scores.empty:
        return html.Div()
    
    top_performer = cashier_scores.iloc[0]
    avg_score = cashier_scores['TOTAL SCORE PPSA'].mean()
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("🏆 TOP PERFORMER", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                    html.Div(top_performer['NAMA KASIR'], style={'fontWeight': '700', 'fontSize': '0.9rem'}),
                    html.Div(f"{top_performer['TOTAL SCORE PPSA']:.1f} points", 
                            style={'color': '#667eea', 'fontWeight': '600', 'fontSize': '0.8rem'})
                ], className="text-center")
            ], width=6),
            dbc.Col([
                html.Div([
                    html.Span("📊 TEAM AVERAGE", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                    html.Div(f"{avg_score:.1f}", style={'fontWeight': '700', 'fontSize': '0.9rem'}),
                    html.Div("points", style={'color': '#64748b', 'fontSize': '0.8rem'})
                ], className="text-center")
            ], width=6),
        ])
    ])

# AI Insights Cards
def create_ai_insights():
    insights = calculate_performance_insights(processed_df)
    
    if not insights:
        return html.Div([
            html.Div([
                html.H5("🤖 AI Insights", style={'fontWeight': '700'}),
                html.P("No insights available yet. Continue collecting data for personalized recommendations.", 
                      style={'color': '#64748b', 'fontSize': '0.9rem'})
            ])
        ], className="content-section")
    
    insight_cards = []
    for insight in insights[:3]:  # Limit to 3 insights on mobile
        bg_color = {
            'success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            'info': 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
            'alert': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
        }.get(insight['type'], 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
        
        insight_cards.append(
            html.Div([
                html.H5(insight['title'], style={'fontWeight': '700', 'marginBottom': '0.5rem'}),
                html.P(insight['text'], style={'margin': '0', 'fontSize': '0.9rem', 'opacity': '0.9'})
            ], className="insight-card", style={'background': bg_color})
        )
    
    return html.Div(insight_cards)

# Mobile Chart Components
def create_mobile_charts():
    if processed_df.empty:
        return html.Div()
    
    # Simple bar chart for component performance
    overall_scores = calculate_overall_ppsa_breakdown(processed_df)
    
    fig_components = go.Figure()
    components = ['PSM', 'PWP', 'SG', 'APC']
    scores = [overall_scores.get(comp.lower(), 0) for comp in components]
    targets = [20, 25, 30, 25]
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
    
    fig_components.add_trace(go.Bar(
        x=components,
        y=scores,
        name='Actual Score',
        marker_color=colors,
        text=[f"{score:.1f}" for score in scores],
        textposition='outside'
    ))
    
    fig_components.add_trace(go.Scatter(
        x=components,
        y=targets,
        mode='markers',
        name='Target',
        marker=dict(size=10, color='#ef4444', symbol='diamond'),
        line=dict(color='#ef4444', width=2)
    ))
    
    fig_components.update_layout(
        template='plotly_white',
        height=300,
        showlegend=True,
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(size=10)
    )
    
    return html.Div([
        dcc.Graph(figure=fig_components, config={'displayModeBar': False})
    ])

# Main Layout Mobile
app.layout = dbc.Container([
    # Custom CSS
    html.Style(mobile_css['custom-css']),
    
    # Mobile Header
    create_mobile_header(),
    
    # Main Content Area dengan padding untuk mobile
    html.Div([
        # KPI Cards
        create_mobile_kpi_cards(),
        
        # Main Score Card
        create_main_score_card(),
        
        # Navigation Tabs
        create_mobile_nav(),
        
        # Tab Content
        html.Div(id="mobile-tab-content", style={'paddingBottom': '5rem'}),
        
    ], style={'padding': '0 0.5rem'}),
    
    # Floating Action Button
    html.Button([
        html.I(className="fas fa-sync-alt")
    ], className="floating-action-btn", id="refresh-btn"),
    
    # Hidden div untuk store data
    dcc.Store(id='data-store', data=processed_df.to_dict('records') if not processed_df.empty else {}),
    
    # Footer
    html.Footer([
        html.Hr(style={'margin': '2rem 0 1rem 0'}),
        html.Div([
            html.P([
                html.Strong("🚀 PPSA Analytics Mobile v2.1"),
                " • Powered by AI • © 2025",
                html.Br(),
                html.Small("Optimized for mobile experience • Real-time insights", 
                          style={'opacity': '0.7'})
            ], className="text-center", style={'fontSize': '0.8rem'})
        ])
    ])
], fluid=True, style={'padding': '0', 'maxWidth': '100%', 'background': '#f8f9fa'})

# --- CALLBACKS UNTUK MOBILE ---

@app.callback(
    Output("mobile-tab-content", "children"),
    [Input(f"tab-{tab}", "n_clicks") for tab in ['overview', 'performance', 'tebus', 'insights', 'team', 'analytics']],
    prevent_initial_call=True
)
def render_mobile_tab_content(overview_clicks, performance_clicks, tebus_clicks, insights_clicks, team_clicks, analytics_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return render_overview_tab()
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'tab-overview':
        return render_overview_tab()
    elif button_id == 'tab-performance':
        return render_performance_tab()
    elif button_id == 'tab-tebus':
        return render_tebus_tab()
    elif button_id == 'tab-insights':
        return render_insights_tab()
    elif button_id == 'tab-team':
        return render_team_tab()
    elif button_id == 'tab-analytics':
        return render_analytics_tab()
    
    return render_overview_tab()

def render_overview_tab():
    return html.Div([
        create_content_section("📈 Quick Overview", [
            create_team_metrics_grid(),
            html.Div(create_performance_badges(), style={'margin': '1.5rem 0'}),
            create_content_section("📊 Component Performance", [
                create_mobile_charts()
            ], "")
        ], "📈")
    ])

def render_performance_tab():
    if processed_df.empty:
        return create_content_section("🚀 Performance", [
            html.P("No performance data available", style={'textAlign': 'center', 'color': '#64748b'})
        ], "🚀")
    
    cashier_scores = calculate_aggregate_scores_per_cashier(processed_df)
    
    # Top 5 Performers
    top_performers = cashier_scores.head(5)
    
    performer_cards = []
    for idx, row in top_performers.iterrows():
        badge_class = "badge-excellent" if row['TOTAL SCORE PPSA'] >= 120 else "badge-good" if row['TOTAL SCORE PPSA'] >= 100 else "badge-average"
        badge_text = "Excellent" if row['TOTAL SCORE PPSA'] >= 120 else "Good" if row['TOTAL SCORE PPSA'] >= 100 else "Needs Improvement"
        
        performer_cards.append(
            html.Div([
                html.Div([
                    html.Div([
                        html.Strong(row['NAMA KASIR'], style={'fontSize': '0.9rem'}),
                        html.Span(badge_text, className=f"performance-badge {badge_class}")
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
                    html.Div([
                        html.Span(f"Score: {row['TOTAL SCORE PPSA']:.1f}", 
                                 style={'color': '#667eea', 'fontWeight': '600', 'fontSize': '0.8rem'}),
                        html.Span(f"Consistency: {max(0, 100 - (row.get('CONSISTENCY', 0) * 2)):.0f}%", 
                                 style={'color': '#64748b', 'fontSize': '0.7rem', 'float': 'right'})
                    ], style={'marginTop': '0.5rem'})
                ])
            ], style={'padding': '1rem', 'background': 'white', 'borderRadius': '12px', 'marginBottom': '0.75rem', 
                     'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'})
        )
    
    return html.Div([
        create_content_section("🏆 Top Performers", performer_cards, "🏆"),
        create_content_section("📈 Performance Trend", [
            html.P("Daily performance charts will be displayed here.", 
                  style={'textAlign': 'center', 'color': '#64748b', 'padding': '2rem'})
        ], "📈")
    ])

def render_tebus_tab():
    if processed_df.empty:
        return create_content_section("🛒 Tebus Analytics", [
            html.P("No tebus data available", style={'textAlign': 'center', 'color': '#64748b'})
        ], "🛒")
    
    # Tebus performance summary
    tebus_summary = processed_df.groupby('NAMA KASIR').agg({
        'TARGET TEBUS 2500': 'sum',
        'ACTUAL TEBUS 2500': 'sum'
    }).reset_index()
    
    tebus_summary['ACV TEBUS (%)'] = (tebus_summary['ACTUAL TEBUS 2500'] / tebus_summary['TARGET TEBUS 2500'] * 100).fillna(0)
    tebus_summary = tebus_summary.sort_values('ACV TEBUS (%)', ascending=False)
    
    tebus_cards = []
    for idx, row in tebus_summary.head(5).iterrows():
        achievement_color = '#10b981' if row['ACV TEBUS (%)'] >= 100 else '#f59e0b' if row['ACV TEBUS (%)'] >= 80 else '#ef4444'
        
        tebus_cards.append(
            html.Div([
                html.Div([
                    html.Strong(row['NAMA KASIR'], style={'fontSize': '0.9rem'}),
                    html.Span(f"{row['ACV TEBUS (%)']:.1f}%", 
                             style={'color': achievement_color, 'fontWeight': '700', 'float': 'right'})
                ]),
                html.Div([
                    html.Small(f"Actual: {row['ACTUAL TEBUS 2500']} | Target: {row['TARGET TEBUS 2500']}", 
                              style={'color': '#64748b', 'fontSize': '0.7rem'})
                ], style={'marginTop': '0.25rem'})
            ], style={'padding': '1rem', 'background': 'white', 'borderRadius': '12px', 'marginBottom': '0.75rem',
                     'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'})
        )
    
    return html.Div([
        create_content_section("🎯 Tebus Performance", tebus_cards, "🎯"),
        create_content_section("📊 Tebus Analytics", [
            html.P("Detailed tebus analytics charts will be displayed here.", 
                  style={'textAlign': 'center', 'color': '#64748b', 'padding': '2rem'})
        ], "📊")
    ])

def render_insights_tab():
    return html.Div([
        create_content_section("🤖 AI-Powered Insights", [
            create_ai_insights()
        ], "🤖"),
        create_content_section("💡 Recommendations", [
            html.Div([
                html.H5("🎯 Action Items", style={'fontWeight': '700', 'marginBottom': '1rem'}),
                html.Ul([
                    html.Li("Focus on improving APC component scores"),
                    html.Li("Schedule training for underperforming team members"),
                    html.Li("Optimize shift scheduling based on performance patterns"),
                    html.Li("Implement weekly performance reviews")
                ], style={'color': '#64748b', 'fontSize': '0.9rem'})
            ])
        ], "💡")
    ])

def render_team_tab():
    if processed_df.empty or 'NAMA KASIR' not in processed_df.columns:
        return create_content_section("👥 Team Management", [
            html.P("No team data available", style={'textAlign': 'center', 'color': '#64748b'})
        ], "👥")
    
    cashier_scores = calculate_aggregate_scores_per_cashier(processed_df)
    
    team_table = dash_table.DataTable(
        data=cashier_scores.to_dict('records'),
        columns=[
            {"name": "Kasir", "id": "NAMA KASIR"},
            {"name": "Score", "id": "TOTAL SCORE PPSA", "type": "numeric", "format": {"specifier": ".1f"}},
            {"name": "PSM", "id": "SCORE PSM", "type": "numeric", "format": {"specifier": ".1f"}},
            {"name": "PWP", "id": "SCORE PWP", "type": "numeric", "format": {"specifier": ".1f"}},
        ],
        style_cell={
            'textAlign': 'left',
            'padding': '8px',
            'fontSize': '12px',
            'fontFamily': 'Inter, sans-serif'
        },
        style_header={
            'backgroundColor': '#667eea',
            'color': 'white',
            'fontWeight': '700',
            'fontSize': '11px'
        },
        style_data={
            'backgroundColor': 'white',
            'color': 'black'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
    
    return html.Div([
        create_content_section("📋 Team Performance", [
            team_table
        ], "📋")
    ])

def render_analytics_tab():
    return html.Div([
        create_content_section("📈 Advanced Analytics", [
            html.Div([
                html.P("Advanced analytics features:", style={'marginBottom': '1rem'}),
                html.Ul([
                    html.Li("Performance correlation analysis"),
                    html.Li("Trend forecasting"),
                    html.Li("Anomaly detection"),
                    html.Li("Predictive insights")
                ], style={'color': '#64748b', 'fontSize': '0.9rem'})
            ])
        ], "📈"),
        create_content_section("🔧 Data Tools", [
            html.Div([
                dbc.Button("Export Report", color="primary", className="me-2", size="sm"),
                dbc.Button("Refresh Data", color="secondary", size="sm"),
            ], className="d-grid gap-2")
        ], "🔧")
    ])

@app.callback(
    Output("data-store", "data"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    if n_clicks:
        try:
            raw_df = load_data_from_gsheet()
            if not raw_df.empty:
                processed_df = process_data(raw_df.copy())
                return processed_df.to_dict('records')
        except Exception as e:
            print(f"Error refreshing data: {e}")
    
    return processed_df.to_dict('records') if not processed_df.empty else {}

# --- RUN APP ---
server = app.server

if __name__ == '__main__':
    print("🚀 Starting PPSA Analytics Mobile Dashboard...")
    print(f"📊 Data ready: {len(processed_df)} records")
    print(f"📱 Mobile-optimized layout activated")
    
    app.run_server(debug=False, host='0.0.0.0', port=8050)
