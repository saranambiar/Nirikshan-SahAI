import pandas as pd
import numpy as np
from mongoengine import connect, Document, StringField, FileField
from io import BytesIO
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

MONGODB_URI = "mongodb+srv://param4mc:3Fj0PbA9t4V6bT1E@cluster0.9f6ij.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Cluster0"
DB_NAME = "Login"

connect(DB_NAME, MONGODB_URI)
class ExcelFile(Document):
    name = StringField(required=True)
    file = FileField(required=True)
    college = StringField(required=True)

    meta = {
        'collection': 'ExcelFile'
    }

def fetch_excel_from_db(file_name):
    """
    Fetch Excel file from MongoDB by name and load it into a DataFrame.
    """
    excel_doc = ExcelFile.objects(name=file_name).first()
    if not excel_doc:
        raise ValueError(f"No file found with the name: {file_name}")

    # Read the binary Excel file into a BytesIO object
    excel_data = BytesIO(excel_doc.file.read())
    df = pd.read_excel(excel_data)
    return df

# -------------------------------
# 4. Preprocess Data
# -------------------------------
def preprocess_data(df):
    """
    Preprocess data for anomaly detection.
    """
    # Label encode categorical fields
    label_encoder_college = LabelEncoder()
    df['College_Encoded'] = label_encoder_college.fit_transform(df['College'])

    label_encoder_branch = LabelEncoder()
    df['Branch_Encoded'] = label_encoder_branch.fit_transform(df['Branch'])

    # Select features for anomaly detection
    features = [
        'Min_Placement_Percentage',
        'Avg_Placement_Percentage',
        'Max_Placement_Percentage',
        'Percentile_Cutoff',
        'College_Encoded',
        'Branch_Encoded'
    ]

    # Scale the numerical features
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)

    return df, df_scaled

# -------------------------------
# 5. Detect Anomalies Using Isolation Forest
# -------------------------------
def detect_anomalies(df, df_scaled, contamination=0.05):
    """
    Detect anomalies using Isolation Forest.
    """
    # Initialize Isolation Forest
    anomaly_detector = IsolationForest(contamination=contamination, random_state=42)
    df['Anomaly'] = anomaly_detector.fit_predict(df_scaled)

    # Mark anomalies: -1 means anomaly, 1 means normal
    df['Anomaly'] = df['Anomaly'].map({1: 'Normal', -1: 'Anomaly'})
    anomalies = df[df['Anomaly'] == 'Anomaly']

    return df, anomalies

# -------------------------------
# 6. Generate PDF Report with Anomalies
# -------------------------------
def generate_pdf(anomalies, output_file='anomaly_report.pdf'):
    """
    Generate a PDF report with the detected anomalies.
    """
    # Create PDF document
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []

    # Title
    styles = getSampleStyleSheet()
    title = Paragraph(f"Placement Anomaly Detection Report - {datetime.now().strftime('%Y-%m-%d')}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Table Data
    data = [['College', 'Branch', 'Year', 'Min %', 'Avg %', 'Max %', 'Cutoff']]
    for _, row in anomalies.iterrows():
        data.append([
            row['College'],
            row['Branch'],
            row['Year'],
            f"{row['Min_Placement_Percentage']:.2f}",
            f"{row['Avg_Placement_Percentage']:.2f}",
            f"{row['Max_Placement_Percentage']:.2f}",
            f"{row['Percentile_Cutoff']:.2f}"
        ])

    # Create Table
    table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])

    # Table Style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # Add Table to Elements
    elements.append(table)

    # Build PDF
    doc.build(elements)
    print(f"PDF saved as '{output_file}'")

# -------------------------------
# 7. Full Pipeline Execution
# -------------------------------
def run_full_analysis(file_name, contamination=0.05):
    """
    Execute complete anomaly detection and reporting pipeline.
    """
    df = fetch_excel_from_db(file_name)
    df, df_scaled = preprocess_data(df)
    df, anomalies = detect_anomalies(df, df_scaled, contamination)
    generate_pdf(anomalies)
    print(f"{len(anomalies)} anomalies detected and reported.")

# Execute the pipeline
if __name__ == "__main__":
    # Replace with your file name stored in MongoDB
    file_name = 'placement_data.xlsx'
    run_full_analysis(file_name)
