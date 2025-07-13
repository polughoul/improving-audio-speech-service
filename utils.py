import os
import json
from moviepy import *
import whisper
from rapidfuzz import fuzz
import re
from pydub import AudioSegment
from pyannote.audio import Pipeline

ALLOWED_EXTENSIONS = {"wav", "mp3", "ogg", "flac", "mp4", "mov", "avi", "mkv"}
DIARIZATION_TOKEN = "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"


# --- load badwords from JSON ---
def load_badwords(path="badwords.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["ru"], data["en"]


BAD_WORDS_RU, BAD_WORDS_EN = load_badwords()


# --- extract_audio_from_video ---
def extract_audio_from_video(video_path):
    output_path = video_path.replace(".mp4", ".wav")
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
        transcript.append(
            {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
        )
    return transcript


# --- find_parasites ---
BADWORD_RE_RU = re.compile(r"\b[а-яА-ЯёЁ]+\b", re.IGNORECASE)
BADWORD_RE_EN = re.compile(r"\b[a-zA-Z]+\b", re.IGNORECASE)


def find_parasites(transcript_segments, threshold_ru=85, threshold_en=90):
    marked = []
    for seg in transcript_segments:
        text = seg["text"]
        seg_start = seg["start"]
        seg_end = seg["end"]
        duration = seg_end - seg_start
        for match in BADWORD_RE_RU.finditer(text):
            word = match.group()
            for bad in BAD_WORDS_RU:
                if fuzz.ratio(word.lower(), bad) >= threshold_ru:
                    start_char = match.start()
                    end_char = match.end()
                    word_start = seg_start + (start_char / len(text)) * duration
                    word_end = seg_start + (end_char / len(text)) * duration
                    marked.append(
                        {
                            "start": word_start,
                            "end": word_end,
                            "text": word,
                            "bad_words": [bad],
                        }
                    )
                    break
        for match in BADWORD_RE_EN.finditer(text):
            word = match.group()
            for bad in BAD_WORDS_EN:
                if fuzz.ratio(word.lower(), bad) >= threshold_en:
                    start_char = match.start()
                    end_char = match.end()
                    word_start = seg_start + (start_char / len(text)) * duration
                    word_end = seg_start + (end_char / len(text)) * duration
                    marked.append(
                        {
                            "start": word_start,
                            "end": word_end,
                            "text": word,
                            "bad_words": [bad],
                        }
                    )
                    break
    return marked


# --- censor_audio ---
def censor_audio(
    audio_path,
    marks,
    action="beep",
    beep_path="static/sounds/beep.wav",
    out_format="wav",
):
    audio = AudioSegment.from_file(audio_path)
    result = AudioSegment.empty()
    current_pos = 0
    for mark in marks:
        start_ms = int(mark["start"] * 1000)
        end_ms = int(mark["end"] * 1000)
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


# --- validation for input file  ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def diarize_audio(audio_path):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization", use_auth_token=DIARIZATION_TOKEN
    )
    diarization = pipeline(audio_path)
    speakers = {}
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if speaker not in speakers:
            speakers[speaker] = []
        speakers[speaker].append({"start": turn.start, "end": turn.end})
    return speakers


def split_audio_by_speakers(audio_path, speakers):
    audio = AudioSegment.from_file(audio_path)
    speaker_files = {}
    for spk, segments in speakers.items():
        spk_audio = AudioSegment.empty()
        for seg in segments:
            start_ms = int(seg["start"] * 1000)
            end_ms = int(seg["end"] * 1000)
            spk_audio += audio[start_ms:end_ms]
        out_path = f"{audio_path}_spk_{spk}.wav"
        spk_audio.export(out_path, format="wav")
        speaker_files[spk] = out_path
    return speaker_files
