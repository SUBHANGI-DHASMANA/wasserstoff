import logging
from typing import List, Dict, Any
from PIL import Image
import shutil
import subprocess

try:
    import pytesseract
    from pdf2image import convert_from_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

def is_tesseract_installed():
    if not TESSERACT_AVAILABLE:
        return False

    try:
        if shutil.which('tesseract') is not None:
            return True

        subprocess.run(['tesseract', '--version'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

OCR_AVAILABLE = is_tesseract_installed()

logger = logging.getLogger(__name__)

class OCRService:

    @staticmethod
    def process_image(image_path: str) -> str:
        if not OCR_AVAILABLE:
            logger.warning("OCR is not available. Tesseract is not installed or not in PATH.")
            return "OCR processing not available. Text extraction skipped."
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error processing image with OCR: {str(e)}")
            return "Error during OCR processing. Text extraction failed."

    @staticmethod
    def process_pdf(pdf_path: str) -> List[Dict[str, Any]]:
        if not OCR_AVAILABLE:
            logger.warning("OCR is not available. Tesseract is not installed or not in PATH.")
            return [{
                "page_num": 1,
                "text": "OCR processing not available. Text extraction skipped."
            }]
        try:
            pages = convert_from_path(pdf_path)
            result = []
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                result.append({
                    "page_num": i + 1,
                    "text": text
                })
            return result
        except Exception as e:
            logger.error(f"Error processing PDF with OCR: {str(e)}")
            return [{
                "page_num": 1,
                "text": f"Error during OCR processing: {str(e)}"
            }]

    @staticmethod
    def is_scanned_document(pdf_path: str) -> bool:
        if not OCR_AVAILABLE:
            logger.warning("OCR is not available. Tesseract is not installed or not in PATH.")
            return False
        try:
            pages = convert_from_path(pdf_path, first_page=1, last_page=1)
            if not pages:
                return False
            text = pytesseract.image_to_string(pages[0])
            return len(text.strip()) < 100
        except Exception as e:
            logger.error(f"Error checking if document is scanned: {str(e)}")
            return False
