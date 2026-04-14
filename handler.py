import PyPDF2
import pdfplumber
from config import MAX_PDF_SIZE_MB, ERROR_MESSAGES

def extract_text_from_pdf(pdf_file):
    try:
        if hasattr(pdf_file, 'size'):
            file_size_mb = pdf_file.size / (1024 * 1024)
            if file_size_mb > MAX_PDF_SIZE_MB:
                return f"HATA: {ERROR_MESSAGES['pdf_too_large']}"
        
        pdf_file.seek(0)  # ← Bunu ekle
        
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        return text.strip() if text.strip() else "HATA: PDF'den metin çıkarılamadı"
    
    except Exception as e:
        return f"HATA: PDF işlenirken sorun oluştu - {str(e)}"


def extract_text_with_pymupdf(pdf_file):
    """
    PyPDF2 ile metin çıkarma (alternatif yöntem)
    
    Args:
        pdf_file: PDF dosyası
    
    Returns:
        Çıkarılan metin (str)
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        return f"HATA: {ERROR_MESSAGES['invalid_pdf']}"


def split_text_into_chunks(text, chunk_size=2000, overlap=200):
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():  # Boş değilse ekle
            chunks.append(chunk)
    
    return chunks


def get_pdf_info(pdf_file):
    """
    PDF dosyasının bilgisini döner (sayfa sayısı, vb)
    
    Args:
        pdf_file: PDF dosyası
    
    Returns:
        Dict: Dosya bilgileri
    """
    try:
        with pdfplumber.open(pdf_file) as pdf:
            return {
                "page_count": len(pdf.pages),
                "status": "success"
            }
    except:
        return {
            "page_count": 0,
            "status": "error"
        }