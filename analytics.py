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