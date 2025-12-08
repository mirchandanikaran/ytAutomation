# 🎬 AI YouTube Shorts Automation (Offline + Local)

This project is a **fully automated YouTube Shorts generator** that works locally and offline using Python, n8n, Whisper, FFmpeg, and Kokoro TTS.

It:
- Generates voiceover using **Kokoro TTS**
- Merges audio with video
- Automatically generates subtitles using **OpenAI Whisper**
- Burns subtitles into video
- Exposes everything through **FastAPI**
- Automates workflow using **n8n**
- Optionally logs output to **Google Sheets**

---

## 🚀 Features

✅ Text-to-Speech (offline)  
✅ Subtitle Generation (Whisper)  
✅ Subtitle Burn-In with FFmpeg  
✅ NVIDIA GPU acceleration (optional)  
✅ Automated workflows via n8n  
✅ API-driven Local Server  
✅ Google Sheets Integration  
✅ No cloud requirements  
✅ Works on Windows  
✅ Fully scriptable
https://www.dropbox.com/scl/fi/cm34rvspskbe9svmnrm1m/video.mp4?rlkey=j4284yfz9ofl699x8vyump1db&st=0g6mb5zf&dl=0
---

## 📁 Project Structure

```text
.
├── burn_subs_server.py     # FastAPI server for subtitles & video generation
├── mcp_kokoro.py           # Kokoro TTS service
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── workflows/              # n8n workflow exports (optional)
ffmpeg -y -loglevel error -stats -i "C:\temp\New folder\video.mp4" -i "{{ $json.url }}" -filter_complex "[0:a]volume=0.5[a0];[1:a]volume=2.5[a1];[a0][a1]amix=inputs=2:duration=shortest:dropout_transition=0[m];[m]loudnorm=I=-14:LRA=11:TP=-1.5:linear=true[a]" -map 0:v -map "[a]" -shortest -c:v h264_nvenc -preset p4 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k "C:\temp\FINAL_YOUTUBE.mp4" echo OUTPUT_VIDEO_PATH=C:\temp\FINAL_YOUTUBE.mp4
