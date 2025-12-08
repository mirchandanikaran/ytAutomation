import uuid
import subprocess
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse

# ---------------- CONFIG ----------------
KOKORO_BINARY = "kokoro"        # already in PATH on your system
DEFAULT_VOICE = "af_jessica"    # ✅ your confirmed working voice
PORT = 5000

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------- API -------------------
app = FastAPI(title="Kokoro TTS API")

class TTSRequest(BaseModel):
    text: str
    voice: str = DEFAULT_VOICE
    speed: float = 1.0

@app.get("/health")
def health():
    return {"status": "ok", "engine": "kokoro", "voice": DEFAULT_VOICE}

@app.post("/tts")
def tts(req: TTSRequest):
    filename = f"{uuid.uuid4()}.wav"
    outfile = OUTPUT_DIR / filename

    command = [
        KOKORO_BINARY,
        "-t", req.text,
        "-m", req.voice,
        "-s", str(req.speed),
        "-o", str(outfile)
    ]
    # subprocess.run(["python", "burn_subs.py", str("C:\temp\FINAL_YOUTUBE.mp4")], check=True)
    result = subprocess.run(command, capture_output=True, text=True)

    # Return ERROR details to n8n if it fails
    if result.returncode != 0:
        return JSONResponse({
            "error": "Kokoro failed",
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr
        }, status_code=500)

    if not outfile.exists():
        return JSONResponse({
            "error": "Audio file not created",
            "command": command
        }, status_code=500)

    return {
        "success": True,
        "file": filename,
        "url": f"http://127.0.0.1:{PORT}/audio/{filename}"
    }

@app.get("/audio/{filename}")
def get_audio(filename: str):
    path = OUTPUT_DIR / filename
    if not path.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(path, media_type="audio/wav")

# ---------------- RUN -------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tts_server:app", host="0.0.0.0", port=5000)
