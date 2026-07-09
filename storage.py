import json
import os
import streamlit as st

# JSON Dosya Yolları Tanımı
HEATMAP_FILE = "heatmap.json"
SESSION_FILE = "reading_session.json"

def load_heatmap():
    """Uygulama başlarken yerel JSON dosyasından kelime geçmişini yükler."""
    if os.path.exists(HEATMAP_FILE):
        try:
            with open(HEATMAP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_heatmap(data):
    """Kelime geçmişi her güncellendiğinde yerel JSON dosyasına kaydeder."""
    try:
        with open(HEATMAP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving heatmap to local storage: {e}")

def load_reading_session():
    """Uygulama başlarken son üretilen okuma oturumunu yükler."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, dict) and "api_data" in content:
                    return content
                return None
        except Exception:
            return None
    return None

def save_reading_session(data):
    """Yeni bir metin üretildiğinde oturum verilerini JSON dosyasına kaydeder."""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving reading session to local storage: {e}")