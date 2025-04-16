import pandas as pd
import numpy as np

def detect_percent_change_anomalies(df, threshold=15):
    """
    Flags rows where % change in KPI exceeds a threshold.
    Returns a list of dictionaries with anomaly details.
    """
    anomalies = []
    kpis = df.columns[1:]  # Skip 'date'
    
    for kpi in kpis:
        df[f"{kpi}_pct_change"] = df[kpi].pct_change() * 100
        for i in range(1, len(df)):
            change = df.loc[i, f"{kpi}_pct_change"]
            if abs(change) >= threshold:
                anomalies.append({
                    "date": df.loc[i, "date"],
                    "kpi": kpi,
                    "current": df.loc[i, kpi],
                    "previous": df.loc[i-1, kpi],
                    "change": change
                })
    
    return anomalies


def detect_zscore_anomalies(df, threshold=2.0):
    """
    Flags KPI values that are statistical outliers (Z-score based).
    """
    anomalies = []
    kpis = df.columns[1:]
    
    for kpi in kpis:
        mean = df[kpi].mean()
        std = df[kpi].std()
        df[f"{kpi}_zscore"] = (df[kpi] - mean) / std
        
        for i in range(len(df)):
            z = df.loc[i, f"{kpi}_zscore"]
            if abs(z) > threshold:
                anomalies.append({
                    "date": df.loc[i, "date"],
                    "kpi": kpi,
                    "current": df.loc[i, kpi],
                    "z_score": z
                })
    
    return anomalies
