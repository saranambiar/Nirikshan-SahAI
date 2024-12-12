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
import requests
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

college_name = "Pune Institute of Computer Technology"

# Query all documents
document = Images.objects(college=college_name)
cloudinary_urls = []
for doc in document:
    for item in doc.classroom:
        if item.get('branch')=="entc":
            print(item.get('url'))
            url = item.get('url')  # Replace 'urls' with the actual key for URLs
            if url:  # Ensure URLs exist
                if isinstance(url, list):  # If URLs is a list, extend the result
                    cloudinary_urls.extend(url)
                else:  # If a single URL, append it directly
                    cloudinary_urls.append(url)
    print(cloudinary_urls)

def get_cloudinary_image_as_binary(cloudinary_url):
    """Retrieves a Cloudinary image as binary data from a given URL."""
    try:
        response = requests.get(cloudinary_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return BytesIO(response.content).getvalue()
    except Exception as e:
        print(f"Error retrieving image from Cloudinary: {e}")
        return None

binary_classrooms=[]
for item in cloudinary_urls:
    updated=get_cloudinary_image_as_binary(item)
    binary_classrooms.append(updated)

for item in binary_classrooms:
    if item:
        with open("downloaded_image.jpg", "wb") as file:
            file.write(item)
            print("Image saved successfully!")
    else:
        print("Failed to download the image.")