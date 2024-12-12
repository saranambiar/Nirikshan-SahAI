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
from mongoengine import connect
from institute.models import Images
import cloudinary
import cloudinary.uploader
from io import BytesIO

connect(
    db="Login",
    host="mongodb+srv://param4mc:3Fj0PbA9t4V6bT1E@cluster0.9f6ij.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Cluster0"
)

cloudinary.config(
    cloud_name='sih24',  
    api_key='491834354871145',        
    api_secret='JAzYjhW7CXXvUFehkGF7IDMUsSM'  
)

def get_cloudinary_image_as_binary(cloudinary_url):
    """Retrieves a Cloudinary image as binary data from a given URL."""
    try:
        response = cloudinary.uploader.download(cloudinary_url)
        return BytesIO(response).getvalue()
    except Exception as e:
        print(f"Error retrieving image from Cloudinary: {e}")
        return None

image_document = Images.objects.get(college='college_name')
classroom_urls = image_document.get_cloudinary_urls_from_field('classroom')

app = FastAPI()

model = YOLO("yolov8l.pt") 

@app.get("/")
def read_root():
    return {"Hello World!"}

def get_image_files(directory_path_or_zip):
    image_files = []

    if zipfile.is_zipfile(directory_path_or_zip):
        with zipfile.ZipFile(directory_path_or_zip, 'r') as zip_ref:
            with TemporaryDirectory() as temp_dir:
                zip_ref.extractall(temp_dir)

                for filename in os.listdir(temp_dir):
                    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                        image_files.append(os.path.join(temp_dir, filename))
    else:
        for filename in os.listdir(directory_path_or_zip):
            if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                image_files.append(os.path.join(directory_path_or_zip, filename))

    return image_files


def process_classroom_images(image_files, threshold_class):
    result_files = []  
    statuses_c = []  
    recommendations_c = []  
    list_of_images = [] 

    for image_file in image_files:
        
        list_of_images.append(os.path.basename(image_file))

        results = model.predict(image_file)  
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
            statuses_c.append('Input image of classroom only')
            recommendations_c.append(f'Invalid image: {os.path.basename(image_file)}')

    return list_of_images, statuses_c, recommendations_c




def process_lab_images(image_files, threshold_lab):
    result_files = []  
    statuses = []  
    recommendations = []  
    list_of_images = [] 

    for image_file in image_files:

        list_of_images.append(os.path.basename(image_file))

        results = model.predict(image_file)  
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
            recommendations.append(f'Invalid image: {os.path.basename(image_file)}')

    return list_of_images, statuses, recommendations


def generate_report(
    branch: str, 
    branch_intake: int, 
    no_div: int, 
    no_batches: int, 
    classroom_file: UploadFile = File(...), 
    labs_file: UploadFile = File(...)
):
    try:
       
        classroom_dir = os.path.join("temp_classroom_dir")
        labs_dir = os.path.join("temp_labs_dir")
        os.makedirs(classroom_dir, exist_ok=True)
        os.makedirs(labs_dir, exist_ok=True)

       
        with NamedTemporaryFile(delete=False) as tmp_zip_classroom:
            shutil.copyfileobj(classroom_file.file, tmp_zip_classroom)
            tmp_zip_classroom_path = tmp_zip_classroom.name

        with NamedTemporaryFile(delete=False) as tmp_zip_labs:
            shutil.copyfileobj(labs_file.file, tmp_zip_labs)
            tmp_zip_labs_path = tmp_zip_labs.name

        with zipfile.ZipFile(tmp_zip_classroom_path, 'r') as zip_ref:
            zip_ref.extractall(classroom_dir)

        with zipfile.ZipFile(tmp_zip_labs_path, 'r') as zip_ref:
            zip_ref.extractall(labs_dir)

       
        classroom_images = get_image_files(classroom_dir)
        lab_images = get_image_files(labs_dir)

      
        classroom_image_names, classroom_statuses, classroom_recommendations = process_classroom_images(classroom_images, threshold_class=10)
        lab_image_names, lab_statuses, lab_recommendations = process_lab_images(lab_images, threshold_lab=5)

      
        classroom_data = [
            [img, status, recommendation] 
            for img, status, recommendation in zip(classroom_image_names, classroom_statuses, classroom_recommendations)
        ]
        
        lab_data = [
            [img, status, recommendation] 
            for img, status, recommendation in zip(lab_image_names, lab_statuses, lab_recommendations)
        ]

      
        output_pdf = "report.pdf"
        generate_pdf(classroom_data, lab_data, output_pdf)

     
        os.remove(tmp_zip_classroom_path)
        os.remove(tmp_zip_labs_path)

      
        return FileResponse(output_pdf, media_type="application/pdf", filename="report.pdf")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


def generate_pdf(classroom_data, lab_data, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
  
    print("Classroom Data:", classroom_data)
    print("Lab Data:", lab_data)
    
    title = Paragraph('Equipment Status and Recommendations', styles['Title'])
    elements.append(title)

  
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

    
    try:
        doc.build(elements)
    except Exception as e:
        print(f"Error building PDF: {e}")
        raise


@app.post("/generate-report/")
async def generate_report(
    branch: str, 
    branch_intake: int, 
    no_div: int, 
    no_batches: int, 
    classroom_file: UploadFile = File(...), 
    labs_file: UploadFile = File(...)
):
    try:
       
        classroom_dir = os.path.join("temp_classroom_dir")
        labs_dir = os.path.join("temp_labs_dir")
        os.makedirs(classroom_dir, exist_ok=True)
        os.makedirs(labs_dir, exist_ok=True)

       
        with NamedTemporaryFile(delete=False) as tmp_zip_classroom:
            shutil.copyfileobj(classroom_file.file, tmp_zip_classroom)
            tmp_zip_classroom_path = tmp_zip_classroom.name

        with NamedTemporaryFile(delete=False) as tmp_zip_labs:
            shutil.copyfileobj(labs_file.file, tmp_zip_labs)
            tmp_zip_labs_path = tmp_zip_labs.name

        # Extract ZIP files into their respective directories
        with zipfile.ZipFile(tmp_zip_classroom_path, 'r') as zip_ref:
            zip_ref.extractall(classroom_dir)

        with zipfile.ZipFile(tmp_zip_labs_path, 'r') as zip_ref:
            zip_ref.extractall(labs_dir)

        # Get image files from both directories
        classroom_images = get_image_files(classroom_dir)
        lab_images = get_image_files(labs_dir)

        # Process the images for classroom and lab
        classroom_results = process_classroom_images(classroom_images, threshold_class=10)  # You can adjust the threshold
        lab_results = process_lab_images(lab_images, threshold_lab=5)  # You can adjust the threshold

        classroom_data = list(zip(classroom_results[0], classroom_results[1], classroom_results[2]))
        lab_data = list(zip(lab_results[0], lab_results[1], lab_results[2]))

        # Create a PDF file for the report
        output_pdf = "report.pdf"
        generate_pdf(classroom_data, lab_data, output_pdf)

        # Clean up temporary files
        os.remove(tmp_zip_classroom_path)
        os.remove(tmp_zip_labs_path)

        # Return the PDF file to the user
        return FileResponse(output_pdf, media_type="application/pdf", filename="report.pdf")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
