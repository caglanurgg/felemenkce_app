import re

def highlight_text(text, heatmap_vocab):
    """
    Metindeki kelimeleri kullanıcının hafıza durumuna göre renklendirir.
    Korece gibi bitişik ek alan dillerde tam kelime sınırı (\b) yerine 
    akıllı kök (substring) araması yapar.
    """
    if not heatmap_vocab:
        return text

    # Kelimeleri uzunluklarına göre büyükten küçüğe sıralıyoruz.
    # (Böylece önce uzun kelimeler boyanır, iç içe geçmeler engellenir)
    sorted_words = sorted(heatmap_vocab.keys(), key=len, reverse=True)

    for word in sorted_words:
        status = heatmap_vocab[word]
        
        if "I know this" in status:
            class_name = "highlight-green"
        elif "I've seen this" in status:
            class_name = "highlight-yellow"
        elif "New to me" in status:
            class_name = "highlight-red"
        else:
            continue

        if re.search(r'[\uac00-\ud7a3]', word):
            # Asya dilleri için: Kelime sınırına bakmadan direkt kök (substring) olarak ara
            pattern = re.compile(re.escape(word), re.IGNORECASE)
        else:
            # Batı dilleri için: Kelime sınırlarını (\b) koru ki kelime içindeki heceler rastgele boyanmasın
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)

        text = pattern.sub(f'<span class="{class_name}">\\g<0></span>', text)

    return text