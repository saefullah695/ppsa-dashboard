import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os, json, warnings

warnings.filterwarnings('ignore')

# --- APP CONFIG ---
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "🚀 PPSA Analytics Dashboard"
server = app.server

# =========================================================
# 🧩 DATA LOADING & CLEANING
# =========================================================

def load_data_from_gsheet():
    """Load data dari Google Sheets dengan robust parsing"""
    try:
        service_account_json = os.environ.get("GCP_SERVICE_ACCOUNT")
        if not service_account_json:
            print("❌ 'GCP_SERVICE_ACCOUNT' tidak ditemukan.")
            return pd.DataFrame()

        creds_info = json.loads(service_account_json)
        SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
        WORKSHEET_NAME = os.environ.get("WORKSHEET_NAME", "Sheet1")
        if not SPREADSHEET_ID:
            print("❌ SPREADSHEET_ID belum diset.")
            return pd.DataFrame()

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)

        ss = client.open_by_key(SPREADSHEET_ID)
        try:
            ws = ss.worksheet(WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            print(f"⚠️ Worksheet '{WORKSHEET_NAME}' tidak ditemukan, gunakan sheet pertama.")
            ws = ss.get_worksheet(0)

        data = ws.get_all_values()
        if not data:
            print("❌ Tidak ada data di sheet.")
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=[c.strip() for c in data[0]])
        df = df.replace("", np.nan).dropna(how="all")
        print(f"✅ Data dimuat: {len(df)} baris, {len(df.columns)} kolom.")
        return df

    except Exception as e:
        print(f"❌ Gagal ambil data: {e}")
        return pd.DataFrame()


def process_data(df):
    """Membersihkan & memproses data agar konsisten"""
    if df.empty:
        return df

    df.columns = df.columns.str.strip().str.upper()

    # --- Kolom tanggal ---
    date_candidates = [c for c in ["TANGGAL", "DATE", "TGL"] if c in df.columns]
    if date_candidates:
        col = date_candidates[0]
        df["TANGGAL"] = pd.to_datetime(df[col], errors="coerce", dayfirst=True, infer_datetime_format=True)
        df = df.dropna(subset=["TANGGAL"])
        df["HARI"] = df["TANGGAL"].dt.day_name(locale="id_ID")
        df["BULAN"] = df["TANGGAL"].dt.month_name(locale="id_ID")
        df["MINGGU"] = df["TANGGAL"].dt.isocalendar().week
    else:
        print("⚠️ Tidak ada kolom tanggal valid.")
        df["TANGGAL"] = pd.NaT

    # --- Shift ---
    if "SHIFT" in df.columns:
        df["SHIFT"] = df["SHIFT"].astype(str).str.extract(r"(\d)").fillna("0")
        df["SHIFT"] = df["SHIFT"].map({
            "1": "Shift 1 (Pagi)",
            "2": "Shift 2 (Siang)",
            "3": "Shift 3 (Malam)"
        }).fillna("Unknown")
    else:
        df["SHIFT"] = "Unknown"

    # --- Numeric cleanup ---
    num_candidates = [c for c in df.columns if any(x in c for x in ["TARGET", "ACTUAL", "BOBOT"])]
    for col in num_candidates:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[^\d,.-]", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # --- Hitung skor per komponen ---
    def safe_div(a, b): return (a / b * 100) if b and b != 0 else 0
    for comp in ["PSM", "PWP", "SG", "APC"]:
        if f"{comp} ACTUAL" in df.columns and f"{comp} TARGET" in df.columns:
            df[f"(%) {comp} ACV"] = df.apply(lambda r: safe_div(r[f"{comp} ACTUAL"], r[f"{comp} TARGET"]), axis=1)
            if f"BOBOT {comp}" in df.columns:
                df[f"SCORE {comp}"] = (df[f"(%) {comp} ACV"] * df[f"BOBOT {comp}"]) / 100
            else:
                df[f"SCORE {comp}"] = df[f"(%) {comp} ACV"] / 4

    score_cols = [c for c in df.columns if c.startswith("SCORE ")]
    df["TOTAL SCORE PPSA"] = df[score_cols].sum(axis=1)
    df = df.dropna(subset=["TOTAL SCORE PPSA"]).sort_values("TANGGAL")
    print(f"✅ Data diproses: {len(df)} record.")
    return df


# =========================================================
# 🔁 LOAD DATA
# =========================================================
try:
    raw_df = load_data_from_gsheet()
    processed_df = process_data(raw_df.copy()) if not raw_df.empty else pd.DataFrame()
except Exception as e:
    print(f"Error load data: {e}")
    processed_df = pd.DataFrame()


# =========================================================
# 🧠 METRIC FUNGSI UTAMA
# =========================================================
def calculate_overall_ppsa_breakdown(df):
    if df.empty:
        return {"total": 0, "psm": 0, "pwp": 0, "sg": 0, "apc": 0}
    weights = {"PSM": 20, "PWP": 25, "SG": 30, "APC": 25}
    scores = {}
    for comp, w in weights.items():
        act_col, tgt_col = f"{comp} ACTUAL", f"{comp} TARGET"
        if act_col in df.columns and tgt_col in df.columns:
            actual, target = df[act_col].sum(), df[tgt_col].sum()
            acv = (actual / target * 100) if target > 0 else 0
            scores[comp.lower()] = acv * w / 100
        else:
            scores[comp.lower()] = 0
    scores["total"] = sum(scores.values())
    return scores


# =========================================================
# 🎨 DASHBOARD LAYOUT
# =========================================================
def create_header():
    data_status = "✅ Data Loaded" if not processed_df.empty else "❌ No Data"
    data_count = f" ({len(processed_df)} records)" if not processed_df.empty else ""
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.H1("🚀 PPSA Analytics Dashboard",
                        className="main-title mb-3",
                        style={"color": "#667eea", "fontWeight": "800", "fontSize": "3rem"}),
                html.H4("2GC6 BAROS PANDEGLANG",
                        style={"color": "#764ba2", "fontWeight": "600"}),
                html.Div([
                    html.Span(f"{data_status}{data_count}",
                              style={"color": "#10b981" if not processed_df.empty else "#ef4444"}),
                    html.Span(" | "),
                    html.Span(f"Spreadsheet: {os.environ.get('SPREADSHEET_ID', 'N/A')[:20]}..."),
                    html.Span(" | "),
                    html.Span(f"Worksheet: {os.environ.get('WORKSHEET_NAME', 'Sheet1')}")
                ], className="mb-3")
            ], className="text-center")
        ])
    )


header = create_header()
overall_scores = calculate_overall_ppsa_breakdown(processed_df)


def create_kpi_card(title, value, color, icon):
    return dbc.Card(
        dbc.CardBody([
            html.Div([html.Span(icon, className="me-2"),
                      html.Span(title, style={"fontSize": "0.9rem", "fontWeight": "700"})],
                     className="d-flex align-items-center mb-2"),
            html.H3(f"{value:.1f}", style={"color": color, "fontWeight": "800", "fontSize": "2.2rem"})
        ]),
        className="m-2 shadow",
        style={"borderRadius": "12px", "borderLeft": f"4px solid {color}"}
    )


# =========================================================
# 📊 DASH LAYOUT
# =========================================================
app.layout = dbc.Container([
    header,
    dbc.Row([
        dbc.Col(create_kpi_card("PSM", overall_scores["psm"], "#667eea", "📊"), 3),
        dbc.Col(create_kpi_card("PWP", overall_scores["pwp"], "#764ba2", "🛒"), 3),
        dbc.Col(create_kpi_card("SG", overall_scores["sg"], "#f093fb", "🛡️"), 3),
        dbc.Col(create_kpi_card("APC", overall_scores["apc"], "#4facfe", "⚡"), 3),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("🏆 TOTAL PPSA SCORE", className="text-center", style={"color": "white"}),
                    html.H1(f"{overall_scores['total']:.1f}",
                            className="text-center",
                            style={"color": "white", "fontWeight": "900", "fontSize": "4rem"})
                ]),
                style={"background": "linear-gradient(135deg,#667eea,#764ba2)",
                       "borderRadius": "20px", "color": "white"},
                className="shadow text-center p-4"
            ), width=8, className="mx-auto"
        )
    ]),
    html.Hr(),
    html.Footer([
        html.P("🚀 PPSA Analytics Dashboard • Powered by Dash • © 2025",
               className="text-center text-muted mt-4")
    ])
], fluid=True, className="py-4")


# =========================================================
# 🧭 RUN APP
# =========================================================
if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
