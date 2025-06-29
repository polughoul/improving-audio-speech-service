from moviepy import *
import os

def extract_audio_from_video(video_path):
    output_path = video_path.replace('.mp4', '.wav') 
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_path)
    return output_path
