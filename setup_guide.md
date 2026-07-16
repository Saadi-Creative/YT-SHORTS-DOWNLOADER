# Local Setup Guide for Shorts Media Downloader

Even though this app is fully configured to deploy seamlessly on Vercel without system dependencies, you might want to run it locally for testing or modifications.

## 1. Install Python Dependencies

Make sure you have Python 3.9+ installed. Open your terminal or command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```
*(This will install FastAPI, Uvicorn, yt-dlp, requests, and imageio-ffmpeg).*

## 2. FFmpeg Configuration

Because we are using `imageio-ffmpeg`, you **do not** need to manually install or configure `ffmpeg`! The Python package automatically downloads a static binary and provides it to `yt-dlp`. 

*If you still want to install system `ffmpeg` for other purposes:*
- **Windows**: Install via `winget install ffmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add to PATH.
- **Mac**: Install via Homebrew: `brew install ffmpeg`
- **Linux (Ubuntu/Debian)**: Run `sudo apt update && sudo apt install ffmpeg`

## 3. Running Locally

To run the full stack locally, we will use standard Python for the backend and serve the frontend files directly.

Since Vercel automatically routes `/` to the public folder and `/api` to the backend, locally we can run the FastAPI server and point our browser to it.

1. **Start the Backend**:
   ```bash
   uvicorn api.index:app --reload
   ```
   *(This starts the backend on `http://127.0.0.1:8000`)*

2. **Serve the Frontend**:
   Open a **new** terminal window, navigate to the `public` folder, and run a simple HTTP server:
   ```bash
   cd public
   python -m http.server 3000
   ```
   *(This serves the frontend on `http://127.0.0.1:3000`)*

3. **Important Note for Local Dev**: 
   Since the frontend is on port `3000` and backend is on `8000`, you might hit CORS issues. For local development, change the `apiUrl` in `public/script.js` to point to `http://127.0.0.1:8000/api/download?url=...` instead of just `/api/download?url=...`. 
   
   *(Remember to change it back before deploying to Vercel!)*

## 4. Deploying to Vercel

1. Push your code to a new GitHub repository.
2. Go to your [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New > Project**.
3. Import your GitHub repository.
4. Leave all settings as default (Framework Preset: Other) and click **Deploy**.
5. Vercel will automatically read the `vercel.json` file, install the Python requirements, configure the 60-second timeout, and deploy both the UI and backend!
