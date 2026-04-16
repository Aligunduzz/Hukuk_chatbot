from functools import lru_cache
from pathlib import Path

try:
    from openai import AuthenticationError, OpenAI, RateLimitError
    OPENAI_IMPORT_ERROR = None
except ImportError as exc:
    OpenAI = None
    OPENAI_IMPORT_ERROR = exc

    class AuthenticationError(Exception):
        pass

    class RateLimitError(Exception):
        pass

from config import (
    CHAT_PROMPT_FILE,
    CLASSIFY_PROMPT_FILE,
    ERROR_MESSAGES,
    OPENAI_API_KEY,
    OPENAI_MAX_TOKENS,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    SUMMARIZE_PROMPT_FILE,
)

PDF_CONTEXT_CHAR_LIMIT = 3000
SUMMARIZE_MAX_TOKENS = 1000
CLASSIFY_MAX_TOKENS = 200
DEFAULT_TIMEOUT_SECONDS = 30
MODULE_DIR = Path(__file__).resolve().parent
DEFAULT_PROMPTS = {
    "chat": "You are a careful Turkish legal assistant. Explain clearly, avoid hallucinations, and state uncertainty.",
    "summarize": "Summarize the given text clearly and accurately in Turkish.",
    "classify": "Classify the legal case described by the user and explain the reasoning briefly in Turkish.",
}


def _resolve_prompt_path(prompt_file):
    prompt_path = Path(prompt_file)
    if prompt_path.is_absolute():
        return prompt_path
    return MODULE_DIR / prompt_path


@lru_cache(maxsize=16)
def load_prompt(prompt_file):
    """
    Prompt dosyasini yukler.

    Args:
        prompt_file: Prompt dosyasinin yolu

    Returns:
        Prompt icerigi (str)
    """
    try:
        return _resolve_prompt_path(prompt_file).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""
    except OSError:
        return ""


def _get_client():
    if OPENAI_IMPORT_ERROR is not None or OpenAI is None:
        raise RuntimeError("openai package is not installed.")
    return OpenAI(api_key=OPENAI_API_KEY, timeout=DEFAULT_TIMEOUT_SECONDS)


def _get_prompt(prompt_file, fallback_key):
    prompt = load_prompt(prompt_file)
    return prompt or DEFAULT_PROMPTS[fallback_key]


def _append_pdf_context(system_prompt, pdf_context):
    if not pdf_context:
        return system_prompt
    reference_text = pdf_context.strip()[:PDF_CONTEXT_CHAR_LIMIT]
    return f"{system_prompt}\n\nREFERANS METIN:\n{reference_text}"


def _sanitize_history(conversation_history):
    if not conversation_history:
        return []

    sanitized_messages = []
    for message in conversation_history:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")
        if role in {"system", "user", "assistant"} and isinstance(content, str) and content.strip():
            sanitized_messages.append({"role": role, "content": content.strip()})

    return sanitized_messages


def _extract_response_content(response):
    try:
        return response.choices[0].message.content.strip()
    except (AttributeError, IndexError, TypeError):
        raise ValueError("OpenAI response did not contain a valid message.")


def _create_chat_completion(messages, temperature, max_tokens):
    client = _get_client()
    return client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=messages,
    )


def _validate_user_text(text, empty_message):
    if not isinstance(text, str) or not text.strip():
        return empty_message
    return None


def ask_lawyer(user_question, pdf_context=""):
    """
    Kullanicinin hukuki sorusuna cevap verir.

    Args:
        user_question: Kullanicinin sorusu
        pdf_context: PDF'den cikarilan baglam (istege bagli)

    Returns:
        Chatbot'un cevabi (str)
    """
    if not OPENAI_API_KEY:
        return ERROR_MESSAGES["no_api_key"]

    validation_error = _validate_user_text(user_question, "❌ Lütfen geçerli bir soru girin.")
    if validation_error:
        return validation_error

    try:
        system_prompt = _append_pdf_context(_get_prompt(CHAT_PROMPT_FILE, "chat"), pdf_context)
        response = _create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question.strip()},
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
        )
        return _extract_response_content(response)
    except AuthenticationError:
        return "❌ OpenAI API anahtarı geçersiz"
    except RateLimitError:
        return "❌ API çok fazla istek aldı. Lütfen biraz bekleyin"
    except Exception as exc:
        return f"{ERROR_MESSAGES['api_error']} ({exc})"


def summarize_text(text):
    """
    Metni ozetler.

    Args:
        text: Ozetlenecek metin

    Returns:
        Ozet (str)
    """
    if not OPENAI_API_KEY:
        return ERROR_MESSAGES["no_api_key"]

    validation_error = _validate_user_text(text, "❌ Lütfen özetlenecek bir metin girin.")
    if validation_error:
        return validation_error

    try:
        response = _create_chat_completion(
            messages=[
                {"role": "system", "content": _get_prompt(SUMMARIZE_PROMPT_FILE, "summarize")},
                {"role": "user", "content": f"Lütfen bu metni özetle:\n\n{text.strip()}"},
            ],
            temperature=0.5,
            max_tokens=SUMMARIZE_MAX_TOKENS,
        )
        return _extract_response_content(response)
    except AuthenticationError:
        return "❌ OpenAI API anahtarı geçersiz"
    except RateLimitError:
        return "❌ API çok fazla istek aldı. Lütfen biraz bekleyin"
    except Exception as exc:
        return f"{ERROR_MESSAGES['api_error']} ({exc})"


def classify_case(case_description):
    """
    Dava turunu tahmin eder.

    Args:
        case_description: Dava aciklamasi

    Returns:
        Tahmini dava turu (str)
    """
    if not OPENAI_API_KEY:
        return ERROR_MESSAGES["no_api_key"]

    validation_error = _validate_user_text(case_description, "❌ Lütfen sınıflandırılacak bir açıklama girin.")
    if validation_error:
        return validation_error

    try:
        response = _create_chat_completion(
            messages=[
                {"role": "system", "content": _get_prompt(CLASSIFY_PROMPT_FILE, "classify")},
                {"role": "user", "content": f"Bu davayı sınıflandır:\n\n{case_description.strip()}"},
            ],
            temperature=0.3,
            max_tokens=CLASSIFY_MAX_TOKENS,
        )
        return _extract_response_content(response)
    except AuthenticationError:
        return "❌ OpenAI API anahtarı geçersiz"
    except RateLimitError:
        return "❌ API çok fazla istek aldı. Lütfen biraz bekleyin"
    except Exception as exc:
        return f"{ERROR_MESSAGES['api_error']} ({exc})"


def chat_with_context(user_question, pdf_context="", conversation_history=None):
    """
    Konusma gecmisi ile sohbet (multi-turn).

    Args:
        user_question: Kullanicinin sorusu
        pdf_context: PDF baglami
        conversation_history: Onceki mesajlarin listesi

    Returns:
        Cevap (str)
    """
    if not OPENAI_API_KEY:
        return ERROR_MESSAGES["no_api_key"]

    validation_error = _validate_user_text(user_question, "❌ Lütfen geçerli bir soru girin.")
    if validation_error:
        return validation_error

    try:
        system_prompt = _append_pdf_context(_get_prompt(CHAT_PROMPT_FILE, "chat"), pdf_context)
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(_sanitize_history(conversation_history))
        messages.append({"role": "user", "content": user_question.strip()})

        response = _create_chat_completion(
            messages=messages,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
        )
        return _extract_response_content(response)
    except AuthenticationError:
        return "❌ OpenAI API anahtarı geçersiz"
    except RateLimitError:
        return "❌ API çok fazla istek aldı. Lütfen biraz bekleyin"
    except Exception as exc:
        return f"{ERROR_MESSAGES['api_error']} ({exc})"
