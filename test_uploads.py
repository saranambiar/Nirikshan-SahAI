from mongoengine import connect, Document, FileField, StringField
import io
import pandas as pd

# MongoDB connection details
MONGODB_URI = "mongodb+srv://param4mc:3Fj0PbA9t4V6bT1E@cluster0.9f6ij.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Cluster0"
DB_NAME = "Login"

# Connect to MongoDB Atlas
connect(db=DB_NAME, host=MONGODB_URI)

class excel_data(Document):
    college_name = StringField(required=True)
    file_data = FileField()

    meta = {
        'collection': 'excel_data'
    }

# Retrieve the document by college_name
document = excel_data.objects(college_name="Pune Institute of Computer Technology").first()

# Extract the Excel file data from the document
excel_data_bytes = document.file_data.read()

# Save the Excel file
output_file = "output.xlsx"
with open(output_file, "wb") as f:
    f.write(excel_data_bytes)

print(f"Excel file saved as: {output_file}")