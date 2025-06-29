from flask import Flask, request, jsonify, send_file
import os
from utils.extract_audio import extract_audio_from_video
from utils.transcribe import transcribe_audio
from utils.markers import find_parasites
from utils.audio_editor import censor_audio

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "AI Speech Cleaner API is running!"

@app.route('/upload', methods=['POST'])
def upload_video():
    video = request.files.get('file')
    if not video:
        return jsonify({'error': 'No file uploaded'}), 400

    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)

    audio_path = extract_audio_from_video(video_path)
    transcript = transcribe_audio(audio_path)
    parasite_marks = find_parasites(transcript)

    edited_audio_path = censor_audio(audio_path, parasite_marks, action="beep", beep_path="beep.wav")

    return jsonify({
        'transcript': transcript,
        'parasites': parasite_marks
    })

if __name__ == '__main__':
    app.run(debug=True)
