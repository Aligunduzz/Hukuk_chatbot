import logging

import pdfplumber

logger = logging.getLogger(__name__)

try:
    from .config import ERROR_MESSAGES, MAX_PDF_SIZE_MB
except ImportError:
    from config import ERROR_MESSAGES, MAX_PDF_SIZE_MB


def extract_text_from_pdf(pdf_file):
    """PDF dosyasindan metin cikartir."""
    try:
        if hasattr(pdf_file, "size"):
            file_size_mb = pdf_file.size / (1024 * 1024)
            if file_size_mb > MAX_PDF_SIZE_MB:
                return f"HATA: {ERROR_MESSAGES['pdf_too_large']}"

        pdf_file.seek(0)
        text_parts = []

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)

        extracted_text = "\n".join(text_parts).strip()
        if not extracted_text:
            logger.warning("PDF'den metin cikarilamadi.")
            return "HATA: PDF'den metin cikarilamadi."

        return extracted_text
    except Exception:
        logger.exception("PDF islenirken hata olustu.")
        return f"HATA: {ERROR_MESSAGES['pdf_processing_error']}"


def get_pdf_info(pdf_file):
    """PDF'nin sayfa sayisini alir."""
    try:
        pdf_file.seek(0)
        with pdfplumber.open(pdf_file) as pdf:
            return {
                "page_count": len(pdf.pages),
                "status": "success",
            }
    except Exception:
        logger.exception("PDF bilgisi alinamadi.")
        return {
            "page_count": 0,
            "status": "error",
        }
