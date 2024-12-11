import pdfplumber
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def upload_pdf():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

def extract_tables_to_excel(pdf_path):
    output_excel_path = "Extracted_Tables_with_Titles.xlsx"

    table_titles = {
        "Professor": "Faculty Information",
        "Classroom": "Classroom Details",
        "Laboratory": "Lab Information",
        "Course": "Courses Offered",
        "Intake": "Student Intake",
        "PCs": "PC Details",
        "titles": "Library Details",
    }

    tables_with_titles = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    if df.shape[0] < 3 or df.shape[1] < 3:
                        continue
                    for keyword, title in table_titles.items():
                        if df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False)).any().any():
                            if title in ["Courses Offered", "Library Details"] and df.shape[0] > 20:
                                continue
                            df["Source_Page"] = page_num
                            tables_with_titles.append((df, title))
                            break
            except Exception as e:
                print(f"Error on page {page_num}: {e}")

    if tables_with_titles:
        with pd.ExcelWriter(output_excel_path, engine="openpyxl") as writer:
            title_counts = {}
            for table, title in tables_with_titles:
                title_counts[title] = title_counts.get(title, 0) + 1
                sheet_name = f"{title} ({title_counts[title]})" if title_counts[title] > 1 else title
                table.to_excel(writer, sheet_name=sheet_name[:31], index=False, header=False)

        print(f"Extracted tables saved to: {output_excel_path}")
        return output_excel_path
    else:
        print("No relevant tables found.")
        return None

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

def generate_report(faculty_data, infrastructure_data):
    file_name = 'compliance_report.pdf'
    doc = SimpleDocTemplate(file_name, pagesize=letter)
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

        # Highlight non-compliant rows in red
        for row_idx, row in enumerate(data[1:], start=1):  # Start from row 1 to skip header
            if row[3].lower() != 'compliant':  # Check if compliance is not 'compliant'
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

        # Highlight non-compliant rows in red
        for row_idx, row in enumerate(data[1:], start=1):  # Start from row 1 to skip header
            if row[3].lower() != 'compliant':  # Check if compliance is not 'compliant'
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                ]))
        
        elements.append(table)

    # Add some space between tables
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))

    # Call the table creation functions
    create_faculty_compliance_table(elements, faculty_data)
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))  # Add space between tables
    create_infrastructure_compliance_table(elements, infrastructure_data)

    # Build the PDF
    doc.build(elements)

    print(f"Report generated: {file_name}")

def main():
    # Upload PDF file
    pdf_path = upload_pdf()
    if not pdf_path:
        print("No file selected. Exiting.")
        return

    # Extract tables from PDF
    excel_file = extract_tables_to_excel(pdf_path)
    if not excel_file:
        return

    # Perform faculty analysis
    total_professors, total_associate_professors, total_assistant_professors = analyze_faculty_data(excel_file)

    # Perform classroom and related data analysis
    total_labs, total_classrooms, total_dept_library, workshops, smart_classroom = analyze_classroom_data(excel_file)

    # Get student intake from user
    student_intake = int(input("Enter student intake: "))

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

    # Generate the report
    generate_report(faculty_data, infrastructure_data)

# Required libraries
# pip install pdfplumber pandas openpyxl reportlab tkinter

if __name__ == "__main__":
    main()