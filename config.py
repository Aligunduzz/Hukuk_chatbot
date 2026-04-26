import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "calistirma.env"
PROMPTS_DIR = BASE_DIR / "prompts"

if load_dotenv is not None:
    load_dotenv(dotenv_path=ENV_FILE if ENV_FILE.exists() else None)

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1200"))

# Prompt files
CHAT_PROMPT_FILE = str(PROMPTS_DIR / "chat.txt")
SUMMARIZE_PROMPT_FILE = str(PROMPTS_DIR / "summarize.txt")
CLASSIFY_PROMPT_FILE = str(PROMPTS_DIR / "classify.txt")
LABOR_LAW_FILE = str(PROMPTS_DIR / "promptslabor_law.txt")

# PDF settings
MAX_PDF_SIZE_MB = 10
ALLOWED_PDF_TYPES = ["pdf"]

# Streamlit settings
STREAMLIT_PAGE_CONFIG = {
    "page_title": "Turk Hukuk Chatbotu",
    "page_icon": "T",
    "layout": "wide",
}

# Legal areas
LEGAL_AREAS = [
    "Genel Hukuk",
    "Is Hukuku",
    "Ceza Hukuku",
    "Borclar Hukuku",
    "Aile Hukuku",
    "Idare Hukuku",
]

# Error messages
ERROR_MESSAGES = {
    "no_api_key": "OpenAI API anahtari bulunamadi. calistirma.env dosyasini kontrol edin.",
    "pdf_too_large": "PDF dosyasi cok buyuk. Maksimum boyut 10 MB.",
    "invalid_pdf": "Gecerli bir PDF dosyasi yukleyin.",
    "api_error": "OpenAI API hatasi. Lutfen tekrar deneyin.",
}
