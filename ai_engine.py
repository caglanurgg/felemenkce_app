import json
from openai import OpenAI

def build_memory_instruction(heatmap_vocab):
    """Kullanıcının geçmiş kelime hafızasına göre adaptif prompt talimatını hazırlar."""
    if not heatmap_vocab:
        return ""
        
    known_words = [w for w, status in heatmap_vocab.items() if "I know this" in status]
    seen_words = [w for w, status in heatmap_vocab.items() if "I've seen this" in status]
    new_words = [w for w, status in heatmap_vocab.items() if "New to me" in status]
    
    return f"""
    \nCRITICAL - LEARNER PROFILE ADAPTATION:
    The user has a personalized vocabulary history tracking profile:
    - 🔴 New to me (Struggling/New): {new_words}
    - 🟡 I've seen this (In-progress): {seen_words}
    - 🟢 I know this (Mastered): {known_words}
    
    GENERATION RULES:
    1. If appropriate, naturally include and REUSE words from the '🔴 New to me' list at least twice to enforce learning.
    2. Occasionally re-introduce words from the '🟡 I've seen this' list to spark active recall.
    3. Do NOT substitute standard vocabulary with words from the '🟢 I know this' list unless completely unavoidable.
    4. Introduce AT MOST 2 completely new advanced vocabulary words that are not in the profile to control cognitive load.
    """

def generate_reading_package(api_key, target_language, seviye, ton, kelime_sayisi, konu, heatmap_vocab, exercise_settings):
    """
    OpenAI API ile konuşur, promptları birleştirir, JSON'ı parse eder 
     ve geriye (True/False, parsed_data, error_message) şeklinde 3'lü tuple döndürür.
    """
    # Eğer kullanıcı konu girmediyse yapay zeka rastgele ama seviyeye uygun saçmalasın
    final_topic = konu if konu.strip() else "General topics suitable for this level"

    try:
        client = OpenAI(api_key=api_key)
        # Egzersiz şeması ve kurallarının dinamik inşası
        exercise_requirements = []
        json_exercise_schema = {}
        
        if exercise_settings.get("show_tf"):
            exercise_requirements.append("- true_false: 3 statements based on the text. Each statement MUST have 'statement' (string), 'correct_answer' (boolean), and 'evidence' (the exact sentence from the text that proves it, string)")
            json_exercise_schema["true_false"] = [{"statement": "example statement", "correct_answer": True, "evidence": "exact sentence from text"}]
            
        if exercise_settings.get("show_mc"):
            exercise_requirements.append("- multiple_choice: 3 questions. Each question MUST have 'question' (string), 'options' (array of strings), 'correct_answer' (string matching one option), and 'evidence' (the exact sentence from the text where the answer is found, string)")
            json_exercise_schema["multiple_choice"] = [{"question": "example question", "options": ["Option A", "Option B"], "correct_answer": "Option A", "evidence": "exact sentence from text"}]
            
        if exercise_settings.get("show_writing"):
            exercise_requirements.append("- open_ended: 1 writing prompt string asking the user to write a short paragraph.")
            json_exercise_schema["open_ended"] = "example writing prompt here"
            
        exercise_req_text = "\n".join(exercise_requirements)
        adaptive_instruction = build_memory_instruction(heatmap_vocab)
        
        # Mimarideki System Prompt
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
            f"{adaptive_instruction}"
        )
        
        # Mimarideki User Prompt
        user_prompt = f"Write a reading text in {target_language}. Level: {seviye}, Tone: {ton}, Length: ~{kelime_sayisi} words, Subject: {final_topic}"
        
        # API Çağrısı
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
        parsed_data = json.loads(raw_json_string)
        
        return True, parsed_data, None
        
    except Exception as e:
        return False, None, str(e)