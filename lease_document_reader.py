# lease_document_reader.py
import os
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from transformers import pipeline
from PIL import Image
from config import *
from post_processing import *

def preprocess_image(image):
    """
    Preprocess image for better OCR results.
    """
    image = image.convert("L")  # Convert to grayscale
    image = image.point(lambda x: 0 if x < 128 else 255)  # Binarize
    return image

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF using Tesseract OCR or pdfplumber as a fallback.
    """
    try:
        # First, try pdfplumber for text-based PDFs
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text
    except Exception as e:
        print(f"pdfplumber failed for {pdf_path}: {e}")

    # Fallback to Tesseract OCR for scanned PDFs
    try:
        images = convert_from_path(pdf_path)
        text = ""
        for image in images:
            image = preprocess_image(image)
            text += pytesseract.image_to_string(image, lang=TESSERACT_LANG, config=TESSERACT_CONFIG) + "\n"
        return text
    except Exception as e:
        print(f"Tesseract OCR failed for {pdf_path}: {e}")
        return ""

def process_lease_document(pdf_path):
    """
    Process a lease document and extract key fields with post-processing.
    """
    print(f"Processing {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        print(f"No text extracted from {pdf_path}")
        return {}

    # Debug: Print first 200 characters of extracted text
    print("Extracted Text Preview:", text[:200])

    # Initialize question-answering pipeline
    try:
        qa_pipeline = pipeline("question-answering", model=QA_MODEL, device=DEVICE)
    except Exception as e:
        print(f"Failed to initialize QA pipeline: {e}")
        return {}

    # Map questions to post-processing functions
    post_processors = {
        "Tenant Name": clean_tenant_name,
        "Lease Duration": clean_lease_duration,
        "Rent Amount": clean_rent_amount,
        "Property Address": clean_property_address
    }

    results = {}
    for question, key in QUESTIONS:
        try:
            result = qa_pipeline(question=question, context=text)
            answer = result["answer"]
            confidence = result["score"]
            # Apply post-processing
            cleaned_answer = post_processors[key](answer, confidence, MIN_CONFIDENCE)
            results[key] = cleaned_answer
        except Exception as e:
            print(f"Error processing question '{question}' for {pdf_path}: {e}")
            results[key] = "Error"

    return results

def main():
    """
    Main function to process all PDFs in the lease_documents directory.
    """
    if not os.path.exists(PDF_DIR):
        print(f"PDF directory {PDF_DIR} does not exist")
        return

    # Set Tesseract path if specified
    if TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    # Process each PDF in the directory
    for pdf_file in os.listdir(PDF_DIR):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, pdf_file)
            results = process_lease_document(pdf_path)
            print(f"\nResults for {pdf_file}:")
            for key, value in results.items():
                print(f"{key}: {value}")

if __name__ == "__main__":
    main()