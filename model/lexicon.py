INDONESIAN_POSITIVE_WORDS = {
    "baik", "bagus", "hebat", "mantap", "setuju", "dukung", "apresiasi",
    "syukur", "alhamdulillah", "terima_kasih", "terimakasih", "berkualitas",
    "tepat", "cerdas", "stabil", "terjangkau", "adil", "bangga", "jaya",
    "lancar", "gembira", "bersyukur", "maju", "sejahtera", "nyaman",
    "aman", "puas", "senang", "brilian", "sukses", "berhasil", "baiknya",
    "indah", "nikmat", "murah", "turun", "hemat", "efisien", "ramah",
}

INDONESIAN_NEGATIVE_WORDS = {
    "naik", "mahal", "sengsara", "menderita", "rugi", "susah", "protes",
    "tolak", "demo", "mogok", "parah", "inflasi", "korupsi", "beban",
    "tidak_becus", "gagal", "ancam", "krisis", "sulit", "buruk", "jelek",
    "sesat", "bodoh", "curang", "serakah", "aneh", "hoax", "bohong",
    "antri", "panic", "kacau", "amburadul", "sedih", "kecewa", "marah",
    "benci", "jengkel", "kesal", "hancur", "morat-marit", "tidak_adil",
    "menyakiti", "mencekik", "memberatkan", "merugikan", "menindas",
}

INDONESIAN_NEGATION_WORDS = {
    "tidak", "bukan", "belum", "jangan", "gak", "ga", "nggak",
    "tak", "tanpa", "kurang",
}

INTENSIFIERS = {
    "sangat", "amat", "sekali", "paling", "terlalu", "begitu",
    "semakin", "makin", "benar-benar", "sungguh",
}


def normalize_word(word):
    word = word.lower().strip(".,!?;:\"'()[]{}")
    return word


def analyze_lexicon(text):
    words = text.lower().split()
    score = 0
    positive_count = 0
    negative_count = 0
    negation_active = False
    found_words = {"positive": [], "negative": []}

    i = 0
    while i < len(words):
        raw = words[i]
        word = normalize_word(raw)
        if not word:
            i += 1
            continue

        if word in INDONESIAN_NEGATION_WORDS:
            negation_active = True
            i += 1
            continue

        word_score = 0
        word_label = None

        if word in INDONESIAN_POSITIVE_WORDS:
            word_score = 1
            word_label = "positive"
            found_words["positive"].append(word)
        elif word in INDONESIAN_NEGATIVE_WORDS:
            word_score = -1
            word_label = "negative"
            found_words["negative"].append(word)

        if word_label:
            if negation_active:
                word_score *= -1
                negation_active = False
            if i > 0 and normalize_word(words[i - 1]) in INTENSIFIERS:
                word_score *= 1.5
            if i > 1 and normalize_word(words[i - 2]) in INTENSIFIERS:
                word_score *= 1.5
            score += word_score
            if word_score > 0:
                positive_count += 1
            elif word_score < 0:
                negative_count += 1
        i += 1

    if positive_count == 0 and negative_count == 0:
        return {"label": "netral", "score": 0.0, "positive_words": [], "negative_words": []}

    total = positive_count + negative_count
    normalized = score / total if total > 0 else 0.0
    normalized = max(-1.0, min(1.0, normalized))

    if normalized > 0.15:
        label = "positif"
    elif normalized < -0.15:
        label = "negatif"
    else:
        label = "netral"

    return {
        "label": label,
        "score": round(normalized, 4),
        "positive_words": found_words["positive"],
        "negative_words": found_words["negative"],
    }
