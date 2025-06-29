from utils.audio_editor import censor_audio
import os
print("Current working directory:", os.getcwd())

marks = [
    {"start": 1.0, "end": 2.0},
    {"start": 4.0, "end": 5.5}
]

censor_audio("test.wav", marks, action="beep", beep_path="utils/beep.wav")
print("Audio censored successfully.")



