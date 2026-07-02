import streamlit as st
from openai import OpenAI
import os

# 1. Sayfa Konfigürasyonu ve Temiz Görünüm
st.set_page_config(page_title="Nederlands Leerplatform", page_icon="🇳🇱", layout="centered")

# CSS ile Görsel Düzenleme (Görseldeki gibi temiz bir tasarım)
st.markdown("""
    <style>
    .main-title { text-align: center; color: #1E3A8A; font-weight: bold; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #6B7280; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🇳🇱 Nederlands AI Reading Platform</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Felemenkçe okuma, kelime ve dinleme becerilerinizi yapay zeka ile geliştirin.</p>", unsafe_allow_html=True)
st.write("---")

# 2. Güvenli API Anahtarı Yönetimi
# Streamlit Cloud'a yüklediğinde Secrets kısmına ekleyeceksin. 
# Yerelde test ederken bilgisayarının Çevre Değişkenlerine (Environment Variables) ekleyebilirsin.
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.warning("⚠️ Lütfen sistem ayarlarından veya Streamlit Secrets alanından 'OPENAI_API_KEY' tanımlayın.")
    # Testleri aksatmamak için geçici bir giriş kutusu:
    api_key = st.text_input("Veya test için API Key'inizi buraya girin:", type="password")

if api_key:
    # Güncel OpenAI İstemcisi Başlatma
    client = OpenAI(api_key=api_key)

    # 3. Form Elemanları (Yan Yana Sıralama)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        seviye = st.selectbox("CEFR Seviyesi", ["A1", "A2", "B1", "B2", "C1"])
    with col2:
        ton = st.selectbox("Metin Tonu", ["Casual", "Friendly", "Formal", "Academic"])
    with col3:
        kelime_sayisi = st.number_input("Kelime Sayısı", min_value=30, max_value=500, value=100, step=10)
    with col4:
        konu = st.text_input("Metin Konusu", value="Vrije tijd")

    # 4. Üretim Butonu
    st.write("")
    if st.button("Metni ve Soruları Oluştur 🚀", use_container_width=True):
        
        # ChatGPT'nin önerdiği şık Spinner yapısı
        with st.spinner("Dutch text and exercises are being generated..."):
            try:
                # Sistem ve Kullanıcı Promptlarının Ayrılması (Kararlılık için)
                system_prompt = (
                    "You are an experienced Dutch language teacher.\n"
                    "Always generate output in this strict format:\n"
                    "1. Reading Text (with a suitable title)\n"
                    "2. --- (Horizontal Rule)\n"
                    "3. Vocabulary (Exactly 5 words with Dutch -> Turkish translations)\n"
                    "4. --- (Horizontal Rule)\n"
                    "5. Multiple Choice Questions (3 questions with A, B, C options)\n\n"
                    "Do not explain grammar. Do not give the answers at the end."
                )
                
                user_prompt = f"Write a reading text in Dutch. Level: {seviye}, Tone: {ton}, Length: ~{kelime_sayisi} words, Subject: {konu}."

                # En güncel OpenAI SDK Kullanımı (gpt-4o-mini)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7, # Yaratıcılık dengesi
                    max_completion_tokens=1000
                )
                
                # Gelen metni hafızaya al
                generated_text = response.choices[0].message.content
                st.session_state['text_result'] = generated_text

            except Exception as e:
                st.error(f"OpenAI API Hatası: {e}")

    # 5. Sonuçların Ekrana Basılması ve Ek Özellikler
    if 'text_result' in st.session_state:
        st.write("---")
        st.markdown("### 📖 Üretilen İçerik")
        
        # Temiz bir kutu içinde Markdown çıktısı
        st.info(st.session_state['text_result'])
        
        st.write("---")
        st.markdown("### 🔊 Dinleme Pratiği (Audio)")
        
        # ChatGPT'nin bahsettiği OpenAI TTS (Seslendirme) Özelliği
        if st.button("Metni Seslendir (TTS) 🎧"):
            with st.spinner("Ses dosyası oluşturuluyor..."):
                try:
                    # Metnin sadece okuma kısmını seslendirmek mantıklı olduğundan ilk bölümü seçmeye çalışıyoruz
                    full_text = st.session_state['text_result']
                    text_to_speak = full_text.split("---")[0] # Sadece metni oku, soruları okuma
                    
                    tts_response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy", # Doğal bir ses tonu
                        input=text_to_speak
                    )
                    
                    # Sesi geçici olarak belleğe alıp Streamlit ses çalarında oynatıyoruz
                    audio_data = tts_response.read()
                    st.audio(audio_data, format="audio/mp3")
                    
                except Exception as audio_err:
                    st.error(f"Seslendirme oluşturulurken hata: {audio_err}")
                    
        # İndirme Seçeneği (Basit txt olarak indirme - PDF kütüphaneleriyle vakit kaybetmemek için en hızlısı)
        st.download_button(
            label="📄 Metni Bilgisayara İndir (.txt)",
            data=st.session_state['text_result'],
            file_name=f"dutch_{konu}_{seviye}.txt",
            mime="text/plain"
        )