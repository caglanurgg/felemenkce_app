import json
import os
import re
from datetime import datetime
import streamlit as st
from openai import OpenAI

# 1. Sayfa Konfigürasyonu ve Temiz Görünüm
st.set_page_config(page_title="AI Language Learning Platform", page_icon="🌏", layout="centered")

# Üst Barı ve Sürüm Kontrol Linklerini Gizleyen CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    
    /* Kelime Vurgulama CSS Sınıfları */
    .highlight-green {
        background-color: rgba(40, 167, 69, 0.25);
        border-bottom: 2px solid #28a745;
        padding: 0 4px;
        border-radius: 4px;
    }
    .highlight-yellow {
        background-color: rgba(255, 193, 7, 0.3);
        border-bottom: 2px solid #ffc107;
        padding: 0 4px;
        border-radius: 4px;
    }
    .highlight-red {
        background-color: rgba(220, 53, 69, 0.25);
        border-bottom: 2px solid #dc3545;
        padding: 0 4px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# F5 Kaybını Önlemek İçin Gelişmiş Hafıza Yapılandırması
if 'heatmap_vocab' not in st.session_state:
    st.session_state['heatmap_vocab'] = {}  # Örn: {"transformative": "🔴 New to me", "provoke": "🟡 I've seen this"}

# CSS ile Görsel Düzenleme
st.markdown("""
<style>
    .main-title { text-align: center; color: #1E3A8A; font-weight: bold; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #6B7280; font-weight: bold; margin-bottom: 25px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌏 Universal AI Reading Platform</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Adaptive Learning Platform with Persistent Reading Heatmap.</p>", unsafe_allow_html=True)
st.write("---")

# 2. Güvenli API Anahtarı Yönetimi
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.warning("⚠️ Please define 'OPENAI_API_KEY' in your system environment or Streamlit Secrets.")
    api_key = st.text_input("Or enter your API Key here for testing:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    
    # Dil Seçim Kutusu
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
    
    # Egzersiz Türü Seçimleri
    st.markdown("### 🛠️ Select Exercise Types")
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    with ex_col1:
        show_tf = st.checkbox("True / False", value=True)
    with ex_col2:
        show_mc = st.checkbox("Reading Comprehension", value=True)
    with ex_col3:
        show_writing = st.checkbox("Open-ended Writing", value=False)
        
    st.write("")
    
    # 4. Üretim Butonu
    if st.button("Generate Text & Exercises 🚀", use_container_width=True):
        with st.spinner(f"Generating {target_language} data structure..."):
            try:
                exercise_requirements = []
                json_exercise_schema = {}
                
                if show_tf:
                    exercise_requirements.append("- true_false: 3 statements based on the text. Each statement MUST have 'statement' (string) and 'correct_answer' (boolean)")
                    json_exercise_schema["true_false"] = [{"statement": "example statement", "correct_answer": True}]
                if show_mc:
                    exercise_requirements.append("- multiple_choice: 3 questions. Each question MUST have 'question' (string), 'options' (array of strings), and 'correct_answer' (string matching one option)")
                    json_exercise_schema["multiple_choice"] = [{"question": "example question", "options": ["Option A", "Option B"], "correct_answer": "Option A"}]
                if show_writing:
                    exercise_requirements.append("- open_ended: 1 writing prompt string asking the user to write a short paragraph.")
                    json_exercise_schema["open_ended"] = "example writing prompt here"
                    
                exercise_req_text = "\n".join(exercise_requirements)
                
                # Hafızadaki zor ve orta kelimeleri (Yani "New to me" ve "I've seen this" olanları) gönderiyoruz
                memory_instruction = ""
                if st.session_state['heatmap_vocab']:
                    review_words = [w for w, status in st.session_state['heatmap_vocab'].items() if "New to me" in status or "I've seen this" in status]
                    if review_words:
                        memory_instruction = f"\nCRITICAL: The user is struggling with or studying these specific words: {review_words}. You MUST include them naturally in the text if appropriate."
                
                system_prompt = (
                    f"You are an expert {target_language} language teacher that outputs raw JSON data.\n"
                    "You must return a valid JSON object matching this strict schema exactly:\n"
                    "{\n"
                    "  \"title\": \"Title of the reading text\",\n"
                    f"  \"text\": \"The complete reading text generated in {target_language}\",\n"
                    "  \"vocabulary\": [\n"
                    "     {\"word\": \"word\", \"meaning\": \"Turkish meaning\", \"level\": \"CEFR level of word\", \"pronunciation\": \"IPA\", \"example\": \"sentence\"}\n"
                    "  ],\n"
                    "  \"exercises\": " + json.dumps(json_exercise_schema) + "\n"
                    "}\n\n"
                    "Generate exactly 5 vocabulary words from the text. "
                    f"Include only the requested exercises in the 'exercises' object:\n{exercise_req_text}"
                    f"{memory_instruction}"
                )
                
                user_prompt = f"Write a reading text in {target_language}. Level: {seviye}, Tone: {ton}, Length: ~{kelime_sayisi} words, Subject: {konu}"
                
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
        reading_text = data.get("text", "")
        
        # Heatmap'te kayıtlı kelimeleri metin içinde dinamik vurgula (Öncelik sıralı)
        if st.session_state['heatmap_vocab']:
            sorted_words = sorted(st.session_state['heatmap_vocab'].keys(), key=len, reverse=True)
            for word in sorted_words:
                status = st.session_state['heatmap_vocab'][word]
                if "I know this" in status:
                    color_class = "highlight-green"
                elif "I've seen this" in status:
                    color_class = "highlight-yellow"
                else:
                    color_class = "highlight-red"
                
                pattern = rf"\b({re.escape(word)})\b"
                reading_text = re.sub(pattern, f'<span class="{color_class}">\\1</span>', reading_text, flags=re.IGNORECASE)
                
        st.markdown(f"<div style='line-height:1.8; font-size:1.1rem;'>{reading_text}</div>", unsafe_allow_html=True)
        st.write("---")
        
        # Smart Reading Assistant & Heatmap Tool
        st.subheader("✨ Smart Reading Assistant & Heatmap Tool")
        st.markdown("*Click a word below to explore it and log your familiarity level:*")
        
        for idx, item in enumerate(data.get('vocabulary', [])):
            word_key = item.get('word')
            status_emoji = ""
            
            if word_key in st.session_state['heatmap_vocab']:
                current_status = st.session_state['heatmap_vocab'][word_key]
                if "I know this" in current_status:
                    status_emoji = "🟢 "
                elif "I've seen this" in current_status:
                    status_emoji = "🟡 "
                elif "New to me" in current_status:
                    status_emoji = "🔴 "
                    
            with st.expander(f"{status_emoji}🔽 {word_key} ({item.get('level', 'N/A')})"):
                st.write(f"**🇹🇷 Meaning:** {item.get('meaning')}")
                st.write(f"**🔊 Pronunciation:** *{item.get('pronunciation', 'N/A')}*")
                st.write(f"**📝 Example:** {item.get('example', 'No example provided.')}")
                
                st.markdown("**How familiar is this word to you?**")
                v_col1, v_col2, v_col3 = st.columns(3)
                
                with v_col1:
                    if st.button("🟢 I know this", key=f"know_{idx}"):
                        st.session_state['heatmap_vocab'][word_key] = "🟢 I know this"
                        st.rerun()
                with v_col2:
                    if st.button("🟡 I've seen this", key=f"seen_{idx}"):
                        st.session_state['heatmap_vocab'][word_key] = "🟡 I've seen this"
                        st.rerun()
                with v_col3:
                    if st.button("🔴 New to me", key=f"new_{idx}"):
                        st.session_state['heatmap_vocab'][word_key] = "🔴 New to me"
                        st.rerun()
                        
        st.write("---")
        
        # İnteraktif Egzersiz Yapısı
        st.subheader("✍️ Interactive Exercises")
        exercises = data.get('exercises', {})
        
        with st.form("exercise_form"):
            user_tf_answers = {}
            user_mc_answers = {}
            user_open_text = ""
            
            if "true_false" in exercises and exercises["true_false"]:
                st.markdown("### 📄 True / False Statements")
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
            
            if "true_false" in exercises and exercises["true_false"]:
                for i, tf in enumerate(exercises["true_false"]):
                    correct = tf.get('correct_answer')
                    ans = user_tf_answers[i]
                    if ans != "Not Answered":
                        user_bool = True if ans == "True" else False
                        st.write(f"Statement {i+1}: {'✅ Correct!' if user_bool == correct else '❌ Incorrect'}")
                        
            if "multiple_choice" in exercises and exercises["multiple_choice"]:
                for i, mc in enumerate(exercises["multiple_choice"]):
                    correct_opt = mc.get('correct_answer')
                    ans = user_mc_answers[i]
                    if ans != "Not Answered":
                        st.write(f"Question {i+1}: {'✅ Correct!' if ans.startswith(correct_opt) or correct_opt in ans else '❌ Incorrect'}")

    # Yan Panel (Sidebar): Canlı Isı Haritası ve Hafıza İstatistikleri
    if st.session_state['heatmap_vocab']:
        st.sidebar.markdown("### 📊 AI Memory Dashboard")
        
        all_words = st.session_state['heatmap_vocab']
        know_count = sum(1 for status in all_words.values() if "I know this" in status)
        seen_count = sum(1 for status in all_words.values() if "I've seen this" in status)
        new_count = sum(1 for status in all_words.values() if "New to me" in status)
        
        st.sidebar.write(f"🟢 **I know this:** {know_count}")
        st.sidebar.write(f"🟡 **I've seen this:** {seen_count}")
        st.sidebar.write(f"🔴 **New to me:** {new_count}")
        st.sidebar.write("---")
        
        st.sidebar.markdown("#### 🗺️ Registered Vocabulary Heatmap")
        for word, status in all_words.items():
            if "I know this" in status:
                st.sidebar.write(f"🟢 **{word}**")
            elif "I've seen this" in status:
                st.sidebar.write(f"🟡 **{word}**")
            else:
                st.sidebar.write(f"🔴 **{word}**")
                
        if st.sidebar.button("🗑️ Reset All Progress"):
            st.session_state['heatmap_vocab'] = {}
            st.rerun()