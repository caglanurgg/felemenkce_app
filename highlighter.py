import re

def highlight_text(text, heatmap_vocab):
    """
    Fransızca, İspanyolca ve İngilizce gibi dillerdeki aksanları (é, à, ç) 
    ve fiil çekimlerini (captiver -> captivé, captivant) kökten yakalayan 
    evrensel akıllı highlighter motoru.
    """
    if not heatmap_vocab:
        return text

    # İç içe çakışmaları önlemek için uzun kelimeler her zaman öncelikli
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

        # 1. KORECE / ASYA DİLLERİ İÇİN
        if re.search(r'[\uac00-\ud7a3]', word):
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            
        # 2. BATI VE ROMANS DİLLERİ İÇİN (French, Spanish, English, Nederlands)
        else:
            # Fiil kökünü yakalama (Romance Language Infinitive Stemmer)
            # Eğer kelime 'captiver' gibi -er, -ir, -re veya -ar ile bitiyorsa son iki harfi esnetiyoruz
            stem = word
            if len(word) > 4 and (word.endswith(('er', 'ir', 're', 'ar'))):
                stem = word[:-2] 

            # \b ile kelime başlangıcını koruyoruz (l' veya d' sonrasını da yakalar)
            # \w* ile Fransızca aksanlı harfler dahil (é, à, ç, ant, ée) tüm çekimleri sonuna kabul ediyoruz
            pattern = re.compile(r'\b' + re.escape(stem) + r'\w*\b', re.IGNORECASE)

        text = pattern.sub(f'<span class="{class_name}">\\g<0></span>', text)

    return text