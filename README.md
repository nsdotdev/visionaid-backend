# VisionAid — OCR Backend

Python backend for VisionAid, an assistive application that extracts text from document images and converts it to audio. Built as a final year group project.

## What it does

- Accepts an image upload via REST API
- Runs OCR using Tesseract to extract text (supports English and Nepali)
- Converts extracted text to speech using Google TTS (gTTS)
- Returns extracted text in the response; serves generated audio via a separate endpoint
- Lists previously processed documents

## Tech Stack

- **FastAPI** — REST API framework
- **Tesseract OCR** (via pytesseract) — text extraction
- **gTTS** — text-to-speech audio generation
- **Pillow** — image processing

## Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR** installed on your system
   - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt install tesseract-ocr`
   - macOS: `brew install tesseract`
3. For Nepali language support, install the `nep` language pack for Tesseract

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/visionaid-backend.git
cd visionaid-backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

By default, the app uses the Windows Tesseract path (`C:\Program Files\Tesseract-OCR\tesseract.exe`).

To override this, set the `TESSERACT_CMD` environment variable:

```bash
# Linux/macOS
export TESSERACT_CMD=/usr/bin/tesseract

# Windows
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Running the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.  
Auto-generated docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/extract/` | Upload image, get extracted text |
| GET | `/output/{filename}` | Download a generated text or audio file |
| GET | `/saved_files/` | List all previously processed documents |

### POST `/extract/`

**Request:** multipart/form-data with a `file` field (image)

**Response:**
```json
{
  "extracted_text": "extracted content here",
  "message": "OCR processed successfully"
}
```

## Notes

- Tesseract accuracy depends heavily on image quality (lighting, resolution, skew). Images should be clear and well-lit for best results.
- gTTS requires an internet connection to generate audio.
- Uploaded images are deleted after processing; generated text and audio files are stored in the `Output/` directory.
