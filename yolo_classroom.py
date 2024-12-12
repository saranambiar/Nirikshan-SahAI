from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from tempfile import TemporaryDirectory
from ultralytics import YOLO
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import shutil
import zipfile
from io import BytesIO
from tempfile import NamedTemporaryFile
from mongoengine import connect,Document,StringField,FileField
from institute.models import Images
import requests
import cloudinary
import cloudinary.uploader
from io import BytesIO
from pydantic import BaseModel

connect(
    db="Login",
    host="mongodb+srv://param4mc:3Fj0PbA9t4V6bT1E@cluster0.9f6ij.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Cluster0"
)

cloudinary.config(
    cloud_name='sih24',  
    api_key='491834354871145',        
    api_secret='JAzYjhW7CXXvUFehkGF7IDMUsSM'  
)

class deficiency_report(Document):
    file = FileField(required=True)
    college = StringField(required=True)
    branch = StringField(required=True)
    meta = {
        'collection': 'deficiency_report'
    }

app = FastAPI()

model = YOLO("yolov8l.pt") 


def get_cloudinary_image_as_binary(cloudinary_url):
    """Retrieves a Cloudinary image as binary data from a given URL."""
    try:
        response = requests.get(cloudinary_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return BytesIO(response.content).getvalue()
    except Exception as e:
        print(f"Error retrieving image from Cloudinary: {e}")
        return None

def save_binary_to_temp_file(binary_data, prefix='image', suffix='.jpg'):
    """Save binary image data to a temporary file."""
    with NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix) as temp_file:
        temp_file.write(binary_data)
        return temp_file.name

def process_classroom_images(binary_images, threshold_class):
    result_files = []  
    statuses_c = []  
    recommendations_c = []  
    list_of_images = [] 

    for binary_image in binary_images:
        if binary_image is None:
            continue
        
        temp_image_path = save_binary_to_temp_file(binary_image)
        list_of_images.append(os.path.basename(temp_image_path))

        results = model.predict(temp_image_path)  
        obj_count = {}  
        for result in results:
            for box in result.boxes: 
                label = result.names[int(box.cls)]  
                obj_count[label] = obj_count.get(label, 0) + 1  

        if 'dining table' in obj_count:
            obj_count['bench'] = obj_count.get('bench', 0) + obj_count['dining table']
            del obj_count['dining table']  

        if 'bench' in obj_count:
            count = obj_count['bench']
            if count + 16 < threshold_class:
                missing = threshold_class - (count + 16)
                statuses_c.append('Insufficient equipment')
                recommendations_c.append(f'Get {missing:.0f} more benches.')
            else:
                statuses_c.append('Sufficient equipment')
                recommendations_c.append('-')
        else:
            statuses_c.append('Not a classroom')
            recommendations_c.append(f'Invalid image: {os.path.basename(temp_image_path)}')
        
        os.unlink(temp_image_path)

    return list_of_images, statuses_c, recommendations_c

def process_lab_images(binary_images, threshold_lab):
    result_files = []  
    statuses = []  
    recommendations = []  
    list_of_images = [] 

    for binary_image in binary_images:
        if binary_image is None:
            continue
        
        temp_image_path = save_binary_to_temp_file(binary_image)
        list_of_images.append(os.path.basename(temp_image_path))

        results = model.predict(temp_image_path)  
        obj_count = {}  
        for result in results:
            for box in result.boxes: 
                label = result.names[int(box.cls)] 
                obj_count[label] = obj_count.get(label, 0) + 1  

        obj_count['monitor'] = obj_count.get('monitor', 0) + obj_count.pop('tv', 0) + obj_count.pop('laptop', 0)

        if 'monitor' in obj_count:
            count = obj_count['monitor']
            if count + 6 < threshold_lab:
                missing = threshold_lab - (count + 6)
                statuses.append('Insufficient equipment')
                recommendations.append(f'Get {missing:.0f} more monitors.')
            else:
                statuses.append('Sufficient equipment')
                recommendations.append('-')
        else:
            statuses.append('Not a lab')
            recommendations.append(f'Invalid image: {os.path.basename(temp_image_path)}')
        
        os.unlink(temp_image_path)

    return list_of_images, statuses, recommendations



def generate_pdf(classroom_data, lab_data, output_file, college_name, branch, intake, no_div, no_batches):
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title = Paragraph('Equipment Status and Recommendations', styles['Title'])
    elements.append(title)
    
    # College details
    details_text = Paragraph(
        f'College: {college_name} | Branch: {branch} | Intake: {intake} | Divisions: {no_div} | Batches: {no_batches}', 
        styles['Normal']
    )
    elements.append(Spacer(1, 12))
    elements.append(details_text)
    
    # Classroom section
    elements.append(Spacer(1, 12))
    elements.append(Paragraph('Report for CLASSROOMS:', styles['Heading2']))
    
    if not classroom_data or len(classroom_data[0]) != 3:
        classroom_data = [['No data', 'No data', 'No data']]
    
    data1 = [['Image', 'Status', 'Recommendations']] + classroom_data
    
    table1 = Table(data1, colWidths=[2 * inch, 2 * inch, 3 * inch])
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table1)

    # Labs section
    elements.append(Spacer(1, 12))
    elements.append(Paragraph('Report for LABS:', styles['Heading2']))
    
    if not lab_data or len(lab_data[0]) != 3:
        lab_data = [['No data', 'No data', 'No data']]
    
    data2 = [['Image', 'Status', 'Recommendations']] + lab_data
    
    table2 = Table(data2, colWidths=[2 * inch, 2 * inch, 3 * inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table2)

    doc.build(elements)

class data(BaseModel):
    college_name: str
    branch: str

@app.post("/generate-report/")
async def generate_report(info : data):
    try:
        document = Images.objects(college=info.college_name)
        for doc in document:  # Loop through all documents
            classroom_images = doc.classroom
            lab_images = doc.lab
            
            if not classroom_images or not lab_images:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Either classroom or lab images are missing in document {doc.id}. Please upload both."
                )


        cloudinary_urls_lab = []
        cloudinary_urls_class = []
        for doc in document:
            for item in doc.classroom:
                if item.get('branch')=="entc":
                    branch_intake = item.get('itbk')
                    no_div=item.get('nod')
                    no_batches=item.get('nob')
                    print(item.get('url'))
                    url = item.get('url')  # Replace 'urls' with the actual key for URLs
                    if url:  # Ensure URLs exist
                        if isinstance(url, list):  # If URLs is a list, extend the result
                            cloudinary_urls_class.extend(url)
                        else:  # If a single URL, append it directly
                            cloudinary_urls_class.append(url)

        for doc in document:
            for item in doc.lab:
                if item.get('branch')=="entc":
                    print(item.get('url'))
                    url = item.get('url')  # Replace 'urls' with the actual key for URLs
                    if url:  # Ensure URLs exist
                        if isinstance(url, list):  # If URLs is a list, extend the result
                            cloudinary_urls_lab.extend(url)
                        else:  # If a single URL, append it directly
                            cloudinary_urls_lab.append(url)
        
        print(cloudinary_urls_class)
        binary_class_urls=[]
        binary_lab_urls=[]
        for url in cloudinary_urls_class:
            binary_url=get_cloudinary_image_as_binary(url)
            binary_class_urls.append(binary_url)
        for url in cloudinary_urls_lab:
            binary_url=get_cloudinary_image_as_binary(url)
            binary_lab_urls.append(binary_url)
                                    

        classroom_results = process_classroom_images(binary_class_urls, threshold_class=10)
        lab_results = process_lab_images(binary_lab_urls, threshold_lab=5)

        # Prepare data for PDF generation
        classroom_data = list(zip(classroom_results[0], classroom_results[1], classroom_results[2]))
        lab_data = list(zip(lab_results[0], lab_results[1], lab_results[2]))

        # Create a PDF file for the report
        output_pdf = f"{info.branch}_report.pdf"
        generate_pdf(
            classroom_data, 
            lab_data, 
            output_pdf, 
            info.college_name, 
            info.branch, 
            branch_intake, 
            no_div, 
            no_batches
        )

        with open(output_pdf, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

        # Create a DeficiencyReport instance and save it to MongoDB
        Deficiency_report = deficiency_report(
            file=pdf_data,  # Save the binary data of the PDF
            college=info.college_name,
            branch=info.branch
        )
        Deficiency_report.save()
        # Return the PDF file to the user
        return {
            "message": "Report generated and saved successfully",
            "file_id": str(deficiency_report.id),  # MongoDB file ID
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")