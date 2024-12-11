
from mongoengine import connect, Document, StringField, FileField
import os

# Connect to MongoDB
connect(
    db="Login",
    host="mongodb+srv://param4mc:3Fj0PbA9t4V6bT1E@cluster0.9f6ij.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Cluster0"
)

class compliancereport(Document):
    college_name = StringField(required=True)
    intake = StringField(required=True)
    report_file = FileField()
    
    meta = {
        'collection': 'compliance_reports'
    }

def download_pdf(college_name, intake, output_file):
    # Fetch the compliance report based on college_name and intake
    report = compliancereport.objects(college_name=college_name, intake=intake).first()
    
    if not report:
        print("No report found for the specified college and intake.")
        return

    # Get the PDF data from the report_file field
    pdf_data = report.report_file.read()  # Read the file data

    # Write the PDF data to a file
    with open(output_file, 'wb') as f:
        f.write(pdf_data)
    
    print(f"PDF downloaded successfully as '{output_file}'.")

if __name__ == "__main__":
    # Specify the college name and intake you want to download the report for
    college_name = "Pune Institute of Computer Technology"  # Replace with the actual college name
    intake = "1200"  # Replace with the actual intake

    # Specify the output file name
    output_file = "compliance_report.pdf"

    # Call the download function
    download_pdf(college_name, intake, output_file)