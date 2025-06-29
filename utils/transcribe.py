import whisper
import os

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
