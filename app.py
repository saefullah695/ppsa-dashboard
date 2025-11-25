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

# --- KONFIGURASI DATA ---
def load_data_from_gsheet():
    """Load data from Google Sheets dengan error handling"""
    try:
        # Untuk deployment di Render, gunakan environment variable
        service_account_info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT'))
        SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
        WORKSHEET_NAME = os.environ.get('WORKSHEET_NAME', 'Sheet1')  # Default ke 'Sheet1'
        
        if not SPREADSHEET_ID:
            print("❌ SPREADSHEET_ID environment variable is not set.")
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
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data[1:], columns=data[0])
        print(f"✅ Data loaded successfully: {len(df)} records")
        return df
    except Exception as e:
        print(f"❌ Gagal mengambil data: {str(e)}")
        return pd.DataFrame()

def process_data(df):
    """Process data dengan validasi dan cleaning"""
    if df.empty:
        return df
    
    # Process dates
    if 'TANGGAL' in df.columns:
        df['TANGGAL'] = pd.to_datetime(df['TANGGAL'], format='%d/%m/%Y', errors='coerce')
        df['HARI'] = df['TANGGAL'].dt.day_name()
        df['BULAN'] = df['TANGGAL'].dt.month_name()
        df['MINGGU'] = df['TANGGAL'].dt.isocalendar().week
        
        hari_map = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        df['HARI'] = df['HARI'].map(hari_map)
    
    # Process shift column
    if 'SHIFT' in df.columns:
        df['SHIFT'] = df['SHIFT'].astype(str)
        shift_map = {
            '1': 'Shift 1 (Pagi)',
            '2': 'Shift 2 (Siang)',
            '3': 'Shift 3 (Malam)'
        }
        df['SHIFT'] = df['SHIFT'].map(shift_map)
        df['SHIFT'] = df['SHIFT'].fillna('Unknown')
    
    # Process numeric columns
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

    # Calculate ACV (Achievement vs Target)
    def calculate_acv(actual, target):
        return (actual / target * 100) if target != 0 else 0.0

    df['(%) PSM ACV'] = df.apply(lambda row: calculate_acv(row['PSM Actual'], row['PSM Target']), axis=1)
    df['(%) PWP ACV'] = df.apply(lambda row: calculate_acv(row['PWP Actual'], row['PWP Target']), axis=1)
    df['(%) SG ACV'] = df.apply(lambda row: calculate_acv(row['SG Actual'], row['SG Target']), axis=1)
    df['(%) APC ACV'] = df.apply(lambda row: calculate_acv(row['APC Actual'], row['APC Target']), axis=1)
    df['(%) ACV TEBUS 2500'] = df.apply(lambda row: calculate_acv(row['ACTUAL TEBUS 2500'], row['TARGET TEBUS 2500']), axis=1)

    # Calculate weighted scores
    df['SCORE PSM'] = (df['(%) PSM ACV'] * df['BOBOT PSM']) / 100
    df['SCORE PWP'] = (df['(%) PWP ACV'] * df['BOBOT PWP']) / 100
    df['SCORE SG'] = (df['(%) SG ACV'] * df['BOBOT SG']) / 100
    df['SCORE APC'] = (df['(%) APC ACV'] * df['BOBOT APC']) / 100

    # Calculate total PPSA score
    score_cols = ['SCORE PSM', 'SCORE PWP', 'SCORE SG', 'SCORE APC']
    df['TOTAL SCORE PPSA'] = df[score_cols].sum(axis=1)
    
    # Remove rows with NaN in critical columns
    df = df.dropna(subset=['SHIFT', 'TOTAL SCORE PPSA'])
    
    return df

def calculate_overall_ppsa_breakdown(df):
    """Calculate overall PPSA breakdown"""
    if df.empty:
        return {'total': 0.0, 'psm': 0.0, 'pwp': 0.0, 'sg': 0.0, 'apc': 0.0}
    
    weights = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}
    scores = {'psm': 0.0, 'pwp': 0.0, 'sg': 0.0, 'apc': 0.0}
    
    # For PSM, PWP, SG - use SUM aggregation
    for comp in ['PSM', 'PWP', 'SG']:
        total_target = df[f'{comp} Target'].sum()
        total_actual = df[f'{comp} Actual'].sum()
        if total_target > 0:
            acv = (total_actual / total_target) * 100
            scores[comp.lower()] = (acv * weights[comp]) / 100
    
    # For APC - use AVERAGE aggregation
    avg_target_apc = df['APC Target'].mean()
    avg_actual_apc = df['APC Actual'].mean()
    if avg_target_apc > 0:
        acv_apc = (avg_actual_apc / avg_target_apc) * 100
        scores['apc'] = (acv_apc * weights['APC']) / 100
    
    scores['total'] = sum(scores.values())
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

# Load data dengan error handling
try:
    raw_df = load_data_from_gsheet()
    processed_df = process_data(raw_df.copy()) if not raw_df.empty else pd.DataFrame()
except Exception as e:
    print(f"Error loading data: {e}")
    raw_df = pd.DataFrame()
    processed_df = pd.DataFrame()

# --- LAYOUT DASHBOARD ---

# Header dengan status data loading
def create_header():
    data_status = "✅ Data Loaded" if not processed_df.empty else "❌ No Data Available"
    data_count = f" ({len(processed_df)} records)" if not processed_df.empty else ""
    
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
                    html.Span(f"Spreadsheet: {os.environ.get('SPREADSHEET_ID', 'Not set')[:20]}...", 
                             style={'color': '#64748b', 'fontSize': '0.9rem'}),
                    html.Span(" | ", className="mx-2"),
                    html.Span(f"Worksheet: {os.environ.get('WORKSHEET_NAME', 'Sheet1')}", 
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

header = create_header()

# KPI Cards
def create_kpi_card(title, value, color, icon):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Span(icon, className="me-2"),
                html.Span(title, style={'fontSize': '0.9rem', 'fontWeight': '700', 'textTransform': 'uppercase'})
            ], className="d-flex align-items-center mb-2"),
            html.H3(f"{value:.1f}", style={'color': color, 'fontWeight': '800', 'fontSize': '2.5rem', 'margin': '0'})
        ]),
        className="m-2 shadow",
        style={'borderRadius': '12px', 'borderLeft': f'4px solid {color}'}
    )

# Overall PPSA Score Card
overall_scores = calculate_overall_ppsa_breakdown(processed_df) if not processed_df.empty else {'total': 0.0}
gap_value = overall_scores['total'] - 100
gap_color = '#10b981' if gap_value >= 0 else '#ef4444'

total_score_card = dbc.Card(
    dbc.CardBody([
        html.Div([
            html.Span("🏆 TOTAL PPSA SCORE", 
                     style={'fontSize': '1.1rem', 'fontWeight': '700', 'textTransform': 'uppercase',
                           'color': 'rgba(255,255,255,0.95)'}),
        ], className="text-center mb-3"),
        html.H2(f"{overall_scores['total']:.1f}", 
               className="text-center",
               style={'color': '#ffffff', 'fontWeight': '900', 'fontSize': '4rem', 'textShadow': '0 4px 20px rgba(0,0,0,0.3)'}),
        html.Div([
            html.Span(f"Gap: {gap_value:+.1f}", 
                     style={'color': '#90EE90' if gap_value >= 0 else '#FFB6C1', 'fontSize': '1.2rem'})
        ], className="text-center mt-2")
    ]),
    className="m-2 shadow",
    style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
           'borderRadius': '20px', 'color': 'white', 'textAlign': 'center'}
)

# Tabs
tabs = dbc.Tabs([
    dbc.Tab(label="📈 PPSA Analytics", tab_id="tab-1"),
    dbc.Tab(label="🛒 Tebus Analytics", tab_id="tab-2"),
    dbc.Tab(label="🔍 Deep Insights", tab_id="tab-3"),
    dbc.Tab(label="🎯 Performance Alerts", tab_id="tab-4"),
    dbc.Tab(label="🕐 Performance Shift", tab_id="tab-5"),
    dbc.Tab(label="📅 Performance Per Hari", tab_id="tab-6"),
    dbc.Tab(label="🔧 Config Debug", tab_id="tab-7"),
], id="tabs", active_tab="tab-1")

# Content containers
def create_content_container(children, title=None):
    if title:
        children = [html.H2(title, className="section-header mb-4")] + children
    
    return dbc.Card(
        dbc.CardBody(children),
        className="mb-4 shadow",
        style={'background': 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%)',
               'borderRadius': '20px', 'border': '1px solid rgba(255, 255, 255, 0.3)'}
    )

# Main Layout
app.layout = dbc.Container([
    # Header
    header,
    
    # KPI Row
    dbc.Row([
        dbc.Col(create_kpi_card("PSM Score", 
                               overall_scores.get('psm', 0), 
                               '#667eea', '📊'), width=3),
        dbc.Col(create_kpi_card("PWP Score", 
                               overall_scores.get('pwp', 0), 
                               '#764ba2', '🛒'), width=3),
        dbc.Col(create_kpi_card("SG Score", 
                               overall_scores.get('sg', 0), 
                               '#f093fb', '🛡️'), width=3),
        dbc.Col(create_kpi_card("APC Score", 
                               overall_scores.get('apc', 0), 
                               '#4facfe', '⚡'), width=3),
    ], className="mb-4"),
    
    # Total Score Card (Centered)
    dbc.Row([
        dbc.Col(total_score_card, width=8, className="mx-auto")
    ], className="mb-4"),
    
    # Tabs
    tabs,
    
    # Tab Content
    html.Div(id="tab-content"),
    
    # Footer
    html.Footer([
        html.Hr(),
        html.P([
            html.Strong("🚀 PPSA Analytics Dashboard v2.0"),
            " • Powered by Dash & AI • © 2025",
            html.Br(),
            html.Small("Advanced Analytics • Real-time Monitoring • Performance Optimization", 
                      style={'opacity': '0.7'})
        ], className="text-center text-muted mt-4")
    ])
], fluid=True, className="py-4")

# --- CALLBACKS ---
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "tab-1":
        return render_ppsa_analytics()
    elif active_tab == "tab-2":
        return render_tebus_analytics()
    elif active_tab == "tab-3":
        return render_deep_insights()
    elif active_tab == "tab-4":
        return render_performance_alerts()
    elif active_tab == "tab-5":
        return render_shift_performance()
    elif active_tab == "tab-6":
        return render_daily_performance()
    elif active_tab == "tab-7":
        return render_config_debug()
    return html.Div("Select a tab")

def render_ppsa_analytics():
    if processed_df.empty:
        return create_content_container("PPSA Analytics", [
            dbc.Alert([
                html.H4("❌ Data Tidak Tersedia", className="alert-heading"),
                html.P("Tidak dapat memuat data dari Google Sheets. Periksa konfigurasi environment variables:"),
                html.Ul([
                    html.Li("GCP_SERVICE_ACCOUNT"),
                    html.Li("SPREADSHEET_ID"), 
                    html.Li("WORKSHEET_NAME (opsional)")
                ]),
                html.Hr(),
                html.P("Pastikan SPREADSHEET_ID benar dan service account memiliki akses.", 
                      className="mb-0")
            ], color="danger")
        ])
    
    # Team Performance Metrics
    cashier_scores = calculate_aggregate_scores_per_cashier(processed_df)
    
    # Charts
    overall_scores = calculate_overall_ppsa_breakdown(processed_df)
    
    # Component vs Target Chart
    chart_data = pd.DataFrame({
        'Komponen': ['PSM', 'PWP', 'SG', 'APC'],
        'Actual': [overall_scores['psm'], overall_scores['pwp'], overall_scores['sg'], overall_scores['apc']],
        'Target': [20, 25, 30, 25]
    })
    
    fig_vs_target = go.Figure()
    fig_vs_target.add_trace(go.Bar(
        name='Actual Score',
        x=chart_data['Komponen'],
        y=chart_data['Actual'],
        marker_color=['#667eea', '#764ba2', '#f093fb', '#4facfe'],
        text=[f"{val:.1f}" for val in chart_data['Actual']],
        textposition='outside'
    ))
    fig_vs_target.add_trace(go.Scatter(
        name='Target',
        x=chart_data['Komponen'],
        y=chart_data['Target'],
        mode='markers+lines',
        marker=dict(size=15, color='#ef4444', symbol='diamond'),
        line=dict(color='#ef4444', width=3, dash='dash')
    ))
    fig_vs_target.update_layout(
        template='plotly_white',
        height=350,
        showlegend=True,
        yaxis_title='Score',
        title_x=0.5
    )
    
    # Performance Distribution
    fig_dist = go.Figure()
    if not cashier_scores.empty:
        fig_dist.add_trace(go.Histogram(
            x=cashier_scores['TOTAL SCORE PPSA'],
            nbinsx=15,
            marker_color='rgba(102, 126, 234, 0.7)',
            name='Distribution'
        ))
        fig_dist.add_vline(
            x=100, 
            line_dash="dash", 
            line_color="red",
            annotation_text="Target (100)"
        )
        fig_dist.update_layout(
            template='plotly_white',
            height=350,
            xaxis_title='Total PPSA Score',
            yaxis_title='Frequency',
            showlegend=False
        )
    
    return create_content_container("PPSA Analytics", [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_vs_target), width=6),
            dbc.Col(dcc.Graph(figure=fig_dist), width=6)
        ]),
        
        # Top Performers
        html.H3("🏅 Top Performers", className="mt-4 mb-3"),
        render_top_performers(cashier_scores),
        
        # Performance Table
        html.H3("📋 Detailed Performance", className="mt-4 mb-3"),
        render_performance_table(cashier_scores)
    ])

def render_tebus_analytics():
    if processed_df.empty:
        return create_content_container("Tebus Analytics", [
            dbc.Alert([
                html.H4("❌ Data Tidak Tersedia", className="alert-heading"),
                html.P("Tidak dapat memuat data dari Google Sheets."),
            ], color="danger")
        ])
    
    # Tebus calculations
    tebus_summary = processed_df.groupby('NAMA KASIR').agg({
        'TARGET TEBUS 2500': 'sum',
        'ACTUAL TEBUS 2500': 'sum'
    }).reset_index()
    
    tebus_summary['ACV TEBUS (%)'] = (tebus_summary['ACTUAL TEBUS 2500'] / tebus_summary['TARGET TEBUS 2500'] * 100).fillna(0)
    tebus_summary = tebus_summary.sort_values('ACV TEBUS (%)', ascending=False)
    
    # Tebus Performance Chart
    fig_tebus = go.Figure()
    colors = ['#10b981' if acv >= 100 else '#f59e0b' if acv >= 80 else '#ef4444' 
             for acv in tebus_summary['ACV TEBUS (%)']]
    
    fig_tebus.add_trace(go.Bar(
        y=tebus_summary['NAMA KASIR'],
        x=tebus_summary['ACV TEBUS (%)'],
        orientation='h',
        marker_color=colors,
        text=[f"{acv:.1f}%" for acv in tebus_summary['ACV TEBUS (%)']],
        textposition='outside'
    ))
    
    fig_tebus.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="Target 100%")
    fig_tebus.update_layout(
        template='plotly_white',
        height=max(400, len(tebus_summary) * 35),
        showlegend=False,
        xaxis_title='Achievement (%)',
        yaxis={'categoryorder': 'total ascending'},
        title="Tebus Performance by Cashier"
    )
    
    return create_content_container("Tebus Analytics", [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_tebus), width=12)
        ])
    ])

def render_deep_insights():
    if processed_df.empty:
        return create_content_container("Deep Insights", [
            dbc.Alert([
                html.H4("❌ Data Tidak Tersedia", className="alert-heading"),
                html.P("Tidak dapat memuat data dari Google Sheets."),
            ], color="danger")
        ])
    
    # Correlation Matrix
    score_cols = ['SCORE PSM', 'SCORE PWP', 'SCORE SG', 'SCORE APC', 'TOTAL SCORE PPSA']
    available_cols = [col for col in score_cols if col in processed_df.columns]
    
    if len(available_cols) >= 2:
        corr_matrix = processed_df[available_cols].corr()
        
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdYlBu',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        
        fig_corr.update_layout(
            template='plotly_white',
            height=400,
            title="Correlation Matrix - PPSA Components"
        )
        
        return create_content_container("Deep Insights", [
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_corr), width=12)
            ])
        ])
    
    return create_content_container("Deep Insights", [
        html.Div("Insufficient data for correlation analysis", className="text-center text-muted")
    ])

def render_performance_alerts():
    if processed_df.empty:
        return create_content_container("Performance Alerts", [
            dbc.Alert([
                html.H4("❌ Data Tidak Tersedia", className="alert-heading"),
                html.P("Tidak dapat memuat data dari Google Sheets."),
            ], color="danger")
        ])
    
    cashier_scores = calculate_aggregate_scores_per_cashier(processed_df)
    alerts = []
    
    # Critical performers
    critical_performers = cashier_scores[cashier_scores['TOTAL SCORE PPSA'] < 80]
    if not critical_performers.empty:
        alerts.append(dbc.Alert([
            html.H4("🚨 Critical Performance Alert", className="alert-heading"),
            html.P(f"{len(critical_performers)} kasir dengan performa < 80 poin"),
            html.Hr(),
            html.P("Immediate coaching dan performance improvement plan diperlukan", 
                  className="mb-0")
        ], color="danger"))
    
    # Component alerts
    overall_scores = calculate_overall_ppsa_breakdown(processed_df)
    for comp, score in [('PSM', overall_scores['psm']), ('PWP', overall_scores['pwp']), 
                       ('SG', overall_scores['sg']), ('APC', overall_scores['apc'])]:
        target = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}[comp]
        if score < target * 0.8:
            alerts.append(dbc.Alert([
                html.H4(f"⚠️ {comp} Component Alert", className="alert-heading"),
                html.P(f"{comp} score ({score:.1f}) significantly below target ({target})"),
                html.Hr(),
                html.P(f"Focus training pada {comp} component untuk semua kasir", 
                      className="mb-0")
            ], color="warning"))
    
    if not alerts:
        alerts.append(dbc.Alert([
            html.H4("✅ No Critical Alerts", className="alert-heading"),
            html.P("All systems operating within normal parameters!")
        ], color="success"))
    
    return create_content_container("Performance Alerts", alerts)

def render_shift_performance():
    if processed_df.empty or 'SHIFT' not in processed_df.columns:
        return create_content_container("Shift Performance", [
            dbc.Alert([
                html.H4("❌ Data Tidak Tersedia", className="alert-heading"),
                html.P("Tidak dapat memuat data shift dari Google Sheets."),
            ], color="danger")
        ])
    
    # Simplified shift performance calculation
    shift_performance = processed_df.groupby('SHIFT').agg({
        'TOTAL SCORE PPSA': ['mean', 'median', 'std', 'count']
    }).reset_index()
    
    shift_performance.columns = ['SHIFT', 'Avg_Score', 'Median_Score', 'Std_Dev', 'Count']
    
    fig_shift = go.Figure()
    fig_shift.add_trace(go.Bar(
        x=shift_performance['SHIFT'],
        y=shift_performance['Avg_Score'],
        name='Average Score',
        marker_color=['#667eea', '#764ba2', '#f093fb'][:len(shift_performance)],
        text=[f"{score:.1f}" for score in shift_performance['Avg_Score']],
        textposition='outside'
    ))
    
    fig_shift.add_trace(go.Scatter(
        x=shift_performance['SHIFT'],
        y=shift_performance['Median_Score'],
        mode='markers+lines',
        name='Median Score',
        marker=dict(size=10, color='#ef4444'),
        line=dict(color='#ef4444', width=2)
    ))
    
    fig_shift.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target (100)")
    fig_shift.update_layout(
        template='plotly_white',
        height=400,
        showlegend=True,
        yaxis_title='Score',
        xaxis_title='Shift',
        title="Performance Comparison by Shift"
    )
    
    return create_content_container("Shift Performance", [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_shift), width=12)
        ])
    ])

def render_daily_performance():
    if processed_df.empty or 'TANGGAL' not in processed_df.columns:
        return create_content_container("Daily Performance", [
            dbc.Alert([
                html.H4("❌ Data Tidak Tersedia", className="alert-heading"),
                html.P("Tidak dapat memuat data harian dari Google Sheets."),
            ], color="danger")
        ])
    
    daily_performance = processed_df.groupby('TANGGAL').agg({
        'TOTAL SCORE PPSA': ['mean', 'median', 'std', 'count']
    }).reset_index()
    
    daily_performance.columns = ['TANGGAL', 'Avg_Score', 'Median_Score', 'Std_Dev', 'Count']
    daily_performance = daily_performance.sort_values('TANGGAL')
    
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=daily_performance['TANGGAL'],
        y=daily_performance['Avg_Score'],
        mode='lines+markers',
        name='Average Score',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    
    fig_daily.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target (100)")
    fig_daily.update_layout(
        template='plotly_white',
        height=400,
        showlegend=True,
        yaxis_title='Score',
        xaxis_title='Date',
        title="Daily Performance Trend"
    )
    
    return create_content_container("Daily Performance", [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_daily), width=12)
        ])
    ])

def render_config_debug():
    """Debug configuration untuk development"""
    config_info = {
        "SPREADSHEET_ID": os.environ.get('SPREADSHEET_ID', 'Not set'),
        "WORKSHEET_NAME": os.environ.get('WORKSHEET_NAME', 'Sheet1 (default)'),
        "DATA_LOADED": not processed_df.empty,
        "RECORD_COUNT": len(processed_df),
        "COLUMNS": list(processed_df.columns) if not processed_df.empty else []
    }
    
    return create_content_container("🔧 Configuration Debug", [
        html.H4("Environment Variables", className="mb-3"),
        dash_table.DataTable(
            data=[{"Variable": k, "Value": str(v)} for k, v in config_info.items()],
            columns=[{"name": "Variable", "id": "Variable"}, {"name": "Value", "id": "Value"}],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
        ),
        html.Hr(),
        html.H4("Data Preview", className="mt-4 mb-3"),
        html.P("5 record pertama:" if not processed_df.empty else "No data available"),
        dash_table.DataTable(
            data=processed_df.head().to_dict('records') if not processed_df.empty else [],
            columns=[{"name": i, "id": i} for i in processed_df.columns] if not processed_df.empty else [],
            page_size=5,
            style_cell={
                'textAlign': 'left',
                'padding': '5px',
                'fontSize': '12px',
                'maxWidth': '150px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
        )
    ])

def render_top_performers(cashier_scores):
    if cashier_scores.empty or len(cashier_scores) < 3:
        return html.Div("Insufficient data for top performers", className="text-center text-muted")
    
    top3 = cashier_scores.head(3)
    cards = []
    
    for i, (idx, row) in enumerate(top3.iterrows()):
        medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
        medal_icons = ["🥇", "🥈", "🥉"]
        
        card = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H2(medal_icons[i], className="text-center mb-3"),
                    html.H4(row['NAMA KASIR'], className="text-center mb-2"),
                    html.H3(f"{row['TOTAL SCORE PPSA']:.1f}", 
                           className="text-center",
                           style={'color': '#667eea', 'fontWeight': '800'}),
                    html.P([
                        f"Consistency: {max(0, 100 - (row.get('CONSISTENCY', 0) * 2)):.0f}%",
                        html.Br(),
                        f"Records: {row.get('RECORD_COUNT', 'N/A')}"
                    ], className="text-center text-muted mt-2")
                ])
            ])
        ], className="h-100 text-center shadow",
           style={'borderTop': f'4px solid {medal_colors[i]}', 'borderRadius': '12px'})
        
        cards.append(dbc.Col(card, width=4))
    
    return dbc.Row(cards, className="g-3")

def render_performance_table(cashier_scores):
    if cashier_scores.empty:
        return html.Div("No performance data available", className="text-center text-muted")
    
    # Add performance categories
    display_df = cashier_scores.copy()
    display_df['Performance Category'] = display_df['TOTAL SCORE PPSA'].apply(
        lambda x: "🏆 Excellent" if x >= 120 else
                 "⭐ Good" if x >= 100 else
                 "⚠️ Needs Improvement" if x >= 80 else
                 "🚨 Critical"
    )
    
    # Create DataTable
    columns = [
        {"name": "Nama Kasir", "id": "NAMA KASIR"},
        {"name": "Total Score", "id": "TOTAL SCORE PPSA", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "Category", "id": "Performance Category"},
        {"name": "PSM", "id": "SCORE PSM", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "PWP", "id": "SCORE PWP", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "SG", "id": "SCORE SG", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "APC", "id": "SCORE APC", "type": "numeric", "format": {"specifier": ".1f"}},
    ]
    
    # Filter available columns
    available_columns = [col for col in columns if col['id'] in display_df.columns]
    
    return dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=available_columns,
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=10
    )

# --- RUN APP ---
# Untuk deployment di Render
server = app.server

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
