import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

import pytesseract
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from fuzzywuzzy import fuzz

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='certificate_verification.log'
)
logger = logging.getLogger(__name__)

class CertificateVerifier:
    def __init__(self, tesseract_path: str = "/usr/bin/tesseract"):
        """
        Initialize the Certificate Verifier
        
        :param tesseract_path: Path to Tesseract OCR executable
        """
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Configuration for certificate types
        self.certificate_types = [
            "Certificate of Architecture",
            "Certificate of Bank Manager",
            "Certificate of Advocate",
            "Academic Certificate",
            "Professional Certificate"
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using multiple methods
        
        :param pdf_path: Path to PDF file
        :return: Extracted text
        """
        try:
            reader = PdfReader(pdf_path)
            extracted_text = ""

            for page in reader.pages:
                # Try direct text extraction
                page_text = page.extract_text() or ""

                # If no text, convert page to image and use OCR
                if not page_text.strip():
                    try:
                        images = convert_from_path(pdf_path)
                        for img in images:
                            page_text += pytesseract.image_to_string(img)
                    except Exception as img_error:
                        logger.warning(f"Image-based text extraction failed: {img_error}")

                extracted_text += page_text

            return extracted_text.strip()

        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""

    def get_user_format(self, certificate_type: str, format_pdf_path: str = None) -> str:
        """
        Get the expected format for a specific certificate type.
        Optionally, extract the format from a provided PDF file.
        
        :param certificate_type: Type of certificate
        :param format_pdf_path: Path to the PDF containing the format
        :return: Expected format as a string
        """
        if format_pdf_path:
            try:
                extracted_format = self.extract_text_from_pdf(format_pdf_path)
                if extracted_format:
                    logger.info(f"Extracted format from PDF: {extracted_format}")
                    return extracted_format
                else:
                    logger.warning("No text could be extracted from the format PDF.")
            except Exception as e:
                logger.error(f"Error reading format PDF: {e}")

        # Default fallback format
        example_formats = {
            "Certificate of Architecture": "Name, Degree, Institution, Date",
            "Certificate of Bank Manager": "Name, Position, Bank Name, Date",
            "Certificate of Advocate": "Name, Bar Council Registration, Date",
            "Academic Certificate": "Name, Degree, Major, University, Graduation Date",
            "Professional Certificate": "Name, Certification, Issuing Body, Date"
        }

        return example_formats.get(certificate_type, "Name, Details, Date")

    def compare_certificate_format(self, extracted_text: str, expected_format: str) -> Dict[str, float]:
        """
        Compare extracted text with expected format
        
        :param extracted_text: Text extracted from certificate
        :param expected_format: User-provided expected format
        :return: Detailed format matching results
        """
        format_elements = [elem.strip().lower() for elem in expected_format.split(',')]

        format_analysis = {
            'overall_similarity': 0.0,
            'element_matches': {}
        }

        cleaned_text = extracted_text.lower()

        for element in format_elements:
            match_ratio = fuzz.partial_ratio(element, cleaned_text)
            format_analysis['element_matches'][element] = match_ratio

        format_analysis['overall_similarity'] = sum(
            format_analysis['element_matches'].values()
        ) / len(format_elements)

        return format_analysis

    def process_certificate(self, pdf_path: str, metadata_words: List[str], format_pdf_path: str = None) -> Dict[str, Any]:
        """
        Comprehensive certificate verification
        
        :param pdf_path: Path to PDF certificate
        :param metadata_words: Expected metadata words
        :param format_pdf_path: Path to the format PDF
        :return: Verification results dictionary
        """
        try:
            extracted_text = self.extract_text_from_pdf(pdf_path)

            if not extracted_text:
                logger.error("No text could be extracted from the PDF")
                return {
                    'text_extraction': False,
                    'certificate_type': None,
                    'format_match': False,
                    'format_details': None
                }

            detected_type = next(
                (cert_type for cert_type in self.certificate_types 
                 if fuzz.partial_ratio(cert_type.lower(), extracted_text.lower()) > 80),
                None
            )

            if not detected_type:
                detected_type = "Unknown Certificate Type"

            user_format = self.get_user_format(detected_type, format_pdf_path)
            format_analysis = self.compare_certificate_format(extracted_text, user_format)

            return {
                'text_extraction': bool(extracted_text),
                'certificate_type': detected_type,
                'format_match': format_analysis['overall_similarity'] >= 70,
                'format_details': format_analysis
            }

        except Exception as e:
            logger.error(f"Certificate processing error: {e}")
            return {
                'text_extraction': False,
                'certificate_type': None,
                'format_match': False,
                'format_details': None
            }

def generate_report(batch_results: List[Dict[str, Any]], output_path: str):
    """
    Generate a report based on the batch processing results
    
    :param batch_results: List of results from certificate processing
    :param output_path: Path to save the generated report (JSON format)
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_path = os.path.join(output_path, f"certificate_verification_report_{timestamp}.json")

        with open(report_path, 'w') as report_file:
            json.dump(batch_results, report_file, indent=4)

        print(f"Report generated successfully at: {report_path}")

    except Exception as e:
        logger.error(f"Error generating report: {e}")


def main():
    # Paths for certificates and reports
    certificates_dir = input("Enter the directory containing certificate PDFs: ").strip()
    report_output_dir = input("Enter the directory to save the report: ").strip()

    metadata_words = ["Pune", "Institute", "computer"]
    verifier = CertificateVerifier()

    batch_results = []

    for filename in os.listdir(certificates_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(certificates_dir, filename)
            print(f"Processing {filename}...")

            result = verifier.process_certificate(pdf_path, metadata_words)
            result['file_name'] = filename
            batch_results.append(result)

    generate_report(batch_results, report_output_dir)

if __name__ == "__main__":
    main()
