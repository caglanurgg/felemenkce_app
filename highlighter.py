import re

def highlight_text(text, heatmap_vocab):
    """
    Fransızca, İspanyolca ve İngilizce gibi dillerdeki aksanları (é, à, ç) 
    ve fiil/isim çekimlerini (captiver -> captivé, mélodie -> mélodies) kökten yakalayan 
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

        # 1. Korean
        if re.search(r'[\uac00-\ud7a3]', word):
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            
        # 2.(French, Spanish, English, Nederlands)
        else:
            # Fiil ve isim kökünü esnetme (Romance Language Stemmer)
            stem = word
            
            # Fiil son ekleri (-er, -ir, -re, -ar) esnetmesi
            if len(word) > 4 and word.endswith(('er', 'ir', 're', 'ar')):
                stem = word[:-2]
            # İsim/Sıfat sonundaki tekil/çoğul veya aksanlı dişil ek esnetmesi (mélodie -> mélodi, spectaculaire -> spectaculair)
            elif len(word) > 4 and word.endswith(('e', 's', 'x')):
                stem = word[:-1]

            # [a-zA-Za-zA-ZÀ-ÿ]* deseni Fransızca aksanlı karakterler (é, è, à, ç vb.) 
            # ve tüm çekim takılarını (s, es, ant, ées) kapsayacak şekilde esnek arama yapar.
            pattern = re.compile(r'(?<!\w)' + re.escape(stem) + r'[\wÀ-ÿ]*(?!\w)', re.IGNORECASE)

        text = pattern.sub(f'<span class="{class_name}">\\g<0></span>', text)

    return text