

````markdown
# AI Speech Cleaner

A service for automatic and manual detection and censoring of profane words in audio and video files.

---

## 🚀 How to Run the Application

### 1. **Clone the repository**

```bash
git clone https://github.com/polughoul/improving-audio-speech-service.git
cd improving-audio-speech-service
````

### 2. **Create and activate a virtual environment (recommended)**

```bash
python -m venv venv
```

* **For Windows:**

  ```bash
  venv\Scripts\activate
  ```
* **For Linux/Mac:**

  ```bash
  source venv/bin/activate
  ```

### 3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Install FFmpeg (required for audio/video processing)**

* **Windows**:

  * Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  * Add the path to `ffmpeg.exe` to your system **PATH** variable
* **Linux**:

  ```bash
  sudo apt install ffmpeg
  ```
* **macOS**:

  ```bash
  brew install ffmpeg
  ```

### 5. **Run the application**

```bash
python app.py
```

### 6. **Open in your browser**

```
http://127.0.0.1:5000/
```

---

## 📝 Notes

* `ffmpeg` must be installed on the machine where you run the Flask application.
* All uploaded and processed files are saved in the `uploads/` folder.
* For manual audio markup, use the **"Manual Markup"** tab in the top menu.
