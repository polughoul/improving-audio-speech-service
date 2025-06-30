import re

BAD_WORDS = [
    "блин", "черт", "срань", "жопа", "хрен", "сука", "мать", "пипец", "нахрен", "пиздец", "бля", "ебать", "еблан", "ахуеть", "хуй", "хуйня", "блять", "ахуел", "пидорас", "уебан"
]

BADWORD_RE = re.compile(r'\b(?:' + '|'.join(map(lambda w: re.escape(w) + r'\w*', BAD_WORDS)) + r')\b', re.IGNORECASE)

def find_parasites(transcript_segments):
    marked = []

    for seg in transcript_segments:
        text = seg['text']
        seg_start = seg['start']
        seg_end = seg['end']
        duration = seg_end - seg_start

        for match in BADWORD_RE.finditer(text):
            word = match.group()
            start_char = match.start()
            end_char = match.end()
            word_start = seg_start + (start_char / len(text)) * duration
            word_end = seg_start + (end_char / len(text)) * duration

            marked.append({
                "start": word_start,
                "end": word_end,
                "text": word,
                "bad_words": [word]
            })

    return marked
