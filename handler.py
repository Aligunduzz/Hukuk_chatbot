import PyPDF2
import pdfplumber

try:
    from .config import ERROR_MESSAGES, MAX_PDF_SIZE_MB
except ImportError:
    from config import ERROR_MESSAGES, MAX_PDF_SIZE_MB


def extract_text_from_pdf(pdf_file):
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
        return extracted_text if extracted_text else "HATA: PDF'den metin cikarilamadi."
    except Exception as exc:
        return f"HATA: PDF islenirken sorun olustu - {exc}"


def extract_text_with_pypdf2(pdf_file):
    try:
        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_parts = []

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)

        extracted_text = "\n".join(text_parts).strip()
        return extracted_text if extracted_text else "HATA: PDF'den metin cikarilamadi."
    except Exception:
        return f"HATA: {ERROR_MESSAGES['invalid_pdf']}"


def split_text_into_chunks(text, chunk_size=2000, overlap=200):
    words = text.split()
    if not words:
        return []

    step = max(1, chunk_size - overlap)
    chunks = []
    for index in range(0, len(words), step):
        chunk = " ".join(words[index:index + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def get_pdf_info(pdf_file):
    try:
        pdf_file.seek(0)
        with pdfplumber.open(pdf_file) as pdf:
            return {
                "page_count": len(pdf.pages),
                "status": "success",
            }
    except Exception:
        return {
            "page_count": 0,
            "status": "error",
        }
