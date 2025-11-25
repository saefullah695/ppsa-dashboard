import pandas as pd
import numpy as np
from datetime import datetime

def calculate_shift_performance_detailed(df):
    """Calculate detailed shift performance"""
    if df.empty or 'SHIFT' not in df.columns:
        return pd.DataFrame()
    
    weights = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}
    
    shift_performance = df.groupby('SHIFT').agg({
        'PSM Target': 'sum', 'PSM Actual': 'sum',
        'PWP Target': 'sum', 'PWP Actual': 'sum',
        'SG Target': 'sum', 'SG Actual': 'sum',
        'APC Target': 'mean', 'APC Actual': 'mean',
        'ACTUAL TEBUS 2500': 'sum',
        'TARGET TEBUS 2500': 'sum',
        'TOTAL SCORE PPSA': ['mean', 'median', 'std', 'count']
    }).reset_index()
    
    # Process the aggregated data
    shift_performance.columns = ['_'.join(col).strip() if col[1] else col[0] for col in shift_performance.columns.values]
    
    # Calculate scores
    for comp in ['PSM', 'PWP', 'SG']:
        target_col = f'{comp} Target_sum'
        actual_col = f'{comp} Actual_sum'
        if target_col in shift_performance.columns and actual_col in shift_performance.columns:
            acv_col = f'ACV {comp} (%)'
            shift_performance[acv_col] = (shift_performance[actual_col] / shift_performance[target_col] * 100).fillna(0)
            score_col = f'SCORE {comp}'
            shift_performance[score_col] = (shift_performance[acv_col] * weights[comp]) / 100
    
    if 'APC Target_mean' in shift_performance.columns and 'APC Actual_mean' in shift_performance.columns:
        shift_performance['ACV APC (%)'] = (shift_performance['APC Actual_mean'] / shift_performance['APC Target_mean'] * 100).fillna(0)
        shift_performance['SCORE APC'] = (shift_performance['ACV APC (%)'] * weights['APC']) / 100
    
    score_cols = [f'SCORE {comp}' for comp in ['PSM', 'PWP', 'SG', 'APC'] 
                 if f'SCORE {comp}' in shift_performance.columns]
    if score_cols:
        shift_performance['TOTAL SCORE PPSA'] = shift_performance[score_cols].sum(axis=1)
    
    return shift_performance

def calculate_daily_performance_detailed(df):
    """Calculate detailed daily performance"""
    if df.empty or 'TANGGAL' not in df.columns:
        return pd.DataFrame()
    
    weights = {'PSM': 20, 'PWP': 25, 'SG': 30, 'APC': 25}
    
    daily_performance = df.groupby('TANGGAL').agg({
        'PSM Target': 'sum', 'PSM Actual': 'sum',
        'PWP Target': 'sum', 'PWP Actual': 'sum',
        'SG Target': 'sum', 'SG Actual': 'sum',
        'APC Target': 'mean', 'APC Actual': 'mean',
        'ACTUAL TEBUS 2500': 'sum',
        'TARGET TEBUS 2500': 'sum',
        'TOTAL SCORE PPSA': ['mean', 'median', 'std', 'count']
    }).reset_index()
    
    daily_performance.columns = ['_'.join(col).strip() if col[1] else col[0] for col in daily_performance.columns.values]
    
    for comp in ['PSM', 'PWP', 'SG']:
        target_col = f'{comp} Target_sum'
        actual_col = f'{comp} Actual_sum'
        if target_col in daily_performance.columns and actual_col in daily_performance.columns:
            acv_col = f'ACV {comp} (%)'
            daily_performance[acv_col] = (daily_performance[actual_col] / daily_performance[target_col] * 100).fillna(0)
            score_col = f'SCORE {comp}'
            daily_performance[score_col] = (daily_performance[acv_col] * weights[comp]) / 100
    
    if 'APC Target_mean' in daily_performance.columns and 'APC Actual_mean' in daily_performance.columns:
        daily_performance['ACV APC (%)'] = (daily_performance['APC Actual_mean'] / daily_performance['APC Target_mean'] * 100).fillna(0)
        daily_performance['SCORE APC'] = (daily_performance['ACV APC (%)'] * weights['APC']) / 100
    
    score_cols = [f'SCORE {comp}' for comp in ['PSM', 'PWP', 'SG', 'APC'] 
                 if f'SCORE {comp}' in daily_performance.columns]
    if score_cols:
        daily_performance['TOTAL SCORE PPSA'] = daily_performance[score_cols].sum(axis=1)
    
    daily_performance['Day of Week'] = daily_performance['TANGGAL'].dt.day_name()
    
    return daily_performance.sort_values('TANGGAL')
