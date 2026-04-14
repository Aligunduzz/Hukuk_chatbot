import os
from dotenv import load_dotenv

# .env dosyasından değişkenleri yükle
load_dotenv()

# ===== OPENAI AYARLARI =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"  # gpt-4 veya gpt-3.5-turbo
OPENAI_TEMPERATURE = 0.7  # Yaratıcılık (0-1)
OPENAI_MAX_TOKENS = 2000  # Maksimum cevap uzunluğu

# ===== PROMPT DOSYALARI =====
PROMPTS_DIR = "prompts"
CHAT_PROMPT_FILE = os.path.join(PROMPTS_DIR, "chat.txt")
SUMMARIZE_PROMPT_FILE = os.path.join(PROMPTS_DIR, "summarize.txt")
CLASSIFY_PROMPT_FILE = os.path.join(PROMPTS_DIR, "classify.txt")

# ===== PDF AYARLARI =====
MAX_PDF_SIZE_MB = 10  # Maksimum PDF boyutu
ALLOWED_PDF_TYPES = ["application/pdf"]

# ===== STREAMLIT AYARLARI =====
STREAMLIT_PAGE_CONFIG = {
    "page_title": "🏛️ Türk Hukuk Chatbotu",
    "page_icon": "⚖️",
    "layout": "wide",
}

# ===== HATA MESAJLARI =====
ERROR_MESSAGES = {
    "no_api_key": "❌ OpenAI API anahtarı bulunamadı. .env dosyasını kontrol edin.",
    "pdf_too_large": "❌ PDF dosyası çok büyük (max 10MB)",
    "invalid_pdf": "❌ Geçerli bir PDF dosyası yükleyiniz.",
    "api_error": "❌ OpenAI API hatası. Lütfen tekrar deneyin.",
}