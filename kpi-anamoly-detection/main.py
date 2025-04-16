import pandas as pd
from detectors.anomaly_detector import detect_percent_change_anomalies, detect_zscore_anomalies
from groq import Groq
import os
from dotenv import load_dotenv
import streamlit as st
from fpdf import FPDF
import datetime

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# Streamlit config
st.set_page_config(page_title="KPI Anomaly Detection", page_icon="📊", layout="wide")

# Styling for a clean and minimalistic UI
st.markdown("""
    <style>
        .stApp {
            background-color: #f4f4f9;
            color: #333333;
            font-family: 'Helvetica Neue', sans-serif;
        }
        .stButton>button {
            background-color: #0061f2;
            color: white;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s ease, transform 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0051c2;
            transform: scale(1.05);
        }
        .alert-header {
            color: #0061f2;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 10px;
            padding: 10px;
            background-color: #e6f0ff;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
        .alert-body {
            background-color: #ffffff;
            color: #333333;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            font-size: 16px;
            margin-top: 10px;
        }
        .stTitle {
            font-size: 36px;
            font-weight: 700;
            color: #333333;
            text-align: center;
            margin-top: 50px;
            margin-bottom: 30px;
        }
        .stMarkdown {
            text-align: center;
            color: #333333;
            font-size: 18px;
        }
        .stFileUploader>label {
            font-size: 18px;
            color: #333333;
            text-align: center;
            font-weight: bold;
        }
        .stFileUploader>div {
            text-align: center;
            padding: 20px;
            border: 2px solid #0061f2;
            border-radius: 8px;
            background-color: #e6f0ff;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .stFileUploader>div:hover {
            background-color: #cce0ff;
        }
        .stDownloadButton>button {
            background-color: #28a745;
            color: white;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 8px;
        }
        .stDownloadButton>button:hover {
            background-color: #218838;
        }
        .stInfo {
            background-color: #e6f0ff;
            color: #333333;
            font-size: 18px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Add Heading
st.markdown("<h1 class='stTitle'>KPI Anomaly Detection</h1>", unsafe_allow_html=True)

# Load Data
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"], label_visibility="collapsed")

def load_data(file):
    if file is not None:
        df = pd.read_csv(file)
        st.write("### Data Preview:")
        st.write(df.head())
        return df
    return None

df = load_data(uploaded_file)

# Update Data
if df is not None and st.checkbox("🔧 Update CSV records"):
    row_idx = st.number_input("Select Row Index", 0, len(df)-1, step=1)
    col_name = st.selectbox("Select Column", options=df.columns)
    new_val = st.text_input(f"New Value for {col_name}", value=str(df.at[row_idx, col_name]))
    if st.button("Update Record"):
        df.at[row_idx, col_name] = new_val
        st.success(f"Updated: {col_name} = {new_val}")
    st.write(df.head())
    st.download_button("📥 Download Updated CSV", df.to_csv(index=False), "updated_data.csv", "text/csv")

# Filter Section
if df is not None:
    st.markdown("### 🔍 Filter Data")
    kpi_filter = st.multiselect("Select KPIs", df.columns)
    date_range = st.date_input("Date Range", [])
    if kpi_filter:
        df = df[kpi_filter]
    if len(date_range) == 2:
        try:
            df = df[(pd.to_datetime(df['date']) >= pd.to_datetime(date_range[0])) & (pd.to_datetime(df['date']) <= pd.to_datetime(date_range[1]))]
        except:
            st.warning("Date column not found or invalid format.")

    # Detect Anomalies
    percent_anomalies = detect_percent_change_anomalies(df)
    zscore_anomalies = detect_zscore_anomalies(df)
    all_anomalies = percent_anomalies + zscore_anomalies

    # Display Alerts & Generate Report
    if all_anomalies:
        st.markdown("### 🚨 Anomaly Alerts")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="KPI Anomaly Report", ln=True, align='C')
        pdf.ln(10)

        for anomaly in all_anomalies:
            change_value = anomaly.get('change', 'N/A')
            previous_value = anomaly.get('previous', 'N/A')

            # Consistent, short Alert Message Format
            prompt = f"""
            Anomaly Detected: KPI: {anomaly['kpi']} | Date: {anomaly['date']}
            - Change: {change_value}%
            - Previous Value: {previous_value if previous_value != 'N/A' else 'N/A'}
            - Current Value: {anomaly['current']}
            """

            chat_completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            summary = chat_completion.choices[0].message.content

            # Display Alert Header and Body
            st.markdown(f"""
                <div class='alert-header'>📢 {anomaly['kpi']} - {anomaly['date']}</div>
                <div class='alert-body'>{summary}</div>
            """, unsafe_allow_html=True)

            pdf.multi_cell(0, 10, f"{summary}\n")

        pdf_output = f"kpi_anomaly_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            st.download_button("📥 Download Anomaly Report (PDF)", f, file_name=pdf_output)
    else:
        st.success("✅ No anomalies detected. All metrics are normal.")
else:
    st.markdown('<div class="stInfo">📁 Please upload a CSV file to begin.</div>', unsafe_allow_html=True)
