from starlette.responses import StreamingResponse
import os
import subprocess
from pathlib import Path
import uuid
import sys
import mimetypes

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse

# ---------------- CONFIG ----------------
PORT = 5001

app = FastAPI(title="Subtitle Burner Server")

# ---------------- REQUEST MODEL ----------------
class BurnRequest(BaseModel):
    video_path: str


# ---------------- RUNNER ----------------
def run(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


# ---------------- API ENDPOINT ----------------
# @app.post("/burn")
# def burn_subtitles(req: BurnRequest):
#     VIDEO = Path(req.video_path).resolve()

#     if not VIDEO.exists():
#         raise HTTPException(status_code=404, detail="Video file not found")

#     OUT_DIR = VIDEO.parent
#     BASE = VIDEO.stem + "_" + uuid.uuid4().hex[:8]

#     AUDIO = OUT_DIR / f"{BASE}_audio.wav"
#     SRT = OUT_DIR / f"{BASE}.srt"
#     FINAL = OUT_DIR / f"{BASE}_SUBBED.mp4"

#     try:
#         print("▶ Extracting audio...")
#         run(["ffmpeg", "-y", "-i", str(VIDEO), "-vn", "-acodec", "pcm_s16le", str(AUDIO)])

#         print("▶ Generating subtitles...")
#         run([
#             sys.executable, "-m", "whisper",
#             str(AUDIO),
#             "--model", "small",
#             "--language", "en",
#             "--output_format", "srt",
#             "--output_dir", str(OUT_DIR),
#         ])

#         generated = AUDIO.with_suffix(".srt")
#         generated.rename(SRT)

#         # ✅ Fixed FFmpeg path for Windows
#         srt_ff = str(SRT).replace("\\", "/").replace(":", "\\:")

#         print("▶ Burning subtitles...")
#         run([
#             "ffmpeg", "-y",
#             "-i", str(VIDEO),
#             "-vf",
#             f"subtitles=filename='{srt_ff}':force_style='Fontname=Consolas,Fontsize=20,PrimaryColour=&H00FF00&,OutlineColour=&H002200&,BorderStyle=1,Outline=1,Shadow=0.3,Alignment=5,Justify=2,MarginV=100",
#             "-c:v", "h264_nvenc",
#             "-preset", "p4",
#             "-pix_fmt", "yuv420p",
#             "-c:a", "copy",
#             str(FINAL)
#         ])

#         return JSONResponse({
#             "status": "success",
#             "final_video": str(FINAL)
#         })

#     except subprocess.CalledProcessError as e:
#         raise HTTPException(status_code=500, detail=str(e))
@app.post("/burn")
def burn_subtitles(req: BurnRequest):
    VIDEO = Path(req.video_path).resolve()

    if not VIDEO.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    OUT_DIR = VIDEO.parent
    BASE = VIDEO.stem + "_" + uuid.uuid4().hex[:8]

    AUDIO = OUT_DIR / f"{BASE}_audio.wav"
    SRT = OUT_DIR / f"{BASE}.srt"
    FINAL = OUT_DIR / f"{BASE}_SUBBED.mp4"

    try:
        print("▶ Extracting audio...")
        run(["ffmpeg", "-y", "-i", str(VIDEO), "-vn", "-acodec", "pcm_s16le", str(AUDIO)])

        print("▶ Generating subtitles...")
        run([
            sys.executable, "-m", "whisper",
            str(AUDIO),
            "--model", "small",
            "--language", "en",
            "--output_format", "srt",
            "--output_dir", str(OUT_DIR),
        ])

        generated = AUDIO.with_suffix(".srt")
        generated.rename(SRT)

        srt_ff = str(SRT).replace("\\", "/").replace(":", "\\:")

        print("▶ Burning subtitles...")
        run([
            "ffmpeg", "-y",
            "-i", str(VIDEO),
            "-vf",
            f"subtitles=filename='{srt_ff}':force_style='Fontname=Consolas,Fontsize=20,"
            f"PrimaryColour=&H00FF00&,OutlineColour=&H002200&,BorderStyle=1,Outline=1,MarginV=100,Shadow=0.3",
            "-c:v", "h264_nvenc",
            "-preset", "p4",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            str(FINAL)
        ])

        # ✅ RETURN FILE AS BINARY STREAM
        mime, _ = mimetypes.guess_type(FINAL)
        return FileResponse(
            FINAL,
            media_type=mime or "video/mp4",
            filename=FINAL.name
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- FILE DOWNLOAD ----------------
# @app.get("/download")
# def download(path: str):
#     file = Path(path)
#     if not file.exists():
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(path=str(file), filename=file.name)


# ---------------- START SERVER ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("burn_subs_server:app", host="0.0.0.0", port=PORT, reload=False)
