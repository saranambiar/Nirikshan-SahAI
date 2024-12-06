from mongoengine import StringField, FileField, Document, connect

MONGO_ATLAS_URI = 'mongodb+srv://param4mc:3Fj0PbA9t4V6bT1E@cluster0.9f6ij.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&appName=Cluster0'
connect('Login',host=MONGO_ATLAS_URI)

class certificate(Document):
    name = StringField(required=True) 
    file = FileField(required=True)

    meta = {
        'collection': 'certificate_format'
    }

name = [
    'Certificate of Advocate format',
    'Certificate of Architect Registered with Council of Architecture format',
    'Certificate of the Bank Manager format'
]

pdf_file_paths = [
    "E:/Programming/SIH_24/frontend/certificate formats/CERTIFICATE-1.pdf",
    "E:/Programming/SIH_24/frontend/certificate formats/CERTIFICATE-2.pdf",
    "E:/Programming/SIH_24/frontend/certificate formats/CERTIFICATE-3_0.pdf"
]

for i, file_path in enumerate(pdf_file_paths):
    # Read the file
    with open(file_path, 'rb') as filee:
        # Create a new certificate entry in the database
        cert = certificate(
            name=name[i],  # You can adjust the name as needed
            file=filee
        )
        cert.save()
        print(f"Certificate {i + 1} uploaded successfully.")