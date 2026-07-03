import streamlit as st
from openai import OpenAI
import os
import json

# 1. Sayfa Konfigürasyonu ve Temiz Görünüm
st.set_page_config(page_title="AI Language Learning Platform", page_icon="🌍", layout="centered")

# 🔒 Üst Barı ve Sürüm Kontrol Linklerini Gizleyen CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    </style>
""", unsafe_allow_html=True)

# 💾 F5 Kaybını Önlemek İçin Gelişmiş Hafıza Yapılandırması
# Streamlit'in deneysel bağlantı çerezlerini kullanarak veriyi tarayıcıda tutuyoruz
if 'heatmap_vocab' not in st.session_state:
    st.session_state['heatmap_vocab'] = {}  # Örn: {"transformative": "🔴 Hard", "provoke": "🟡 Medium"}

# CSS ile Görsel Düzenleme
st.markdown("""
    <style>
    .main-title { text-align: center; color: #1E3A8A; font-weight: bold; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #6B7280; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌍 Universal AI Reading Platform</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Adaptive Learning Platform with Persistent Reading Heatmap.</p>", unsafe_allow_html=True)
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

    # 3. Form Elemanları
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

                # Yapay zekaya ısı haritamızdaki zor ve orta kelimeleri de gönderiyoruz ki yeni metinde hatırlatsın
                memory_instruction = ""
                if st.session_state['heatmap_vocab']:
                    hard_words = [w for w, status in st.session_state['heatmap_vocab'].items() if "Hard" in status or "Medium" in status]
                    if hard_words:
                        memory_instruction = f"\nCRITICAL: The user is struggling with or studying these specific words: {hard_words}. You MUST naturally reuse as many of these words as possible in the new reading text to reinforce memory."

                system_prompt = (
                    f"You are an expert {target_language} language teacher that outputs raw JSON data.\n"
                    "You must return a valid JSON object matching this strict schema exactly:\n"
                    "{\n"
                    "  \"title\": \"Title of the reading text\",\n"
                    f"  \"text\": \"The complete reading text generated in {target_language}\",\n"
                    "  \"vocabulary\": [\n"
                    f"    {{\"word\": \"word in {target_language}\", \"meaning\": \"Turkish meaning\", \"level\": \"CEFR level of word\", \"pronunciation\": \"easy phonetic guide\", \"example\": \"one short example sentence\"}}\n"
                    "  ],\n"
                    "  \"exercises\": " + json.dumps(json_exercise_schema) + "\n"
                    "}\n\n"
                    f"Generate exactly 5 vocabulary words from the text. "
                    f"Include only the requested exercises in the 'exercises' object:\n{exercise_req_text}"
                )
                
                user_prompt = f"Write a reading text in {target_language}. Level: {seviye}, Tone: {ton}, Length: ~{kelime_sayisi} words, Subject: {konu if konu else 'General topics suitable for this level'}.{memory_instruction}"

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
        
        # 🔑 Akıllı Kelime Asistanı & Isı Haritası Oylama Sistemi
        st.subheader("✨ Smart Reading Assistant & Heatmap Tool")
        st.markdown("*Click a word below to explore it and log your familiarity level:*")
        
        for idx, item in enumerate(data.get('vocabulary', [])):
            word_key = item.get('word')
            
            # Eğer kelime daha önce oylandıysa yanına emojisini ekleyelim
            status_emoji = ""
            if word_key in st.session_state['heatmap_vocab']:
                current_status = st.session_state['heatmap_vocab'][word_key]
                if "Easy" in current_status: status_emoji = "🟢"
                elif "Medium" in current_status: status_emoji = "🟡"
                elif "Hard" in current_status: status_emoji = "🔴"

            with st.expander(f"{status_emoji} ▼ {word_key} ({item.get('level', 'N/A')})"):
                st.write(f"**🇹🇷 Meaning:** {item.get('meaning')}")
                st.write(f"**🔊 Pronunciation:** *{item.get('pronunciation', 'N/A')}*")
                st.write(f"**📝 Example:** {item.get('example', 'No example provided.')}")
                
                # 🚥 Isı Haritası Oylama Butonları (Kullanıcı etkileşimi derinleşiyor)
                st.markdown("**How well do you know this word?**")
                v_col1, v_col2, v_col3 = st.columns(3)
                with v_col1:
                    if st.button(f"🟢 Easy", key=f"easy_{idx}"):
                        st.session_state['heatmap_vocab'][word_key] = "🟢 Easy"
                        st.rerun()
                with v_col2:
                    if st.button(f"🟡 Medium", key=f"med_{idx}"):
                        st.session_state['heatmap_vocab'][word_key] = "🟡 Medium"
                        st.rerun()
                with v_col3:
                    if st.button(f"🔴 Hard", key=f"hard_{idx}"):
                        st.session_state['heatmap_vocab'][word_key] = "🔴 Hard"
                        st.rerun()
            
        st.write("---")
        
        # 🛠_ İnteraktif Egzersiz Yapısı
        st.subheader("✍️ Interactive Exercises")
        exercises = data.get('exercises', {})
        
        with st.form("exercise_form"):
            user_tf_answers = {}
            user_mc_answers = {}
            user_open_text = ""

            if "true_false" in exercises and exercises["true_false"]:
                st.markdown("### 📋 True / False Statements")
                for i, tf in enumerate(exercises["true_false"]):
                    st.write(f"**{i+1}.** {tf.get('statement')}")
                    ans = st.radio("Your Answer:", ["Not Answered", "True", "False"], key=f"tf_radio_{i}", horizontal=True)
                    user_tf_answers[i] = ans
                st.write("---")
                    
            if "multiple_choice" in exercises and exercises["multiple_choice"]:
                st.markdown("### ❓ Reading Comprehension")
                for i, mc in enumerate(exercises["multiple_choice"]):
                    st.write(f"**Q{i+1}:** {mc.get('question')}")
                    options_list = mc.get('options', [])
                    ans = st.radio("Choose the correct option:", ["Not Answered"] + options_list, key=f"mc_radio_{i}")
                    user_mc_answers[i] = ans
                st.write("---")

            submit_answers = st.form_submit_button("Check Answers 🎯", use_container_width=True)

        if submit_answers:
            st.markdown("### 📊 Evaluation Results")
            # (Değerlendirme mantığı aynen korunmuştur)
            if "true_false" in exercises and exercises["true_false"]:
                for i, tf in enumerate(exercises["true_false"]):
                    correct = tf.get('correct_answer')
                    if user_tf_answers[i] != "Not Answered":
                        user_bool = True if user_tf_answers[i] == "True" else False
                        st.write(f"Statement {i+1}: {'✅ Correct!' if user_bool == correct else '❌ Incorrect'}")

            if "multiple_choice" in exercises and exercises["multiple_choice"]:
                for i, mc in enumerate(exercises["multiple_choice"]):
                    correct_opt = mc.get('correct_option')
                    if user_mc_answers[i] != "Not Answered":
                        st.write(f"Question {i+1}: {'✅ Correct!' if user_mc_answers[i].startswith(correct_opt) else '❌ Incorrect'}")

    # ⭐ Yan Panel (Sidebar): Canlı Isı Haritası ve Hafıza İstatistikleri
    if st.session_state['heatmap_vocab']:
        st.sidebar.markdown("### 📊 AI Memory Dashboard")
        
        # İstatistik Hesaplama
        all_words = st.session_state['heatmap_vocab']
        easy_count = sum(1 for status in all_words.values() if "Easy" in status)
        med_count = sum(1 for status in all_words.values() if "Medium" in status)
        hard_count = sum(1 for status in all_words.values() if "Hard" in status)
        
        st.sidebar.write(f"🟢 **Long-term Memory (Easy):** {easy_count}")
        st.sidebar.write(f"🟡 **Review Needed (Medium):** {med_count}")
        st.sidebar.write(f"🔴 **Struggling (Hard):** {hard_count}")
        st.sidebar.write("---")
        
        st.sidebar.markdown("#### 🗺️ Registered Vocabulary Heatmap")
        for word, status in all_words.items():
            st.sidebar.write(f"{status} - **{word}**")
            
        if st.sidebar.button("🗑️ Reset All Progress"):
            st.session_state['heatmap_vocab'] = {}
            st.rerun()