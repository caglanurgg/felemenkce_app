import re

def highlight_text(reading_text, heatmap_vocab):
    """
    Kayıtlı kelimeleri metin içinde dilden bağımsız (Unicode), 
    ekleri ve aksanları kapsayacak şekilde dinamik olarak vurgular.
    """
    if not heatmap_vocab:
        return reading_text
        
    # Uzun kelimeler öncelikli olsun ki iç içe çakışma (substring mismatch) yaşanmasın
    sorted_words = sorted(heatmap_vocab.keys(), key=len, reverse=True)
    
    for word in sorted_words:
        status = heatmap_vocab[word]
        
        # Duruma göre CSS sınıfı seçimi
        if "I know this" in status:
            color_class = "highlight-green"
        elif "I've seen this" in status:
            color_class = "highlight-yellow"
        else:
            color_class = "highlight-red"
            
        # Esnek kök analizi ve Unicode (aksan) destekli regex deseni
        root_word = word[:-2] if len(word) > 5 else word[:-1] if len(word) > 3 else word
        pattern = rf"\b({re.escape(root_word)}[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]*)\b"
        
        # HTML enjeksiyonu ile kelimeyi sarmala
        reading_text = re.sub(
            pattern, 
            f'<span class="{color_class}">\\1</span>', 
            reading_text, 
            flags=re.IGNORECASE
        )
        
    return reading_text