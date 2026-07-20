# 🎬 Shorts Media Downloader

A premium, serverless-compatible web application to download short-form videos (YouTube Shorts, Instagram Reels, TikToks) in their highest/original posted quality (1080p, 720p, etc.) with audio fully merged. 

It features a stunning, dark-themed **glassmorphic UI** and is pre-configured to deploy directly on **Vercel** with zero external dependencies (using Python backend serverless functions and pre-compiled FFmpeg static bindings).

---

## ✨ Features

- **Highest Quality**: Configured to dynamically request 1080p/720p+ stream components and merge them.
- **Glassmorphic UI**: Beautiful frontend built with pure HTML/CSS/JS containing rich animations, hover states, and dark mode.
- **Real-Time Progress**: Streams progress (percentage, download speed, total size) directly from the backend to the UI.
- **Dual-Mode Delivery**:
  - **Local Mode**: Downloads and saves files instantly to `public/downloads/` (skips cloud uploads).
  - **Vercel Mode**: Dynamically uploads files to secure temporary storage (`tmpfiles.org` or `litterbox`) to bypass Vercel's 4.5MB response size limits.
- **Zero-Config FFmpeg**: Uses `imageio-ffmpeg` to bundle static FFmpeg binaries, eliminating the need to install or configure FFmpeg on Vercel or locally.

---

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (Custom Variables, Keyframe Animations), Vanilla JavaScript (Server-Sent Events / EventSource).
- **Backend**: Python 3.9+, FastAPI, Uvicorn, `yt-dlp`, `imageio-ffmpeg`.
- **Hosting**: Vercel (Frontend + Serverless Functions).

---

## 🚀 Getting Started

### Local Setup & Testing

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Saadi-Creative/YT-SHORTS-DOWNLOADER.git
   cd YT-SHORTS-DOWNLOADER
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   uvicorn api.index:app --reload
   ```

4. **Access the Web App**:
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## 📁 Project Structure

```text
├── api/
│   └── index.py        # FastAPI Backend (logical handler + yt-dlp)
├── public/
│   ├── index.html      # UI Layout
│   ├── style.css       # Glassmorphism Styles & Animations
│   └── script.js       # SSE Progress tracker & download initiator
├── vercel.json         # Vercel Serverless configurations (maxDuration: 60s)
├── requirements.txt    # Python dependencies
└── .gitignore          # Git exclusion rules (e.g. downloaded videos)
```

---

## 📄 License

MIT License. Designed and optimized for personal automation and high-speed media processing.
