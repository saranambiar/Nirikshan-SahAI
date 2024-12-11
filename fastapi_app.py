from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mongoengine import connect, Document, StringField, FileField
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from fastapi.responses import StreamingResponse
from institute.models import mandatory_dis

app = FastAPI()

# Connect to MongoDB
connect(
    db="Login",
    host="mongodb+srv://param4mc:3Fj0PbA9t4V6bT1E@cluster0.9f6ij.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Cluster0"
)


class excel_data(Document):
    college_name = StringField(required=True)
    intake = StringField(required=True)
    file_data = FileField()  # Field to store the processed Excel file

    meta={
        'collection':'excel_data'
    }

class CollegeLoginInfo(BaseModel):
    college_name: str
    intake: str

@app.post("/process-mandatory-disclosure/")
async def process_mandatory_disclosure(info: CollegeLoginInfo):
    try:
        # Fetch mandatory disclosure based on college_name
        mandatory_disclosure = mandatory_dis.objects(college_name=info.college_name).first()
        if not mandatory_disclosure:
            raise HTTPException(status_code=404, detail="Mandatory disclosure not found")

        # Read the PDF file from the database
        pdf_file = mandatory_disclosure.file.read()  # Read the file data

        # Keywords and associated sheet titles
        table_titles = {
            "Professor": "Faculty Information",
            "Classroom": "Classroom Details",
            "Laboratory": "Lab Information",
            "Course": "Courses Offered",
            "Intake": "Student Intake",
            "PCs": "PC Details",
            "titles": "Library Details",
        }

        # DataFrame to store extracted data
        tables_with_titles = []

        # Open the PDF and extract tables
        with pdfplumber.open(BytesIO(pdf_file)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    tables = page.extract_tables()
                    for table in tables:
                        # Convert table to DataFrame
                        df = pd.DataFrame(table)
                        # Skip tables with fewer than 3 rows or columns
                        if df.shape[0] < 3 or df.shape[1] < 3:
                            continue
                        # Check if the table contains any of the keywords
                        for keyword, title in table_titles.items():
                            if df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False)).any().any():
                                # Skip large tables for specific titles
                                if title == "Courses Offered" and df.shape[0] > 20:
                                    continue
                                if title == "Library Details" and df.shape[0] > 20:
                                    continue
                                df["Source_Page"] = page_num  # Add source page number
                                tables_with_titles.append((df, title))
                                break
                except Exception as e:
                    print(f"Error on page {page_num}: {e}")

        # Save relevant tables to Excel
        if tables_with_titles:
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                title_counts = {}
                for table, title in tables_with_titles:
                    title_counts[title] = title_counts.get(title, 0) + 1
                    sheet_name = f"{title} ({title_counts[title]})" if title_counts[title] > 1 else title
                    table.to_excel(writer, sheet_name=sheet_name[:31], index=False, header=False)

            output_excel.seek(0)

            # Save the processed data to a new class in the database
            processed_data = excel_data(
                college_name=info.college_name,
                intake =info.intake,
                file_data=output_excel.read()  # Store the Excel file data
            )
            processed_data.save()


            return {"message": "Mandatory disclosure processed successfully", "data": processed_data.id}
        else:
            raise HTTPException(status_code=404, detail="No relevant tables found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))