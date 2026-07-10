import streamlit as st
import os

def render_sidebar(save_heatmap):
    """Yan paneldeki AI Hafıza Dashboard'unu ve Isı Haritasını çizer."""
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
            st.session_state['saved_session'] = None
            save_heatmap({})
            if os.path.exists("reading_session.json"):
                os.remove("reading_session.json")
            st.rerun()

def render_vocabulary_assistant(vocabulary, save_heatmap):
    """Metnin altındaki interaktif kelime kartlarını ve oylama butonlarını çizer."""
    st.subheader("✨ Smart Reading Assistant & Heatmap Tool")
    st.markdown("*Click a word below to explore it and log your familiarity level:*")
    
    for idx, item in enumerate(vocabulary):
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
                    save_heatmap(st.session_state['heatmap_vocab'])
                    st.rerun()
            with v_col2:
                if st.button("🟡 I've seen this", key=f"seen_{idx}"):
                    st.session_state['heatmap_vocab'][word_key] = "🟡 I've seen this"
                    save_heatmap(st.session_state['heatmap_vocab'])
                    st.rerun()
            with v_col3:
                if st.button("🔴 New to me", key=f"new_{idx}"):
                    st.session_state['heatmap_vocab'][word_key] = "🔴 New to me"
                    save_heatmap(st.session_state['heatmap_vocab'])
                    st.rerun()

def render_exercises(exercises):
    """Metne ait interaktif egzersiz formunu ve değerlendirme sonuçlarını çizer."""
    st.subheader("✍️ Interactive Exercises")
    
    with st.form("exercise_form"):
        user_tf_answers = {}
        user_mc_answers = {}
        
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