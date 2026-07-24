def update_analytics(analytics, correct_answers, total_questions, language, mistake_counter=None):
    """
    İstatistik hesaplama mantığının yaşadığı ana modül.
    Gelişmiş veri modeliyle dil ve hata türü dağılımlarını kümülatif toplar.
    """
    analytics["total_texts_read"] = analytics.get("total_texts_read", 0) + 1
    analytics["correct_answers"] = analytics.get("correct_answers", 0) + correct_answers
    analytics["total_questions_answered"] = analytics.get("total_questions_answered", 0) + total_questions
    
    # Dil dağılımı
    lang_dist = analytics.get("language_distribution", {})
    lang_dist[language] = lang_dist.get(language, 0) + 1
    analytics["language_distribution"] = lang_dist
    
    # Hata türleri dağılımı güncellemesi
    if mistake_counter:
        current_mistakes = analytics.get("mistake_types_distribution", {"Inference": 0, "False Assumption": 0, "Careless Reading": 0})
        for m_type, count in mistake_counter.items():
            current_mistakes[m_type] = current_mistakes.get(m_type, 0) + count
        analytics["mistake_types_distribution"] = current_mistakes
    
    accuracy = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    session_summary = {
        "accuracy": accuracy,
        "correct": correct_answers,
        "total": total_questions,
        "language": language
    }
    
    return analytics, session_summary

def update_cognitive_profile(filepath="learner_analytics.json", session_data=None):
    """
    Okuma tamamlandığında kullanıcının bilişsel metriklerini 
    performansına göre dinamik olarak günceller.
    """
    if session_data is None:
        return

    import json
    import os

    # Dosya yoksa bile çökmesin, varsayılan şemayla oluştursun
    if not os.path.exists(filepath):
        data = {
            "user_id": "default_user",
            "heatmap_vocab": {},
            "reading_history": [],
            "cognitive_profile": {}
        }
    else:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    profile = data.setdefault("cognitive_profile", {
        "visual_thinking_index": 0.5,
        "inference_accuracy": 0.5,
        "abstract_tolerance": 0.5,
        "avg_reading_speed_wpm": 0,
        "total_texts_read": 0
    })

    # Toplam okunan metin sayısını artır
    profile["total_texts_read"] += 1

    # Çıkarım başarısını güncelle (Oturumda inference skoru varsa)
    if "inference_score" in session_data:
        current_inf = profile.get("inference_accuracy", 0.5)
        new_inf = session_data["inference_score"]
        profile["inference_accuracy"] = round((current_inf * 0.7) + (new_inf * 0.3), 2)

    # Okuma hızını güncelle (WPM)
    if "wpm" in session_data and session_data["wpm"] > 0:
        current_wpm = profile.get("avg_reading_speed_wpm", 0)
        if current_wpm == 0:
            profile["avg_reading_speed_wpm"] = session_data["wpm"]
        else:
            profile["avg_reading_speed_wpm"] = round((current_wpm * 0.8) + (session_data["wpm"] * 0.2), 1)

    data["cognitive_profile"] = profile

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Bilişsel profil güncellenirken hata oluştu: {e}")