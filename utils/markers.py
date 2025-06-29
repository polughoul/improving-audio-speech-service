import re

FILLER_WORDS = [
    "ну", "короче", "типа", "это самое", "как бы", "значит", "получается", "прикинь", "в общем"
]

BAD_WORDS = [
    "блин", "черт", "срань", "жопа", "хрен", "сука", "мать", "пипец", "нахрен", "ё", "ёп", "пиздец", "пошел ты", "бля"
]

FILLER_RE = re.compile(r'\b(?:' + '|'.join(map(re.escape, FILLER_WORDS)) + r')\b', re.IGNORECASE)
BADWORD_RE = re.compile(r'\b(?:' + '|'.join(map(re.escape, BAD_WORDS)) + r')\b', re.IGNORECASE)

def find_parasites(transcript_segments):
    marked = []

    for seg in transcript_segments:
        text = seg['text']
        fillers = FILLER_RE.findall(text)
        bads = BADWORD_RE.findall(text)

        if fillers or bads:
            marked.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": text,
                "fillers": fillers,
                "bad_words": bads
            })

    return marked
