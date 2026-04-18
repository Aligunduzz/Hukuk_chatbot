import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if load_dotenv is not None:
    load_dotenv(dotenv_path=ENV_FILE if ENV_FILE.exists() else None)

# OpenAI ayarlari
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# Prompt dosyalari
PROMPTS_DIR = "prompts"
CHAT_PROMPT_FILE = str(Path(PROMPTS_DIR) / "chat.txt")
SUMMARIZE_PROMPT_FILE = str(Path(PROMPTS_DIR) / "summarize.txt")
CLASSIFY_PROMPT_FILE = str(Path(PROMPTS_DIR) / "classify.txt")

# PDF ayarlari
MAX_PDF_SIZE_MB = 10
ALLOWED_PDF_TYPES = ["application/pdf"]

# Streamlit ayarlari
STREAMLIT_PAGE_CONFIG = {
    "page_title": "Turk Hukuk Chatbotu",
    "page_icon": "⚖️",
    "layout": "wide",
}

# Hata mesajlari
ERROR_MESSAGES = {
    "no_api_key": "❌ OpenAI API anahtari bulunamadi. .env dosyasini kontrol edin.",
    "pdf_too_large": "❌ PDF dosyasi cok buyuk (max 10MB).",
    "invalid_pdf": "❌ Gecerli bir PDF dosyasi yukleyin.",
    "api_error": "❌ OpenAI API hatasi. Lutfen tekrar deneyin.",
}
