import PyPDF2
import pdfplumber
from config import MAX_PDF_SIZE_MB, ERROR_MESSAGES

def extract_text_from_pdf(pdf_file):
    """
    PDF dosyasından metin çıkarır.
    
    Args:
        pdf_file: Streamlit UploadedFile nesnesi veya dosya yolu
    
    Returns:
        Çıkarılan metin (str)
    """
    try:
        # Dosya boyutunu kontrol et
        if hasattr(pdf_file, 'size'):
            file_size_mb = pdf_file.size / (1024 * 1024)
            if file_size_mb > MAX_PDF_SIZE_MB:
                return f"HATA: {ERROR_MESSAGES['pdf_too_large']}"
        
        # pdfplumber ile metin çıkar (daha iyi)
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        return text.strip()
    
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
    """
    Uzun metni parçalara böler (LLM için)
    
    Args:
        text: Bölünecek metin
        chunk_size: Her bir parçanın boyutu
        overlap: Parçalar arasında tekrarlanan kelime sayısı
    
    Returns:
        Metin parçaları listesi
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
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