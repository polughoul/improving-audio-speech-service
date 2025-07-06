import os
from moviepy import *
import whisper
from rapidfuzz import fuzz
import re
from pydub import AudioSegment

# --- extract_audio_from_video ---
def extract_audio_from_video(video_path):
    output_path = video_path.replace('.mp4', '.wav')
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_path)
    return output_path

# --- transcribe_audio ---
model = whisper.load_model("base")
def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    segments = result.get("segments", [])
    transcript = []
    for seg in segments:
        transcript.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })
    return transcript

# --- find_parasites ---
BAD_WORDS = [
    "блин", "черт", "срань", "жопа", "хрен", "сука", "мать", "пипец", "нахрен", "пиздец", "бля", "ебать", "еблан", "ахуеть", "хуй", "хуйня", "блять", "ахуел", "пидорас", "уебан",
    "bastard", "fucked-up", "fucking", "damn", "shit", "goddamn", "asshole", "son of a bitch", "motherfucker", "bullshit", "piece of shit", "dickhead", "moron", "fuck", "shithead", "fucker", "dumb fuck"
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

# --- censor_audio ---
def censor_audio(audio_path, marks, action="beep", beep_path="sounds/beep.wav", out_format="wav"):
    audio = AudioSegment.from_file(audio_path)
    result = AudioSegment.empty()
    current_pos = 0
    for mark in marks:
        start_ms = int(mark['start'] * 1000)
        end_ms = int(mark['end'] * 1000)
        result += audio[current_pos:start_ms]
        duration = end_ms - start_ms
        if action == "beep" or action == "funny":
            beep = AudioSegment.from_wav(beep_path)
            if len(beep) > duration:
                result += beep[:duration]
            else:
                times = duration // len(beep) + 1
                result += (beep * times)[:duration]
        elif action == "mute":
            result += AudioSegment.silent(duration=duration)
        elif action == "cut":
            pass
        current_pos = end_ms
    result += audio[current_pos:]
    base, _ = os.path.splitext(audio_path)
    censored_path = f"{base}_{action}.{out_format}"
    result.export(censored_path, format=out_format)
    return censored_path