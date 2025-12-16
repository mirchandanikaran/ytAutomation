from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import subprocess
import uuid

app = FastAPI(title="FFmpeg Audio Mix Server")

# -------- CONFIG --------
FFMPEG_BIN = "ffmpeg"  # full path if not in PATH
OUTPUT_DIR = Path("D:/Python/VOUT")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------- REQUEST MODEL --------
class MixRequest(BaseModel):
    video_path: str
    audio_url: str

# -------- API --------
@app.post("/mix")
def mix_audio(req: MixRequest):
    video = Path(req.video_path)

    if not video.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    output_file = OUTPUT_DIR / f"FINAL_YOUTUBE_{uuid.uuid4().hex[:8]}.mp4"

    cmd = [
        FFMPEG_BIN, "-y",
        "-loglevel", "error",
        "-stats",
        "-i", str(video),
        "-i", req.audio_url,
        "-filter_complex",
        (
            "[0:a]volume=0.5[a0];"
            "[1:a]volume=2.5[a1];"
            "[a0][a1]amix=inputs=2:duration=shortest:dropout_transition=0[m];"
            "[m]loudnorm=I=-14:LRA=11:TP=-1.5:linear=true[a]"
        ),
        "-map", "0:v",
        "-map", "[a]",
        "-shortest",
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_file)
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "success",
        "output_video_path": str(output_file)
    }

# -------- HEALTH CHECK --------
@app.get("/health")
def health():
    return {"status": "ok"}
