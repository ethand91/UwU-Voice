"""
KittenTTS API Server uwu
A cute little API for generating TTS audio from KittenTTS model
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import soundfile as sf

from kittentts import KittenTTS

# Initialize the model
model = KittenTTS("KittenML/kitten-tts-mini-0.8")

app = FastAPI(
    title="KittenTTS API",
    description="Cute TTS API for VTuber Studio integration uwu",
    version="1.0.0"
)

# Available voices
AVAILABLE_VOICES = ['Bella', 'Jasper', 'Luna', 'Bruno', 'Rosie', 'Hugo', 'Kiki', 'Leo']


class TTSRequest(BaseModel):
    text: str
    voice: str = 'Kiki'
    sample_rate: int = 24000


@app.get("/health")
async def health_check():
    """Check if the API is running uwu"""
    return {"status": "ok", "message": "KittenTTS is ready! uwu"}


@app.get("/voices")
async def list_voices():
    """Get list of available voices"""
    return {"voices": AVAILABLE_VOICES}


@app.post("/generate")
async def generate_tts(request: TTSRequest):
    """
    Generate TTS audio from text
    
    Returns audio as WAV file
    """
    if request.voice not in AVAILABLE_VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice. Available: {AVAILABLE_VOICES}"
        )
    
    try:
        # Generate audio
        audio = model.generate(request.text, voice=request.voice)
        
        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio, request.sample_rate, format='WAV')
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=tts_output.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate-stream")
async def generate_tts_get(text: str, voice: str = 'Kiki', sample_rate: int = 24000):
    """
    Generate TTS audio via GET request (for easy browser testing)
    """
    return await generate_tts(TTSRequest(text=text, voice=voice, sample_rate=sample_rate))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
