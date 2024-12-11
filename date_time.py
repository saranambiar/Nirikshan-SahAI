import re
from datetime import datetime
import pytesseract
from PIL import Image

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Adjust path as necessary

# Function to extract text from the image using pytesseract
def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

# Function to validate extracted keywords
def validate_keywords(text, keywords):
    matched_keywords = [keyword for keyword in keywords if keyword.lower() in text.lower()]
    return len(matched_keywords) > 0, matched_keywords

# Function to validate metadata and match words with a threshold
def validate_metadata(text, metadata_words, threshold):
    text_words = text.lower().split()
    match_count = sum(1 for word in metadata_words if word in text_words)
    return match_count >= threshold, match_count

# Function to verify the date
def verify_date(text, start_date, end_date):
    date_pattern = r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b"  # Matches DD-MM-YYYY or DD/MM/YYYY
    dates_found = re.findall(date_pattern, text)

    if dates_found:
        try:
            extracted_date = datetime.strptime(dates_found[0], "%d/%m/%Y")
            start_date_obj = datetime.strptime(start_date, "%d-%m-%Y")
            end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")

            if start_date_obj <= extracted_date <= end_date_obj:
                return True, extracted_date.strftime('%d/%m/%Y')
            else:
                return False, extracted_date.strftime('%d/%m/%Y')
        except ValueError:
            return False, "Error parsing extracted date"
    else:
        return False, "No valid date detected"

# Main function to verify the certificate
def verify_certificate(image_path, keywords, start_date, end_date, metadata_words, threshold):
    # Extract text from the image
    ocr_text_full = extract_text_from_image(image_path)
    print("Extracted Text from Certificate:")
    print(ocr_text_full)

    # Verify keywords
    keyword_verification, matched_keywords = validate_keywords(ocr_text_full, keywords)
    print(f"\nKeyword Verification Result: {'Verified' if keyword_verification else 'Failed'} (Matched Keywords: {matched_keywords})")

    # Verify metadata
    metadata_verification, match_count = validate_metadata(ocr_text_full, metadata_words, threshold)
    print(f"Metadata Verification Result: {'Verified' if metadata_verification else 'Failed'} (Matched Words: {match_count})")

    # Verify date
    date_verification, date_result = verify_date(ocr_text_full, start_date, end_date)
    print(f"Date Verification Result: {'Verified' if date_verification else 'Failed'} (Details: {date_result})")

    # Final verification result
    if keyword_verification and metadata_verification and date_verification:
        print("\nFinal Verification: Certificate Verified Successfully")
    else:
        print("\nFinal Verification: Certificate Verification Failed")

# Input parameters
image_path = "D:\Certificate verification\ocr\Screenshot 2024-12-05 102741.png"  # Update this with your local image file path
certificate_name = "Bonafide certificate"
keywords = certificate_name.lower()  # Keywords to match in the certificate
start_date = "01-01-2024"  # Start date for verification range
end_date = "31-12-2024"  # End date for verification range
metadata_college = "Pune Institute of Computer Technology"
metadata_words = metadata_college.lower().split()  # Split metadata into words for partial matching
threshold = 1  # Threshold for metadata matching

# Run the verification
verify_certificate(image_path, keywords, start_date, end_date, metadata_words, threshold)
