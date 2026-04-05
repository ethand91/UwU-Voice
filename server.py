"""
KittenTTS API Server uwu
A cute little API for generating TTS audio from KittenTTS model
"""

import os
from pathlib import Path
import logging
import re
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import numpy as np
import soundfile as sf

from kittentts import KittenTTS

logger = logging.getLogger("uvicorn.error")

# Help phonemizer find the Homebrew espeak-ng library on macOS.
espeak_library = Path("/opt/homebrew/opt/espeak-ng/lib/libespeak-ng.dylib")
if "PHONEMIZER_ESPEAK_LIBRARY" not in os.environ and espeak_library.is_file():
    os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = str(espeak_library)

# Initialize the model
model = KittenTTS()

app = FastAPI(
    title="KittenTTS API",
    description="Cute TTS API for VTuber Studio integration uwu",
    version="1.0.0"
)

# Available voices
AVAILABLE_VOICES = model.available_voices
MAX_TTS_TOKENS = 240
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
EMPHASIS_RE = re.compile(r"\*([^*]+)\*")


class TTSRequest(BaseModel):
    text: str
    voice: str = AVAILABLE_VOICES[0]
    sample_rate: int = 24000


def normalize_tts_text(text: str) -> str:
    # Keep the emphasized text but strip authoring markers like *excited*.
    text = EMPHASIS_RE.sub(r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_phonemes(phonemes: str) -> str:
    return " ".join(re.findall(r"\w+|[^\w\s]", phonemes))


def token_count_for_text(text: str) -> int:
    phonemes = model._phonemizer.phonemize([text])[0]
    tokenized = tokenize_phonemes(phonemes)
    return len([c for c in tokenized if c in model._word_index_dictionary])


def split_long_segment(segment: str, max_tokens: int) -> List[str]:
    words = segment.split()
    chunks: List[str] = []
    current: List[str] = []

    for word in words:
        candidate = " ".join(current + [word]).strip()
        if current and token_count_for_text(candidate) > max_tokens:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_tts_text(text: str, max_tokens: int = MAX_TTS_TOKENS) -> List[str]:
    normalized = normalize_tts_text(text)
    if not normalized:
        return []

    segments = [s.strip() for s in SENTENCE_SPLIT_RE.split(normalized) if s.strip()]
    chunks: List[str] = []
    current = ""

    for segment in segments:
        candidate = f"{current} {segment}".strip() if current else segment
        if current and token_count_for_text(candidate) > max_tokens:
            chunks.append(current)
            current = segment
        elif token_count_for_text(segment) > max_tokens:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(split_long_segment(segment, max_tokens))
        else:
            current = candidate

    if current:
        chunks.append(current)
    return chunks


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
        normalized_text = normalize_tts_text(request.text)
        phonemes = model._phonemizer.phonemize([normalized_text])[0]
        tokenized = tokenize_phonemes(phonemes)
        bad_chars = sorted({c for c in tokenized if c not in model._word_index_dictionary})
        if bad_chars:
            logger.warning(
                "Unsupported characters in generate request text=%r voice=%s phonemes=%r bad_chars=%s",
                normalized_text,
                request.voice,
                phonemes,
                bad_chars,
            )

        chunks = chunk_tts_text(request.text)
        if not chunks:
            raise HTTPException(status_code=400, detail="Text is empty after preprocessing")

        if len(chunks) > 1:
            logger.info(
                "Chunking generate request voice=%s chunks=%d original_len=%d normalized_len=%d",
                request.voice,
                len(chunks),
                len(request.text),
                len(normalized_text),
            )

        audio_parts = []
        for chunk in chunks:
            audio_parts.append(model.generate(chunk, voice=request.voice))

        # Concatenate chunk audio into a single WAV response.
        audio = np.concatenate(audio_parts) if len(audio_parts) > 1 else audio_parts[0]
        
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
async def generate_tts_get(text: str, voice: str = AVAILABLE_VOICES[0], sample_rate: int = 24000):
    """
    Generate TTS audio via GET request (for easy browser testing)
    """
    return await generate_tts(TTSRequest(text=text, voice=voice, sample_rate=sample_rate))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "5050"))
    uvicorn.run(app, host="0.0.0.0", port=port)
