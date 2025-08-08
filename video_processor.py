import subprocess
import os
import time

def get_video_dimensions(path):
    """دریافت عرض و ارتفاع ویدیو با ffprobe"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True
    )
    width, height = map(int, result.stdout.strip().split(','))
    return width, height

def process_video(input_path):
    """پردازش ویدیو و تبدیل به فرمت مناسب Shorts"""
    os.makedirs("processed", exist_ok=True)
    output_path = f"processed/processed_{int(time.time())}.mp4"

    width, height = get_video_dimensions(input_path)

    if width > height and (width / height) > 0.5625:
        new_height = int(width / 0.5625)
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"pad=width={width}:height={new_height}:x=0:y=(oh-ih)/2:color=black",
            "-c:a", "copy", output_path
        ], check=True)
    else:
        os.replace(input_path, output_path)

    return output_path
