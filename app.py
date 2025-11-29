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
        {"name": "theme-color", "content": "#667eea"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"}
    ]
)

app.title = "🚀 PPSA Analytics Dashboard"

# CSS Custom untuk Mobile
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
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
                margin: 0;
                padding: 0;
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
            
            @media (max-width: 768px) {
                .container-fluid {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- FUNGSI DATA YANG DIPERBAIKI ---

def load_data_from_gsheet():
    """Load data from Google Sheets dengan error handling yang lebih baik"""
    try:
        # Untuk deployment, gunakan environment variable
        SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
        
        if not SPREADSHEET_ID:
            print("❌ SPREADSHEET_ID environment variable is not set.")
            return create_sample_data()
        
        # Untuk development, bisa menggunakan service account
        if os.path.exists('service_account.json'):
            creds = Credentials.from_service_account_file('service_account.json')
        else:
            # Fallback untuk Render deployment
            service_account_info = {
                "type": "service_account",
                "project_id": os.environ.get('GCP_PROJECT_ID', 'default-project'),
                "private_key_id": os.environ.get('GCP_PRIVATE_KEY_ID', ''),
                "private_key": os.environ.get('GCP_PRIVATE_KEY', '').replace('\\n', '\n'),
                "client_email": os.environ.get('GCP_CLIENT_EMAIL', ''),
                "client_id": os.environ.get('GCP_CLIENT_ID', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
            creds = Credentials.from_service_account_info(service_account_info)
        
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 
                 'https://www.googleapis.com/auth/drive']
        creds = creds.with_scopes(scopes)
        client = gspread.authorize(creds)
        
        # Open spreadsheet by ID
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.get_worksheet(0)  # First worksheet
        
        data = worksheet.get_all_values()
        
        if not data or len(data) <= 1:
            print("⚠️ No data or only headers found in worksheet")
            return create_sample_data()
            
        df = pd.DataFrame(data[1:], columns=data[0])
        print(f"✅ Data loaded successfully: {len(df)} records")
        return df
        
    except Exception as e:
        print(f"❌ Gagal mengambil data dari Google Sheets: {str(e)}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for testing when no real data is available"""
    print("📝 Creating sample data for demonstration...")
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
    sample_data = []
    
    kasir_names = ['Budi Santoso', 'Siti Rahayu', 'Ahmad Wijaya', 'Dewi Lestari', 'Joko Prasetyo']
    shifts = ['1', '2', '3']
    
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
                    'APC Target': round(np.random.uniform(0.8, 1.2), 2),
                    'APC Actual': round(np.random.uniform(0.7, 1.3), 2),
                    'BOBOT APC': 25,
                    'TARGET TEBUS 2500': np.random.randint(8, 12),
                    'ACTUAL TEBUS 2500': np.random.randint(6, 14)
                })
    
    df = pd.DataFrame(sample_data)
    print("💾 Sample data created successfully")
    return df

def normalize_column_names(df):
    """Normalize column names to handle various formats"""
    if df.empty:
        return df
    
    column_mapping = {
        'tanggal': 'TANGGAL', 'date': 'TANGGAL', 'tgl': 'TANGGAL',
        'nama kasir': 'NAMA KASIR', 'kasir': 'NAMA KASIR', 'name': 'NAMA KASIR',
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

def process_data(df):
    """Process data dengan validasi dan cleaning yang lebih robust"""
    if df.empty:
        print("⚠️ No data to process")
        return df
    
    df = normalize_column_names(df)
    print(f"📊 Columns after normalization: {list(df.columns)}")
    
    if 'TANGGAL' in df.columns:
        print("📅 Processing dates...")
        df['TANGGAL'] = pd.to_datetime(df['TANGGAL'], format='%d/%m/%Y', errors='coerce')
        
        valid_dates = df['TANGGAL'].notna()
        df.loc[valid_dates, 'HARI'] = df.loc[valid_dates, 'TANGGAL'].dt.day_name()
        
        hari_map = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        df['HARI'] = df['HARI'].map(hari_map)
    
    if 'SHIFT' in df.columns:
        print("🕐 Processing shifts...")
        df['SHIFT'] = df['SHIFT'].astype(str).str.strip()
        shift_mapping = {
            '1': 'Shift 1 (Pagi)', '2': 'Shift 2 (Siang)', '3': 'Shift 3 (Malam)'
        }
        df['SHIFT'] = df['SHIFT'].map(shift_mapping)
        df['SHIFT'] = df['SHIFT'].fillna('Unknown')
    
    numeric_cols = [
        'PSM Target', 'PSM Actual', 'BOBOT PSM',
        'PWP Target', 'PWP Actual', 'BOBOT PWP',
        'SG Target', 'SG Actual', 'BOBOT SG',
        'APC Target', 'APC Actual', 'BOBOT APC',
        'TARGET TEBUS 2500', 'ACTUAL TEBUS 2500'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

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
    
    print(f"✅ Data processing completed: {len(df)} valid records")
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
        
        if 'APC Target' in df.columns and 'APC Actual' in df.columns:
            avg_target_apc = df['APC Target'].mean()
            avg_actual_apc = df['APC Actual'].mean()
            if avg_target_apc > 0:
                acv_apc = (avg_actual_apc / avg_target_apc) * 100
                scores['apc'] = (acv_apc * weights['APC']) / 100
        
        scores['total'] = sum(scores.values())
        
    except Exception as e:
        print(f"❌ Error calculating overall PPSA: {e}")
    
    return scores

# Load and process data
try:
    raw_df = load_data_from_gsheet()
    processed_df = process_data(raw_df.copy()) if not raw_df.empty else pd.DataFrame()
except Exception as e:
    print(f"❌ Error in data processing: {e}")
    processed_df = create_sample_data()
    processed_df = process_data(processed_df)

print(f"🎯 Final data status: {len(processed_df)} records loaded")

# --- SIMPLIFIED LAYOUT FOR DEPLOYMENT ---

def create_mobile_header():
    data_status = "✅ Data Loaded" if not processed_df.empty else "❌ No Data"
    data_count = f" ({len(processed_df)} records)" if not processed_df.empty else ""
    
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
                ], className="mb-2"),
            ], className="text-center")
        ], className="mobile-header"),
    ])

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

def create_simple_dashboard():
    """Create a simplified dashboard for deployment"""
    return html.Div([
        create_mobile_header(),
        create_mobile_kpi_cards(),
        create_main_score_card(),
        
        html.Div([
            html.H4("📊 Quick Stats", style={'fontWeight': '700', 'marginBottom': '1rem'}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Small("TEAM MEMBERS", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                        html.H5(f"{processed_df['NAMA KASIR'].nunique() if 'NAMA KASIR' in processed_df.columns else 0}", 
                               style={'fontWeight': '700', 'margin': '0'})
                    ], className="text-center stat-item")
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.Small("ACHIEVEMENT RATE", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                        html.H5(f"{(len(processed_df[processed_df['TOTAL SCORE PPSA'] >= 100])/len(processed_df)*100 if len(processed_df) > 0 else 0):.0f}%", 
                               style={'fontWeight': '700', 'margin': '0'})
                    ], className="text-center stat-item")
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Small("AVG SCORE", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                        html.H5(f"{processed_df['TOTAL SCORE PPSA'].mean() if not processed_df.empty else 0:.1f}", 
                               style={'fontWeight': '700', 'margin': '0'})
                    ], className="text-center stat-item")
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.Small("DATA RECORDS", style={'fontSize': '0.7rem', 'opacity': '0.8'}),
                        html.H5(f"{len(processed_df)}", 
                               style={'fontWeight': '700', 'margin': '0'})
                    ], className="text-center stat-item")
                ], width=6),
            ])
        ], className="content-section"),
        
        html.Div([
            html.H4("🚀 Performance Overview", style={'fontWeight': '700', 'marginBottom': '1rem'}),
            dcc.Graph(
                figure=create_performance_chart(),
                config={'displayModeBar': False}
            )
        ], className="content-section"),
        
        html.Div([
            html.H4("🔧 Configuration", style={'fontWeight': '700', 'marginBottom': '1rem'}),
            html.P(f"Data Source: {'Google Sheets' if os.environ.get('SPREADSHEET_ID') else 'Sample Data'}"),
            html.P(f"Records Processed: {len(processed_df)}"),
            dbc.Button("Refresh Data", color="primary", id="refresh-btn", className="w-100")
        ], className="content-section"),
        
        html.Footer([
            html.Hr(style={'margin': '2rem 0 1rem 0'}),
            html.P([
                html.Strong("🚀 PPSA Analytics Mobile v2.1"),
                " • Powered by Dash • © 2025",
                html.Br(),
                html.Small("Optimized for mobile experience", style={'opacity': '0.7'})
            ], className="text-center", style={'fontSize': '0.8rem'})
        ])
    ], style={'padding': '0 0.5rem 2rem 0.5rem'})

def create_performance_chart():
    """Create a simple performance chart"""
    if processed_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    overall_scores = calculate_overall_ppsa_breakdown(processed_df)
    
    fig = go.Figure()
    components = ['PSM', 'PWP', 'SG', 'APC']
    scores = [overall_scores.get(comp.lower(), 0) for comp in components]
    targets = [20, 25, 30, 25]
    
    fig.add_trace(go.Bar(
        x=components,
        y=scores,
        name='Actual Score',
        marker_color=['#667eea', '#764ba2', '#f093fb', '#4facfe']
    ))
    
    fig.add_trace(go.Scatter(
        x=components,
        y=targets,
        mode='markers',
        name='Target',
        marker=dict(size=10, color='#ef4444', symbol='diamond')
    ))
    
    fig.update_layout(
        template='plotly_white',
        height=300,
        showlegend=True,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

# Main Layout
app.layout = create_simple_dashboard()

@app.callback(
    Output("refresh-btn", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    if n_clicks:
        try:
            global processed_df
            raw_df = load_data_from_gsheet()
            processed_df = process_data(raw_df.copy()) if not raw_df.empty else pd.DataFrame()
            return "Data Refreshed!"
        except Exception as e:
            return f"Error: {str(e)}"
    return "Refresh Data"

# Server configuration for Render
server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
