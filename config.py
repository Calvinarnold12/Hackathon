# config.py
import os

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "lease_documents")

# Tesseract settings
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update this for your system
TESSERACT_LANG = "eng"
TESSERACT_CONFIG = "--psm 6"  # Page segmentation mode for better OCR

# Question-answering model settings
QA_MODEL = "deepset/roberta-base-squad2"
MIN_CONFIDENCE = 0.5  # Minimum confidence score for answers

# Questions and their corresponding keys for extraction
QUESTIONS = [
    ("Who is the tenant signing the lease agreement?", "Tenant Name"),
    ("What is the duration of the lease?", "Lease Duration"),
    ("What is the monthly rent amount?", "Rent Amount"),
    ("What is the full address of the leased property?", "Property Address")
]

# Device setting (-1 for CPU, 0 or higher for GPU if available)
DEVICE = -1