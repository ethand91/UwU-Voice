# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Running

```bash
pip install -r requirements.txt
python server.py        # Starts server on http://localhost:8888
python test.py          # Runs a basic demo that generates a WAV file
```

Interactive API docs available at `http://localhost:8888/docs` once the server is running.

## Architecture

This is a minimal FastAPI wrapper around the `kittentts` TTS model, designed for VTuber Studio integration.

**server.py** is the entire server — one file, four endpoints:
- `GET /health` — health check
- `GET /voices` — lists the 8 available voices (Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo)
- `POST /generate` — main TTS endpoint, accepts `TTSRequest` JSON body
- `GET /generate-stream` — GET-based TTS for browser/VTuber Studio use

Both generation endpoints share the same logic: validate voice → call `model.generate(text, voice=voice)` → encode to WAV via `soundfile` + `io.BytesIO` → return `StreamingResponse` with `audio/wav` MIME type.

The KittenTTS model (`KittenML/kitten-tts-mini-0.8`) is loaded once at startup as a module-level singleton. It runs on CPU (no GPU required).
