import streamlit as st
from openai import OpenAI
import os
import json

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
st.markdown("<p class='subtitle'>Enhance your reading, vocabulary, and listening skills with Structured Data.</p>", unsafe_allow_html=True)
st.write("---")

# 2. Güvenli API Anahtarı Yönetimi
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.warning("⚠️ Please define 'OPENAI_API_KEY' in your system environment or Streamlit Secrets.")
    api_key = st.text_input("Or enter your API Key here for testing:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # 🌍 Dil Seçim Kutusu
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
    
    # 📝 Egzersiz Türü Seçimleri
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
        
        with st.spinner(f"Generating {target_language} data structure..."):
            try:
                # Kullanıcının seçtiği egzersizleri prompta ve JSON şemasına dikte ediyoruz
                exercise_requirements = []
                json_exercise_schema = {}
                
                if show_tf:
                    exercise_requirements.append("- true_false: 3 statements based on the text, each having 'statement' (string) and 'correct_answer' (boolean: true/false).")
                    json_exercise_schema["true_false"] = [{"statement": "example", "correct_answer": True}]
                if show_mc:
                    exercise_requirements.append("- multiple_choice: 3 questions, each having 'question' (string), 'options' (array of 3 strings), and 'correct_option' (string: A, B, or C).")
                    json_exercise_schema["multiple_choice"] = [{"question": "example", "options": ["A", "B", "C"], "correct_option": "B"}]
                if show_writing:
                    exercise_requirements.append("- open_ended: 1 writing prompt string asking the user to write a short paragraph related to the text.")
                    json_exercise_schema["open_ended"] = "example writing prompt prompt here"

                exercise_req_text = "\n".join(exercise_requirements)

                system_prompt = (
                    f"You are an expert {target_language} language teacher that outputs raw JSON data.\n"
                    "You must return a valid JSON object matching this strict schema exactly:\n"
                    "{\n"
                    "  \"title\": \"Title of the reading text\",\n"
                    f"  \"text\": \"The complete reading text generated in {target_language}\",\n"
                    "  \"vocabulary\": [\n"
                    f"    {{\"word\": \"word in {target_language}\", \"meaning\": \"Turkish meaning\", \"level\": \"CEFR level of word\"}}\n"
                    "  ],\n"
                    "  \"exercises\": " + json.dumps(json_exercise_schema) + "\n"
                    "}\n\n"
                    f"Generate exactly 5 vocabulary words from the text. "
                    f"Include only the requested exercises in the 'exercises' object:\n{exercise_req_text}"
                )
                
                user_prompt = f"Write a reading text in {target_language}. Level: {seviye}, Tone: {ton}, Length: ~{kelime_sayisi} words, Subject: {konu if konu else 'General topics suitable for this level'}."

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    # OpenAI'a zorla JSON formatında çıktı vermesini söylüyoruz:
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_completion_tokens=1500
                )
                
                # Gelen ham string'i Python sözlüğüne (dictionary) çevirip session_state'e kaydediyoruz
                raw_json_string = response.choices[0].message.content
                st.session_state['json_data'] = json.loads(raw_json_string)

            except Exception as e:
                st.error(f"OpenAI API Error: {e}")

    # 5. Sonuçların Ekrana Basılması (Sprint 1 Kilometre Taşı)
    if 'json_data' in st.session_state:
        data = st.session_state['json_data']
        
        st.write("---")
        
        # JSON'dan gelen Başlık ve Metin
        st.subheader(f"📖 {data.get('title', 'Reading Text')}")
        st.write(data.get('text', ''))
        
        st.write("---")
        
        # JSON'dan gelen Kelimeler
        st.subheader("🔑 Vocabulary")
        for item in data.get('vocabulary', []):
            st.markdown(f"**{item.get('word')}** ({item.get('level', 'N/A')}) $\rightarrow$ {item.get('meaning')}")
            
        st.write("---")
        
        # JSON'dan gelen Egzersiz Yapısı (Geliştirici modu için ham veri çıktısı dahil)
        st.subheader("🛠️ Exercises (Loaded from JSON)")
        exercises = data.get('exercises', {})
        
        if "true_false" in exercises:
            st.markdown("#### True / False Statements")
            for tf in exercises["true_false"]:
                st.write(f"- {tf.get('statement')}")
                
        if "multiple_choice" in exercises:
            st.markdown("#### Multiple Choice Questions")
            for mc in exercises["multiple_choice"]:
                st.write(f"**Question:** {mc.get('question')}")
                st.write(f"Options: {', '.join(mc.get('options', []))}")
                
        if "open_ended" in exercises:
            st.markdown("#### Open-ended Writing Prompt")
            st.write(exercises["open_ended"])
            
        st.write("---")
        st.markdown("### 🔊 Listening Practice (Audio)")
        
        if st.button("Speak Text (TTS) 🎧"):
            with st.spinner("Generating audio file..."):
                try:
                    text_to_speak = data.get('text', '')
                    tts_response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=text_to_speak
                    )
                    audio_data = tts_response.read()
                    st.audio(audio_data, format="audio/mp3")
                except Exception as audio_err:
                    st.error(f"Audio Generation Error: {audio_err}")