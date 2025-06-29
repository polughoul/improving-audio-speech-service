from pydub import AudioSegment
import os

def censor_audio(audio_path, marks, action="beep", beep_path="beep.wav"):
    audio = AudioSegment.from_wav(audio_path)
    result = AudioSegment.empty()

    current_pos = 0
    for mark in marks:
        start_ms = int(mark['start'] * 1000)
        end_ms = int(mark['end'] * 1000)
        result += audio[current_pos:start_ms]

        if action == "beep":
            beep = AudioSegment.from_wav(beep_path)
            duration = end_ms - start_ms
            result += beep[:duration] if len(beep) > duration else beep * (duration // len(beep) + 1)
        elif action == "cut":
            pass  

        current_pos = end_ms
    result += audio[current_pos:]

    censored_path = audio_path.replace(".wav", f"_{action}.wav")
    result.export(censored_path, format="wav")

    return censored_path
