from rapidfuzz import fuzz
import re

BAD_WORDS = [
    "блин", "черт", "срань", "жопа", "хрен", "сука", "мать", "пипец", "нахрен", "пиздец", "бля", "ебать", "еблан", "ахуеть", "хуй", "хуйня", "блять", "ахуел", "пидорас", "уебан"
]

BADWORD_RE = re.compile(r'\b\w+\b', re.IGNORECASE)

def find_parasites(transcript_segments, threshold=85):
    marked = []

    for seg in transcript_segments:
        text = seg['text']
        seg_start = seg['start']
        seg_end = seg['end']
        duration = seg_end - seg_start

        for match in BADWORD_RE.finditer(text):
            word = match.group()
            for bad in BAD_WORDS:
                if fuzz.ratio(word.lower(), bad) >= threshold:
                    start_char = match.start()
                    end_char = match.end()
                    word_start = seg_start + (start_char / len(text)) * duration
                    word_end = seg_start + (end_char / len(text)) * duration
                    marked.append({
                        "start": word_start,
                        "end": word_end,
                        "text": word,
                        "bad_words": [bad]
                    })
                    break

    return marked