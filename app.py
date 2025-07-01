from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import os
from utils.extract_audio import extract_audio_from_video
from utils.transcribe import transcribe_audio
from utils.markers import find_parasites
from utils.audio_editor import censor_audio

app = Flask(__name__)
app.secret_key = "secret"
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('Choose file!')
            return redirect(url_for('index'))
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            audio_path = extract_audio_from_video(file_path)
        else:
            audio_path = file_path

        transcript = transcribe_audio(audio_path)
        marks = find_parasites(transcript)
        censored_path = censor_audio(audio_path, marks, action="beep", beep_path="beep.wav") if marks else None

        return render_template('index.html', transcript=transcript, marks=marks, censored_path=censored_path, filename=filename)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
