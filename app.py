import streamlit as st
from openai import OpenAI
import os
import json

# 1. Sayfa Konfigürasyonu ve Temiz Görünüm
st.set_page_config(page_title="AI Language Learning Platform", page_icon="🌍", layout="centered")

st.markdown("""
    <style>
    /* GitHub simgesini, Share butonunu ve üst bar elemanlarını tamamen gizler */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    </style>
""", unsafe_allow_html=True)

# Kaydedilen kelimeler için session_state (hafıza) başlatma
if 'saved_words' not in st.session_state:
    st.session_state['saved_words'] = []

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
                    exercise_requirements.append("- true_false: 3 statements based on the text. Each statement MUST have 'statement' (string) and 'correct_answer' (boolean: true or false).")
                    json_exercise_schema["true_false"] = [{"statement": "example statement", "correct_answer": True}]
                if show_mc:
                    exercise_requirements.append("- multiple_choice: 3 questions. Each question MUST have 'question' (string), 'options' (array of 3 short strings), and 'correct_option' (string: exactly 'A', 'B', or 'C').")
                    json_exercise_schema["multiple_choice"] = [{"question": "example question", "options": ["Option A", "Option B", "Option C"], "correct_option": "B"}]
                if show_writing:
                    exercise_requirements.append("- open_ended: 1 writing prompt string asking the user to write a short paragraph related to the text.")
                    json_exercise_schema["open_ended"] = "example writing prompt here"

                exercise_req_text = "\n".join(exercise_requirements)

                system_prompt = (
                    f"You are an expert {target_language} language teacher that outputs raw JSON data.\n"
                    "You must return a valid JSON object matching this strict schema exactly:\n"
                    "{\n"
                    "  \"title\": \"Title of the reading text\",\n"
                    f"  \"text\": \"The complete reading text generated in {target_language}\",\n"
                    "  \"vocabulary\": [\n"
                    f"    {{\"word\": \"word in {target_language}\", \"meaning\": \"Turkish meaning\", \"level\": \"CEFR level of word\", \"pronunciation\": \"easy phonetic guide/spelling for pronunciation\", \"example\": \"one short example sentence using this word in {target_language}\"}}\n"
                    "  ],\n"
                    "  \"exercises\": " + json.dumps(json_exercise_schema) + "\n"
                    "}\n\n"
                    f"Generate exactly 5 vocabulary words from the text. "
                    f"Include only the requested exercises in the 'exercises' object:\n{exercise_req_text}"
                )
                
                user_prompt = f"Write a reading text in {target_language}. Level: {seviye}, Tone: {ton}, Length: ~{kelime_sayisi} words, Subject: {konu if konu else 'General topics suitable for this level'}."

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_completion_tokens=1500
                )
                
                raw_json_string = response.choices[0].message.content
                st.session_state['json_data'] = json.loads(raw_json_string)
                # Yeni metin üretildiğinde eski kullanıcı cevaplarını temizle
                if 'user_answers' in st.session_state:
                    del st.session_state['user_answers']

            except Exception as e:
                st.error(f"OpenAI API Error: {e}")

    # 5. Sonuçların Ekrana Basılması
    if 'json_data' in st.session_state:
        data = st.session_state['json_data']
        
        st.write("---")
        
        # Başlık ve Metin
        st.subheader(f"📖 {data.get('title', 'Reading Text')}")
        st.write(data.get('text', ''))
        
        st.write("---")
        
        # 🔑 Akıllı Kelime Asistanı
        st.subheader("✨ Smart Reading Assistant")
        st.markdown("*Click a word below to explore it and test your memory:*")
        
        for idx, item in enumerate(data.get('vocabulary', [])):
            word_key = item.get('word')
            with st.expander(f"▼ {word_key} ({item.get('level', 'N/A')})"):
                st.write(f"**🇹🇷 Meaning:** {item.get('meaning')}")
                st.write(f"**🔊 Pronunciation:** *{item.get('pronunciation', 'N/A')}*")
                st.write(f"**📝 Example:** {item.get('example', 'No example provided.')}")
                
                if word_key not in st.session_state['saved_words']:
                    if st.button(f"⭐ Save '{word_key}'", key=f"save_{idx}"):
                        st.session_state['saved_words'].append(word_key)
                        st.rerun()
                else:
                    st.success(f"✅ '{word_key}' is saved to your vocabulary pool!")
            
        st.write("---")
        
        # 🛠️ İnteraktif Egzersiz Yapısı (Kullanıcının Seçim Yapabileceği Alan)
        st.subheader("✍️ Interactive Exercises")
        exercises = data.get('exercises', {})
        
        # Form kullanarak sayfayı her tıklamada yukarı atmaktan kurtarıyoruz
        with St.form("exercise_form"):
            user_tf_answers = {}
            user_mc_answers = {}
            user_open_text = ""

            if "true_false" in exercises:
                st.markdown("### 📋 True / False Statements")
                for i, tf in enumerate(exercises["true_false"]):
                    st.write(f"**{i+1}.** {tf.get('statement')}")
                    # Radyo butonları ile seçim yaptırıyoruz
                    ans = st.radio("Your Answer:", ["Not Answered", "True", "False"], key=f"tf_radio_{i}", horizontal=True)
                    user_tf_answers[i] = ans
                st.write("---")
                    
            if "multiple_choice" in exercises:
                st.markdown("### ❓ Reading Comprehension")
                for i, mc in enumerate(exercises["multiple_choice"]):
                    st.write(f"**Q{i+1}:** {mc.get('question')}")
                    # Seçenekleri yan yana veya alt alta şıkça gösteriyoruz
                    options_list = mc.get('options', [])
                    ans = st.radio("Choose the correct option:", ["Not Answered"] + options_list, key=f"mc_radio_{i}")
                    user_mc_answers[i] = ans
                st.write("---")

            if "open_ended" in exercises:
                st.markdown("### 📝 Open-ended Writing Prompt")
                st.write(exercises["open_ended"])
                user_open_text = st.text_area("Write your response here:", placeholder="Type your answer in the target language...", key="open_text_area")
                st.write("---")

            # Cevapları Kontrol Et Butonu
            submit_answers = st.form_submit_button("Check Answers 🎯", use_container_width=True)

        # Butona basıldığında sonuç değerlendirmesini ekrana basıyoruz
        if submit_answers:
            st.markdown("### 📊 Evaluation Results")
            
            if "true_false" in exercises:
                st.markdown("#### True / False Evaluation:")
                for i, tf in enumerate(exercises["true_false"]):
                    correct = tf.get('correct_answer') 
                    user_ans_str = user_tf_answers[i]
                    
                    if user_ans_str == "Not Answered":
                        st.warning(f"Statement {i+1}: Not Answered 🟡")
                    else:
                        user_bool = True if user_ans_str == "True" else False
                        if user_bool == correct:
                            st.success(f"Statement {i+1}: Correct! ✅")
                        else:
                            st.error(f"Statement {i+1}: Incorrect ❌ (Correct Answer: {correct})")

            if "multiple_choice" in exercises:
                st.markdown("#### Multiple Choice Evaluation:")
                for i, mc in enumerate(exercises["multiple_choice"]):
                    correct_opt = mc.get('correct_option') 
                    user_ans_str = user_mc_answers[i]
                    
                    if user_ans_str == "Not Answered":
                        st.warning(f"Question {i+1}: Not Answered 🟡")
                    else:
                        if user_ans_str.startswith("A") and correct_opt == "A":
                            st.success(f"Question {i+1}: Correct! ✅")
                        elif user_ans_str.startswith("B") and correct_opt == "B":
                            st.success(f"Question {i+1}: Correct! ✅")
                        elif user_ans_str.startswith("C") and correct_opt == "C":
                            st.success(f"Question {i+1}: Correct! ✅")
                        else:
                            st.error(f"Question {i+1}: Incorrect ❌ (Correct Option: {correct_opt})")

            if "open_ended" in exercises and user_open_text:
                st.info("📝 Your open-ended writing response has been saved. Great effort practicing!")

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

    # ⭐ Yan Panel (Sidebar): Kaydedilen Kelimeler Listesi
    if st.session_state['saved_words']:
        st.sidebar.markdown("### ⭐ Saved Words Pool")
        for saved_w in st.session_state['saved_words']:
            st.sidebar.write(f"- {saved_w}")
        
        if st.sidebar.button("🗑️ Clear Saved Words"):
            st.session_state['saved_words'] = []
            st.rerun()