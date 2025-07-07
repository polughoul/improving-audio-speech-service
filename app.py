from flask import Flask, request, render_template, send_from_directory, flash
import os
from utils import (
    extract_audio_from_video,
    transcribe_audio,
    find_parasites,
    censor_audio,
    allowed_file,
)

app = Flask(__name__)
app.secret_key = "secret"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            filename = file.filename
            if not allowed_file(filename):
                flash(
                    "Unsupported file type. Allowed: wav, mp3, ogg, flac, mp4, mov, avi, mkv."
                )
                return render_template("index.html")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            if filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
                audio_path = extract_audio_from_video(file_path)
            else:
                audio_path = file_path

            transcript = transcribe_audio(audio_path)
            marks = find_parasites(transcript)
            out_format = request.form.get("out_format", "wav")
            return render_template(
                "index.html",
                transcript=transcript,
                marks=marks,
                filename=filename,
                out_format=out_format,
            )

        filename = request.form.get("file")
        out_format = request.form.get("out_format", "wav")
        action = request.form.get("action", "beep")
        funny_sound = request.form.get("funny_sound", "static/sounds/duck.wav")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            audio_path = extract_audio_from_video(file_path)
        else:
            audio_path = file_path

        transcript = transcribe_audio(audio_path)
        marks = find_parasites(transcript)
        selected = request.form.getlist("selected_marks")
        if selected:
            marks = [marks[int(i)] for i in selected]

        if action == "funny":
            beep_path = funny_sound
        else:
            beep_path = "static/sounds/beep.wav"
        censored_path = (
            censor_audio(
                audio_path,
                marks,
                action=action,
                beep_path=beep_path,
                out_format=out_format,
            )
            if marks
            else None
        )
        censored_filename = os.path.basename(censored_path) if censored_path else None
        return render_template(
            "index.html",
            transcript=transcript,
            marks=marks,
            censored_path=censored_path,
            censored_filename=censored_filename,
            filename=filename,
        )

    return render_template("index.html")


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
