def update_analytics(analytics, correct_answers, total_questions, language):
    """
    İstatistik hesaplama mantığının yaşadığı ana modül.
    ui.py'dan sadece ham verileri alır, hesaplar ve güncel analitik ile oturum özetini döner.
    """
    # 1. Güvenli varsayılan değerleri sağla
    analytics["total_texts_read"] = analytics.get("total_texts_read", 0) + 1
    analytics["correct_answers"] = analytics.get("correct_answers", 0) + correct_answers
    analytics["total_questions_answered"] = analytics.get("total_questions_answered", 0) + total_questions
    
    # 2. Dil dağılımını güncelle
    lang_dist = analytics.get("language_distribution", {})
    lang_dist[language] = lang_dist.get(language, 0) + 1
    analytics["language_distribution"] = lang_dist
    
    # 3. Anlık oturumun başarı yüzdesini hesapla (Session Summary)
    accuracy = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    session_summary = {
        "accuracy": accuracy,
        "correct": correct_answers,
        "total": total_questions,
        "language": language
    }
    
    return analytics, session_summary