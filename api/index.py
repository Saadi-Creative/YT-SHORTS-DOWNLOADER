import os
import uuid
import queue
import threading
import json
import logging
import requests
import imageio_ffmpeg
import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

IS_VERCEL = os.environ.get("VERCEL") == "1" or os.environ.get("VERCEL_ENV") is not None

def handle_file_delivery(filepath):
    """Delivers file locally or uploads it to a sharing service depending on Vercel environment."""
    if not IS_VERCEL:
        try:
            import shutil
            os.makedirs("public/downloads", exist_ok=True)
            filename = os.path.basename(filepath)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            local_dest = os.path.join("public/downloads", unique_filename)
            shutil.move(filepath, local_dest)
            return f"/downloads/{unique_filename}"
        except Exception as e:
            logging.error(f"Local file delivery failed: {e}")
            # Fallback to upload if local move fails

    # Vercel upload logic: Try tmpfiles.org first
    try:
        with open(filepath, "rb") as f:
            response = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=15)
        response.raise_for_status()
        url = response.json().get("data", {}).get("url")
        if url:
            return url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except Exception as e:
        logging.error(f"tmpfiles.org upload failed: {e}")

    # Fallback to litterbox
    try:
        with open(filepath, "rb") as f:
            data = {
                "reqtype": "fileupload",
                "time": "1h"
            }
            response = requests.post("https://litterbox.catbox.moe/api", data=data, files={"fileToUpload": f}, timeout=15)
        response.raise_for_status()
        url = response.text.strip()
        if url.startswith("https://"):
            return url
    except Exception as e:
        logging.error(f"Litterbox upload failed: {e}")

    return None

def download_video(url: str, q: queue.Queue):
    import tempfile
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    download_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{download_id}.%(ext)s")
    
    # To keep track of the final filename decided by yt-dlp
    final_filename = [None]
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            # Remove ANSI escape codes that yt-dlp might add
            def clean_ansi(text):
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                return ansi_escape.sub('', text)

            percent = clean_ansi(d.get('_percent_str', '0%')).strip()
            speed = clean_ansi(d.get('_speed_str', '0KiB/s')).strip()
            eta = clean_ansi(d.get('_eta_str', 'Unknown')).strip()
            file_size = clean_ansi(d.get('_total_bytes_str', d.get('_estimate_bytes_str', 'Unknown'))).strip()
            
            q.put({
                "status": "downloading",
                "percent": percent,
                "speed": speed,
                "eta": eta,
                "size": file_size
            })
        elif d['status'] == 'finished':
            q.put({
                "status": "processing",
                "message": "Download finished. Merging audio and video..."
            })
            
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/best',
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': temp_path,
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4'
    }

    try:
        q.put({"status": "starting", "message": "Fetching video info..."})
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Since merge_output_format is mp4, yt-dlp often creates an .mp4 file.
            if filename.endswith('.webm'):
                base = filename.rsplit('.', 1)[0]
                if os.path.exists(base + '.mp4'):
                    filename = base + '.mp4'
            
            if not os.path.exists(filename):
                # Check for merged mp4 file if filename is different
                base = os.path.splitext(temp_path.replace('%(ext)s', ''))[0]
                possible_mp4 = base + '.mp4'
                if os.path.exists(possible_mp4):
                    filename = possible_mp4

            if not os.path.exists(filename):
                raise Exception("File was not downloaded successfully.")
                
            q.put({"status": "uploading", "message": "Saving video..." if not IS_VERCEL else "Uploading to secure server..."})
            
            # Save or Upload the file
            direct_url = handle_file_delivery(filename)
            
            if direct_url:
                title = info.get('title', 'downloaded_video')
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                
                q.put({
                    "status": "done",
                    "url": direct_url,
                    "title": safe_title
                })
            else:
                q.put({"status": "error", "message": "Failed to generate direct download link."})
                
            # Cleanup
            if IS_VERCEL:
                try:
                    os.remove(filename)
                except:
                    pass
                
    except Exception as e:
        q.put({"status": "error", "message": str(e)})


@app.get("/api/download")
def download_endpoint(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    q = queue.Queue()

    # Start the download in a background thread
    t = threading.Thread(target=download_video, args=(url, q))
    t.start()

    def event_generator():
        while True:
            try:
                msg = q.get(timeout=1.0)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg["status"] in ["done", "error"]:
                    break
            except queue.Empty:
                if not t.is_alive():
                    break
                # Send a ping to keep connection alive
                yield ": ping\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Mount static files for local development
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")

