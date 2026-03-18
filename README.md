# KittenTTS API uwu

A cute little API server for generating TTS audio using KittenTTS, designed for VTuber Studio integration!

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Server

```bash
python server.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### `GET /health`
Check if the API is running

```bash
curl http://localhost:8000/health
```

### `GET /voices`
List available voices

```bash
curl http://localhost:8000/voices
```

### `POST /generate`
Generate TTS audio (returns WAV file)

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from VTuber Studio!", "voice": "Kiki"}' \
  --output output.wav
```

### `GET /generate-stream`
Generate TTS via GET (for easy testing)

```bash
curl "http://localhost:8000/generate-stream?text=Hello&voice=Kiki" --output output.wav
```

## Available Voices

- Bella, Jasper, Luna, Bruno
- Rosie, Hugo, Kiki, Leo

## Usage in VTuber Studio

```javascript
// Example fetch call
const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Nyaa! Welcome to my stream!',
    voice: 'Kiki'
  })
});

const audioBlob = await response.blob();
const audioUrl = URL.createObjectURL(audioBlob);
const audio = new Audio(audioUrl);
audio.play();
```

## API Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation uwu
