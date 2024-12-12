import re
import os
import cv2
import numpy as np
from datetime import datetime
import pytesseract
from PIL import Image
import fitz  # PyMuPDF for PDF rendering

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class CertificateVerifier:
    def __init__(self, file_path, keywords, start_date, end_date, metadata_words, threshold):
        """
        Initialize certificate verification parameters
        
        Args:
        file_path (str): Path to the certificate file (PDF or Image)
        keywords (list): List of keywords to verify
        start_date (str): Start date for verification
        end_date (str): End date for verification
        metadata_words (list): Words to verify in metadata
        threshold (int): Minimum metadata word match threshold
        """
        self.file_path = file_path
        self.keywords = keywords
        self.start_date = start_date
        self.end_date = end_date
        self.metadata_words = metadata_words
        self.threshold = threshold
        self.image = None
        self.ocr_text = ""

    def convert_pdf_to_image(self):
        """
        Converts the first page of a PDF to an image using PyMuPDF.
        """
        try:
            # Open the PDF using PyMuPDF
            pdf_document = fitz.open(self.file_path)

            # Render the first page as an image
            page = pdf_document[0]  # First page (index 0)
            pix = page.get_pixmap(dpi=300)  # High DPI for better resolution
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert to OpenCV format
            self.image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            pdf_document.close()

            print("PDF successfully converted to an image using PyMuPDF.")
            return True

        except Exception as e:
            print(f"PDF Conversion Error: {e}")
            return False

    def preprocess_image(self):
        """
        Preprocess image for better OCR results
        
        Returns:
        numpy.ndarray: Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian Blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        return thresh

    def detect_stamp_region(self, preprocessed_image):
        """
        Detect potential stamp regions in the image
        
        Args:
        preprocessed_image (numpy.ndarray): Preprocessed image
        
        Returns:
        tuple: Stamp region coordinates or None
        """
        # Find contours
        contours, _ = cv2.findContours(
            preprocessed_image, 
            cv2.RETR_TREE, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            approx = cv2.approxPolyDP(
                contour, 
                0.02 * cv2.arcLength(contour, True), 
                True
            )
            area = cv2.contourArea(contour)
            
            # Filter for potential stamp regions
            if area > 500 and (len(approx) > 4 or len(approx) == 4):
                return cv2.boundingRect(contour)
        
        return None

    def extract_ocr_text(self, preprocessed_image):
        """
        Extract text from the image using Tesseract OCR
        
        Args:
        preprocessed_image (numpy.ndarray): Preprocessed image
        
        Returns:
        str: Extracted text
        """
        # Use preprocessed image for OCR
        self.ocr_text = pytesseract.image_to_string(preprocessed_image)
        return self.ocr_text

    def validate_keywords(self):
        """
        Validate keywords in the extracted text
        
        Returns:
        tuple: (verification_status, matched_keywords)
        """
        matched_keywords = [
            keyword for keyword in self.keywords 
            if keyword.lower() in self.ocr_text.lower()
        ]
        return len(matched_keywords) > 0, matched_keywords

    def validate_metadata(self):
        """
        Validate metadata words in the extracted text
        
        Returns:
        tuple: (verification_status, matched_word_count)
        """
        text_words = self.ocr_text.lower().split()
        match_count = sum(
            1 for word in self.metadata_words 
            if word in text_words
        )
        return match_count >= self.threshold, match_count

 
    def verify_date(self):
  
    # Updated date pattern to handle more separator variations
        date_pattern = r"\b(\d{1,2}[-/.\s]?\d{1,2}[-/.\s]?\d{4})\b"
        dates_found = re.findall(date_pattern, self.ocr_text)

        if dates_found:
            # Print the raw extracted date for debugging
            print("Extracted Date from OCR:", dates_found[0])

            # Clean the extracted date (remove unwanted spaces or separators)
            cleaned_date = dates_found[0].replace(' ', '').replace('.', '/').replace('-', '/')

            try:
                # Now parse the cleaned date
                extracted_date = datetime.strptime(cleaned_date, "%d/%m/%Y")
                start_date_obj = datetime.strptime(self.start_date, "%d/%m/%Y")
                end_date_obj = datetime.strptime(self.end_date, "%d/%m/%Y")

                # Compare the extracted date with the provided date range
                if start_date_obj <= extracted_date <= end_date_obj:
                    return True, extracted_date.strftime('%d/%m/%Y')
                else:
                    return False, extracted_date.strftime('%d/%m/%Y')
            except ValueError:
                return False, "Error parsing extracted date"
        else:
            return False, "No valid date detected"

    

    def verify_certificate(self):
        """
        Main certificate verification method
        
        Returns:
        bool: Overall verification status
        """
        # Convert PDF to image
        if not self.convert_pdf_to_image():
            return False

        # Preprocess image
        preprocessed_image = self.preprocess_image()

        # Extract OCR text
        self.extract_ocr_text(preprocessed_image)

        # Perform verifications
        keyword_verification, matched_keywords = self.validate_keywords()
        metadata_verification, metadata_match_count = self.validate_metadata()
        date_verification, date_result = self.verify_date()

        # Optional: Stamp detection (you can enhance this)
        stamp_region = self.detect_stamp_region(preprocessed_image)

        # Print verification results
        print("\n--- Certificate Verification Results ---")
        print(f"Keywords Verified: {keyword_verification}")
        print(f"Matched Keywords: {matched_keywords}")
        print(f"Metadata Verified: {metadata_verification}")
        print(f"Metadata Matched Words: {metadata_match_count}")
        print(f"Date Verified: {date_verification}")
        print(f"Date Details: {date_result}")
        print(f"Stamp Region Detected: {'Yes' if stamp_region else 'No'}")

        # Final verification
        return (keyword_verification and 
                metadata_verification and 
                date_verification)

# Example Usage
def main():
    # Input parameters
    file_path = r"D:\Certificate verification\ocr\bonafide.pdf"  # Can be PDF or image
    certificate_name = "Bonafide Certificate"
    keywords = [certificate_name.lower()]
    start_date = "01/01/2024"
    end_date = "31/12/2024"
    metadata_college = "Pune Institute of Computer Technology"
    metadata_words = metadata_college.lower().split()
    threshold = 1

    # Create verifier instance
    verifier = CertificateVerifier(
        file_path, 
        keywords, 
        start_date, 
        end_date, 
        metadata_words, 
        threshold
    )

    # Verify certificate
    verification_status = verifier.verify_certificate()
    
    # Final result
    print("\nFinal Verification:", 
          "Certificate Verified Successfully" if verification_status 
          else "Certificate Verification Failed")

if __name__ == "__main__":
    main()
