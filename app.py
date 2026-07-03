import streamlit as st
from openai import OpenAI
import os

# 1. Sayfa Konfigürasyonu ve Temiz Görünüm
st.set_page_config(page_title="AI Language Learning Platform", page_icon="🌍", layout="centered")

# CSS ile Görsel Düzenleme
st.markdown("""
    <style>
    .main-title { text-align: center; color: #1E3A8A; font-weight: bold; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #6B7280; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌍 Universal AI Reading Platform</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Enhance your reading, vocabulary, and listening skills with Artificial Intelligence.</p>", unsafe_allow_html=True)
st.write("---")

# 2. Güvenli API Anahtarı Yönetimi
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.warning("⚠️ Please define 'OPENAI_API_KEY' in your system environment or Streamlit Secrets.")
    api_key = st.text_input("Or enter your API Key here for testing:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # 🌍 Dil Seçim Kutusu (En Üstte)
    target_language = st.selectbox(
        "Select the language you want to learn:",
        ["Nederlands", "English", "French", "Korean", "Spanish"]
    )
    st.write("")

    # 3. Form Elemanları (Yan Yana Sıralama)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        seviye = st.selectbox("CEFR Level", ["A1", "A2", "B1", "B2", "C1"])
    with col2:
        ton = st.selectbox("Text Tone", ["Casual", "Friendly", "Formal", "Academic"])
    with col3:
        kelime_sayisi = st.number_input("Word Count", min_value=30, max_value=500, value=100, step=10)
    with col4:
        konu = st.text_input("Topic", value="", placeholder="e.g., Daily Routine, Hobbies, Travel...")

    st.write("")
    
    # 📝 Egzersiz Türü Seçimleri (Abinin istediği zenginleştirilmiş yapı)
    st.markdown("### 🛠️ Select Exercise Types")
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    with ex_col1:
        show_tf = st.checkbox("True / False", value=True)
    with ex_col2:
        show_mc = st.checkbox("Reading Comprehension", value=True)
    with ex_col3:
        show_writing = st.checkbox("Open-ended Writing", value=False)

    # 4. Üretim Butonu
    st.write("")
    if st.button("Generate Text & Exercises 🚀", use_container_width=True):
        
        with st.spinner(f"Generating {target_language} text and exercises..."):
            try:
                # Egzersiz tercihlerine göre promptu dinamik olarak inşa ediyoruz
                exercise_instructions = []
                if show_tf:
                    exercise_instructions.append("- True/False Questions (3 statements based on the text)")
                if show_mc:
                    exercise_instructions.append("- Multiple Choice Questions (3 comprehension questions with A, B, C options)")
                if show_writing:
                    exercise_instructions.append("- Open-ended Writing Exercise (A prompt asking the user to write a short text related to the topic)")

                exercise_format = "\n".join(exercise_instructions)

                system_prompt = (
                    f"You are an experienced {target_language} language teacher.\n"
                    "Always generate output in this strict format:\n"
                    f"1. Reading Text in {target_language} (with a suitable title)\n"
                    "2. --- (Horizontal Rule)\n"
                    f"3. Vocabulary (Exactly 5 words with {target_language} -> Turkish translations)\n"
                    "4. --- (Horizontal Rule)\n"
                    f"5. Exercises (Include only the following requested types):\n"
                    f"{exercise_format}\n\n"
                    "Do not explain grammar. Do not provide the answers at the end."
                )
                
                user_prompt = f"Write a reading text in {target_language}. Level: {seviye}, Tone: {ton}, Length: ~{kelime_sayisi} words, Subject: {konu if konu else 'General topics suitable for this level'}."

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_completion_tokens=1500
                )
                
                generated_text = response.choices[0].message.content
                st.session_state['text_result'] = generated_text

            except Exception as e:
                st.error(f"OpenAI API Error: {e}")

    # 5. Sonuçların Ekrana Basılması ve Ek Özellikler
    if 'text_result' in st.session_state:
        st.write("---")
        st.markdown("### 📖 Generated Content")
        
        # İçeriği temiz bir kutu içinde gösteriyoruz
        st.info(st.session_state['text_result'])
        
        st.write("---")
        st.markdown("### 🔊 Listening Practice (Audio)")
        
        if st.button("Speak Text (TTS) 🎧"):
            with st.spinner("Generating audio file..."):
                try:
                    full_text = st.session_state['text_result']
                    text_to_speak = full_text.split("---")[0] # Sadece ana metni seslendir, egzersizleri okuma
                    
                    tts_response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=text_to_speak
                    )
                    
                    audio_data = tts_response.read()
                    st.audio(audio_data, format="audio/mp3")
                    
                except Exception as audio_err:
                    st.error(f"Audio Generation Error: {audio_err}")
                    
        # İndirme Butonu
        st.download_button(
            label="📄 Download Text (.txt)",
            data=st.session_state['text_result'],
            file_name=f"{target_language.lower()}_{seviye}.txt",
            mime="text/plain"
        )