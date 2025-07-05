from pydub import AudioSegment
import os

def censor_audio(audio_path, marks, action="beep", beep_path="beep.wav", out_format="wav"):
    audio = AudioSegment.from_file(audio_path)
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

    base, _ = os.path.splitext(audio_path)
    censored_path = f"{base}_{action}.{out_format}"
    result.export(censored_path, format=out_format)

    return censored_path
