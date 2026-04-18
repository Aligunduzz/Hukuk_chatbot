import streamlit as st

try:
    from .chatbot import ask_lawyer, classify_case, summarize_legal_text
    from .config import ALLOWED_PDF_TYPES, STREAMLIT_PAGE_CONFIG
    from .handler import extract_text_from_pdf, get_pdf_info
except ImportError:
    from chatbot import ask_lawyer, classify_case, summarize_legal_text
    from config import ALLOWED_PDF_TYPES, STREAMLIT_PAGE_CONFIG
    from handler import extract_text_from_pdf, get_pdf_info


def _init_session_state():
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("pdf_text", "")
    st.session_state.setdefault("pdf_name", "")


def _render_sidebar():
    with st.sidebar:
        st.title("Hukuk Chatbotu")
        st.write("Turk hukuku odakli soru-cevap, ozet ve dava turu siniflandirma araci.")
        st.caption("Calismasi icin `.env` dosyasi icinde `OPENAI_API_KEY` tanimli olmali.")

        uploaded_pdf = st.file_uploader(
            "PDF yukle",
            type=["pdf"],
            accept_multiple_files=False,
        )

        if uploaded_pdf is not None:
            pdf_text = extract_text_from_pdf(uploaded_pdf)
            if pdf_text.startswith("HATA:"):
                st.error(pdf_text)
            else:
                info = get_pdf_info(uploaded_pdf)
                st.session_state["pdf_text"] = pdf_text
                st.session_state["pdf_name"] = uploaded_pdf.name
                st.success(f"PDF hazir: {uploaded_pdf.name}")
                if info["status"] == "success":
                    st.caption(f"Sayfa sayisi: {info['page_count']}")

        if st.session_state["pdf_name"]:
            st.info(f"Aktif PDF: {st.session_state['pdf_name']}")
            if st.button("PDF baglamini temizle", use_container_width=True):
                st.session_state["pdf_text"] = ""
                st.session_state["pdf_name"] = ""
                st.rerun()

        if st.button("Sohbet gecmisini temizle", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()


def _render_chat_tab():
    st.subheader("Hukuki Soru Sor")
    st.write("Sorunuzu yazin. Yuklenmis bir PDF varsa cevapta referans baglami olarak kullanilir.")

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ornek: Kira sozlesmesinde tahliye sureci nasil ilerler?")
    if not prompt:
        return

    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history_without_latest = st.session_state["chat_history"][:-1]
    with st.chat_message("assistant"):
        with st.spinner("Yanit hazirlaniyor..."):
            answer = ask_lawyer(
                prompt,
                pdf_context=st.session_state["pdf_text"],
                conversation_history=history_without_latest,
            )
            st.markdown(answer)

    st.session_state["chat_history"].append({"role": "assistant", "content": answer})


def _render_summary_tab():
    st.subheader("Hukuki Metin Ozeti")
    default_text = st.session_state["pdf_text"] if st.session_state["pdf_text"] else ""
    text = st.text_area(
        "Ozetlenecek metin",
        value=default_text,
        height=280,
        placeholder="Bir dilekce, karar metni veya PDF icerigini buraya ekleyin.",
    )

    if st.button("Ozeti Olustur", use_container_width=True):
        with st.spinner("Ozet hazirlaniyor..."):
            summary = summarize_legal_text(text)
        st.markdown(summary)


def _render_classify_tab():
    st.subheader("Dava Turu Siniflandirma")
    case_text = st.text_area(
        "Dava aciklamasi",
        height=220,
        placeholder="Ornek: Isveren, kidem tazminatimi odemeden is akdimi feshetti.",
    )

    if st.button("Dava Turunu Belirle", use_container_width=True):
        with st.spinner("Siniflandiriliyor..."):
            result = classify_case(case_text)
        st.markdown(result)


def main():
    st.set_page_config(**STREAMLIT_PAGE_CONFIG)
    _init_session_state()
    _render_sidebar()

    st.title("Turk Hukuk Chatbotu")
    st.caption("PDF baglamli soru-cevap, hukuki metin ozeti ve dava turu tahmini")

    tab_chat, tab_summary, tab_classify = st.tabs(
        ["Soru-Cevap", "Metin Ozeti", "Dava Turu"]
    )

    with tab_chat:
        _render_chat_tab()

    with tab_summary:
        _render_summary_tab()

    with tab_classify:
        _render_classify_tab()


if __name__ == "__main__":
    main()
