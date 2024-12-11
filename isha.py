import os
import cv2
import pytesseract
import re
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Adjust path as necessary

# Function to extract text from the image using pytesseract
def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

# Function to validate extracted keywords
import re

def validate_keywords(text, keywords):
    # Normalize the text (remove extra spaces, punctuation handling)
    text = re.sub(r'[^\w\s]', '', text.lower()).strip()  # Remove punctuation and extra spaces
    matched_keywords = [keyword.lower() for keyword in keywords if keyword.lower() in text]
    
    # Check if there are matched keywords
    return len(matched_keywords) > 0, matched_keywords


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

# Function to match format
def match_format(format_text, extracted_text):
    template_fields = re.findall(r"<.*?>", format_text)
    for field in template_fields:
        if field.strip("<>").lower() not in extracted_text.lower():
            return False
    return True

# Function to perform stamp detection and verification
def verify_stamp(image_path, metadata_words):
    # Load the image
    image = cv2.imread(image_path)

    # Preprocess the image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    thresholded_image = cv2.adaptiveThreshold(
        blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Detect contours (to identify stamp region)
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    stamp_region = None

    # Iterate through contours to find circular or rectangular shapes
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        if area > 500:  # Filter small areas to avoid noise
            if len(approx) > 4:  # Circle or similar shape
                stamp_region = cv2.boundingRect(contour)
                break
            elif len(approx) == 4:  # Rectangle
                stamp_region = cv2.boundingRect(contour)
                break

    if stamp_region:
        x, y, w, h = stamp_region
        stamp = gray_image[y:y+h, x:x+w]  # Crop the stamp region

        # Display the cropped stamp
        plt.imshow(stamp, cmap='gray')
        plt.title("Detected Stamp Region")
        plt.axis('off')
        plt.show()

        # Perform OCR on the stamp
        ocr_text_stamp = pytesseract.image_to_string(stamp, config='--psm 6')
        print("Extracted Text from Stamp:", ocr_text_stamp)

        # Verify stamp against metadata
        stamp_matches = [word for word in metadata_words if word in ocr_text_stamp.lower()]
        if stamp_matches:
            stamp_verification = True
            print(f"Stamp Verification Result: Verified (Matched Words: {stamp_matches})")
        else:
            stamp_verification = False
            print("Stamp Verification Result: Failed")
    else:
        stamp_verification = False
        print("No valid stamp region detected.")

    return stamp_verification

# Function to adjust threshold based on feedback
def adjust_threshold(feedback, threshold, step=1):
    """
    Adjusts the threshold based on feedback.
    Positive feedback increases the threshold; negative feedback decreases it.
    """
    for success in feedback:
        if success:
            threshold += step
        else:
            threshold = max(1, threshold - step)  # Prevent threshold from dropping below 1
    return threshold

# Main function to verify the certificate
def verify_certificate(image_path, keywords, start_date, end_date, metadata_words, threshold, format_text=None):
    # Extract text from the image
    ocr_text_full = extract_text_from_image(image_path)
    print("Extracted Text from Certificate:")
    print(ocr_text_full)

    # Verify keywords
    keyword_verification, matched_keywords = validate_keywords(ocr_text_full, keywords)
    print(f"\nKeyword Verification Result: {'Verified' if keyword_verification else 'Failed'} (Matched Keywords: {matched_keywords})")

    # Verify stamp
    stamp_verification = verify_stamp(image_path, metadata_words)

    # Verify date
    date_verification, date_result = verify_date(ocr_text_full, start_date, end_date)
    print(f"Date Verification Result: {'Verified' if date_verification else 'Failed'} (Details: {date_result})")

    # Perform format verification if applicable
    if format_text:
        format_verification = match_format(format_text, ocr_text_full)
        print(f"Format Verification Result: {'Verified' if format_verification else 'Failed'}")
    else:
        format_verification = True

    # Final verification result
    if keyword_verification and stamp_verification and date_verification and format_verification:
        print("\nFinal Verification: Certificate Verified Successfully")
        return True
    else:
        print("\nFinal Verification: Certificate Verification Failed")
        return False

# Simulated feedback data (True for successful verification, False otherwise)
feedback_data = [True, False, True, True, False]

# Set initial threshold and adjust based on feedback
threshold = 3  # Initial threshold value
threshold = adjust_threshold(feedback_data, threshold)

print(f"\nAdjusted Threshold: {threshold}")

# Example Usage
image_path = r"D:\Certificate verification\ocr\Screenshot 2024-12-05 102741.png"  # Update with your image path
keywords = "Internal quality assurance cell".lower()  # Example keyword for the certificate type
start_date = "01-01-2024"  # Start date for verification range
end_date = "31-12-2024"  # End date for verification range
metadata_words = "Pune Institute of Computer Technology".lower().split()  # Example metadata
threshold = 1  # Threshold for metadata matching

# Template for format verification (specific to "Certificate of Architecture")
format_text_architecture = "<certificate_of_architecture> <issued_by> <confirmation> <completion>"

# Run the verification (only perform format verification for specific certificate types)
model_verified = verify_certificate(image_path, keywords, start_date, end_date, metadata_words, threshold, format_text=format_text_architecture)

# Simulate Inspector Feedback
inspector_feedback = False  # Assume the inspector rejected the certificate

# Update feedback data based on inspector's feedback
feedback_data.append(inspector_feedback)

# Adjust the threshold based on the new feedback
threshold = adjust_threshold(feedback_data, threshold)
print(f"New Threshold after Inspector Feedback: {threshold}")
