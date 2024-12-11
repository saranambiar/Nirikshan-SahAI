from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mongoengine import connect, Document, StringField, FileField
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from fastapi.responses import StreamingResponse
from institute.models import mandatory_dis
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

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

class compliancereport(Document):
    college_name = StringField(required=True)
    intake = StringField(required=True)
    report_file = FileField()
    
    meta = {
        'collection': 'compliance_reports'
    }

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

            report_response = await create_compliance_report(info)
            return {
                "message": "Compliance report processed successfully",
                "report_response": report_response
            }
        else:
            raise HTTPException(status_code=404, detail="No relevant tables found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/create-compliance-report/")
async def create_compliance_report(info: CollegeLoginInfo):
    try:
        excel_file_obj = excel_data.objects(college_name=info.college_name).first()
        if not excel_file_obj:
            raise HTTPException(status_code=404, detail="Excel not found")

        # Convert stored file data to a file-like object
        excel_file = BytesIO(excel_file_obj.file_data.read())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    def analyze_faculty_data(excel_file):
        excel_data = pd.ExcelFile(excel_file)

        # Total professors analysis
        faculty_sheets = [sheet for sheet in excel_data.sheet_names if "Faculty Information" in sheet]
        total_professors = total_associate_professors = total_assistant_professors = 0

        for sheet_name in faculty_sheets:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            if df.shape[1] < 3:
                continue
            third_column = df.iloc[:, 2].astype(str).str.strip().str.lower()
            for value in third_column:
                if value == "professor":
                    total_professors += 1
                elif value in {"associate professor", "asso.professor"}:
                    total_associate_professors += 1
                elif value in {"assistant professor", "asst professor", "asstt.professor"}:
                    total_assistant_professors += 1

        print(f"Total Professors: {total_professors}")
        print(f"Total Associate Professors: {total_associate_professors}")
        print(f"Total Assistant Professors: {total_assistant_professors}")

        return total_professors, total_associate_professors, total_assistant_professors
    
    def analyze_classroom_data(excel_file):
        excel_data = pd.ExcelFile(excel_file)

        classroom_sheets = [sheet for sheet in excel_data.sheet_names if "Classroom Details" in sheet]
        total_labs = total_classrooms = total_dept_library = workshops = smart_classroom = 0

        for sheet_name in classroom_sheets:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            if df.shape[1] < 3:
                continue
            third_column = df.iloc[:, 2].astype(str).str.lower()

            total_labs += third_column.str.contains(r'\blaboratory\b', na=False).sum()
            total_classrooms += third_column.str.contains(r'\bclassroom\b', na=False).sum()
            total_dept_library += third_column.str.contains(r'\bdept. library\b|\bdepartment library\b', na=False).sum()
            workshops += third_column.str.contains(r'\bworkshop\b', na=False).sum()
            smart_classroom += third_column.str.contains(r'\bsmart classroom\b', na=False).sum()
        
        print(f"Total Labs: {total_labs}")
        print(f"Total Classrooms: {total_classrooms}")
        print(f"Total Dept Libraries: {total_dept_library}")
        print(f"Total Workshops: {workshops}")
        print(f"Total Smart Classrooms: {smart_classroom}")

        return total_labs, total_classrooms, total_dept_library, workshops, smart_classroom
    
    def validate_classroom_details(excel_file):
        excel_data = pd.ExcelFile(excel_file)
        
        # Find sheets related to Classroom Details
        classroom_sheets = [sheet for sheet in excel_data.sheet_names if "Classroom Details" in sheet]
        
        validation_results = []
        
        for sheet_name in classroom_sheets:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Ensure the DataFrame has at least 4 columns
            if df.shape[1] < 4:
                print(f"Error: '{sheet_name}' sheet has fewer than 4 columns.")
                continue
            
            # Iterate through the rows of the DataFrame
            for index, row in df.iterrows():
                third_col = str(row.iloc[2]).strip().lower()  # 3rd column
                fourth_col = row.iloc[3]  # 4th column (assumed numerical)
                
                # Default status
                status = "Valid"
                
                # Check conditions
                try:
                    if third_col in ["classroom", "laboratory", "smart classroom"]:
                        if fourth_col <= 66:
                            status = f"Invalid. The room is smaller by {66 - fourth_col} square meters"
                    elif third_col == "workshop":
                        if fourth_col <= 200:
                            status = f"Invalid. The room is smaller by {200 - fourth_col} square meters"
                    elif third_col == "tutorial":
                        if fourth_col <= 33:
                            status = f"Invalid. The room is smaller by {33 - fourth_col} square meters"
                    elif third_col == "seminar hall":
                        if fourth_col <= 132:
                            status = f"Invalid. The room is smaller by {132 - fourth_col} square meters"
                except Exception as e:
                    status = f"Error: {e}"
                
                # Append the result
                validation_results.append({
                    "Room Type (3rd Column)": row.iloc[2],
                    "Capacity (4th Column)": fourth_col,
                    "Status": status
                })
                print(validation_results)
                print(pd.DataFrame(validation_results))
        return pd.DataFrame(validation_results)

    def generate_report(faculty_data, infrastructure_data, validation_results=None, college_name=None, intake=None):
        try:
            # Create an in-memory PDF file
            output_pdf = BytesIO()
            doc = SimpleDocTemplate(output_pdf, pagesize=letter)
            elements = []  # List to hold all the content

            styles = getSampleStyleSheet()

            # Title Section
            title_style = styles['Title']
            title_style.fontName = 'Helvetica-Bold'
            title_style.fontSize = 16
            title = Paragraph("<b>Norms and Compliance with AICTE Norms</b>", title_style)
            elements.append(title)

            # Note Section
            note_style = styles['Normal']
            note_style.fontSize = 10
            note = Paragraph("<i>(Data taken from mandatory disclosure uploaded by college)</i>", note_style)
            elements.append(note)

            # Create faculty compliance table
            def create_faculty_compliance_table(elements, faculty_data):
                data = [
                    ['Faculty Category', 'Actual', 'Required', 'Compliance'],
                    ['Professor', faculty_data['professors'], faculty_data['required_professors'], faculty_data['professor_compliance']],
                    ['Associate Professor', faculty_data['associate_professors'], faculty_data['required_associate_professors'], faculty_data['associate_professor_compliance']],
                    ['Assistant Professor', faculty_data['assistant_professors'], faculty_data['required_assistant_professors'], faculty_data['assistant_professor_compliance']],
                ]

                table = Table(data, colWidths=[200, 100, 100, 100])
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black)
                ]))

                for row_idx, row in enumerate(data[1:], start=1):
                    if row[3].lower() != 'compliant':
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                        ]))

                elements.append(table)

            # Create infrastructure compliance table
            def create_infrastructure_compliance_table(elements, infrastructure_data):
                data = [
                    ['Infrastructure Category', 'Actual', 'Required', 'Compliance'],
                    ['Classrooms', infrastructure_data['classrooms'], infrastructure_data['required_classrooms'], infrastructure_data['classroom_compliance']],
                    ['Labs', infrastructure_data['labs'], infrastructure_data['required_labs'], infrastructure_data['lab_compliance']],
                    ['Workshops', infrastructure_data['workshops'], infrastructure_data['required_workshops'], infrastructure_data['workshop_compliance']],
                    ['Smart Classrooms', infrastructure_data['smart_classrooms'], infrastructure_data['required_smart_classrooms'], infrastructure_data['smart_classroom_compliance']],
                ]

                table = Table(data, colWidths=[200, 100, 100, 100])
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black)
                ]))

                for row_idx, row in enumerate(data[1:], start=1):
                    if row[3].lower() != 'compliant':
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                        ]))

                elements.append(table)

            # Create classroom validation table
            def create_classroom_validation_table(elements, validation_results):
                if validation_results is None or validation_results.empty:
                    return

                # Convert validation results to a format suitable for PDF table
                data = [['Room Type', 'Capacity', 'Status']]
                for _, row in validation_results.iterrows():
                    data.append([
                        str(row['Room Type (3rd Column)']), 
                        str(row['Capacity (4th Column)']), 
                        str(row['Status'])
                    ])

                table = Table(data, colWidths=[200, 100, 200])
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black)
                ]))

                # Highlight rows with invalid status
                for row_idx, row in enumerate(data[1:], start=1):
                    if 'Invalid' in str(row[2]):
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                        ]))

                # Add a title for the validation results
                validation_title = Paragraph("<b>Classroom Space Validation Results</b>", styles['Heading2'])
                elements.append(validation_title)
                elements.append(table)

            # Add some spacing between sections
            elements.append(Spacer(1, 12))

            # Create tables
            create_faculty_compliance_table(elements, faculty_data)
            elements.append(Spacer(1, 12))
            create_infrastructure_compliance_table(elements, infrastructure_data)
            
            # If validation results are provided, add them to the report
            if validation_results is not None and not validation_results.empty:
                elements.append(Spacer(1, 12))
                create_classroom_validation_table(elements, validation_results)

            # Build the PDF
            doc.build(elements)

            # Save the report in MongoDB
            output_pdf.seek(0)
            compliance_report = compliancereport(
                college_name=college_name,
                intake=intake,
                report_file=output_pdf.read()
            )
            compliance_report.save()

            return {"message": "Report generated and saved successfully", "report_id": str(compliance_report.id)}
        except Exception as e:
            # Log or re-raise with additional context
            raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


    total_professors, total_associate_professors, total_assistant_professors = analyze_faculty_data(excel_file)

    # Perform classroom and related data analysis
    total_labs, total_classrooms, total_dept_library,workshops, smart_classroom = analyze_classroom_data(excel_file)

    # Classroom validation
    validation_results = validate_classroom_details(excel_file)

    # Get student intake from user
    student_intake = int(info.intake)
    print(student_intake)
    # Prepare faculty data for report
    faculty_data = {
        'professors': total_professors,
        'required_professors': student_intake / 180,
        'professor_compliance': 'Compliant' if total_professors >= student_intake / 180 else 'Non-Compliant',
        'associate_professors': total_associate_professors,
        'required_associate_professors': student_intake / 90,
        'associate_professor_compliance': 'Compliant' if total_associate_professors >= student_intake / 90 else 'Non-Compliant',
        'assistant_professors': total_assistant_professors,
        'required_assistant_professors': student_intake / 30,
        'assistant_professor_compliance': 'Compliant' if total_assistant_professors >= student_intake / 30 else 'Non-Compliant',
    }

    # Prepare infrastructure data for report
    D = student_intake / 60
    dept = 1  # Assuming one department, adjust as needed
    labs = 2 * dept * 3  # Calculate required labs based on intake

    infrastructure_data = {
        'classrooms': total_classrooms,
        'required_classrooms': D,
        'classroom_compliance': 'Compliant' if total_classrooms >= D else 'Non-Compliant',
        'labs': total_labs,
        'required_labs': labs,
        'lab_compliance': 'Compliant' if total_labs >= labs else 'Non-Compliant',
        'workshops': workshops,
        'required_workshops': 1,
        'workshop_compliance': 'Compliant' if workshops >= 1 else 'Non-Compliant',
        'smart_classrooms': smart_classroom,
        'required_smart_classrooms': 4,
        'smart_classroom_compliance': 'Compliant' if smart_classroom >= 4 else 'Non-Compliant',
    }

    # Generate the report with validation results
    report_result = generate_report(
        faculty_data, 
        infrastructure_data, 
        validation_results, 
        college_name=info.college_name,
        intake=info.intake
    )

    return report_result