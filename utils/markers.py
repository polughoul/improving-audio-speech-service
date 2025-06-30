import re

BAD_WORDS = [
    "блин", "черт", "срань", "жопа", "хрен", "сука", "мать", "пипец", "нахрен", "ё", "ёп", "пиздец", "пошел ты", "бля"
]

BADWORD_RE = re.compile(r'\b(?:' + '|'.join(map(re.escape, BAD_WORDS)) + r')\b', re.IGNORECASE)

def find_parasites(transcript_segments):
    marked = []

    for seg in transcript_segments:
        text = seg['text']
        bads = BADWORD_RE.findall(text)

        if bads:
            marked.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": text,
                "bad_words": bads
            })

    return marked
