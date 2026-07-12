import re

def highlight_text(text, heatmap_vocab):
    if not heatmap_vocab:
        return text

    # Uzunluktan bağımsız olarak kelimeleri işle
    sorted_words = sorted(heatmap_vocab.keys(), key=len, reverse=True)

    for word in sorted_words:
        status = heatmap_vocab[word]
        class_name = "highlight-green" if "I know this" in status else "highlight-yellow" if "I've seen this" in status else "highlight-red"
        
        # Batı dilleri için: Kelime sınırını (\b) sadece kök için değil, 
        # türevleri de kapsayacak şekilde genişledi
        # \b(profound)(ly)?\b -> profound ve profoundly'yi yakalar.
        pattern = re.compile(r'\b' + re.escape(word) + r'[a-z]*\b', re.IGNORECASE)
        text = pattern.sub(f'<span class="{class_name}">\\g<0></span>', text)
        
    return text