import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from gtts import gTTS

app = FastAPI()

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'Output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Tesseract path: set TESSERACT_CMD env var to override, otherwise uses Windows default
tesseract_cmd = os.environ.get('TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Vision Aid OCR API"}

@app.post("/extract/")
async def extract_text_and_tts(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        # Save the uploaded file temporarily
        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())

        # Open image and OCR
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang='eng+nep')

        # Clean text (remove line breaks)
        clean_text = ' '.join(text.splitlines()).strip()

        # Save text file
        text_filename_base = filename.rsplit('.', 1)[0]
        text_path = os.path.join(OUTPUT_FOLDER, f"{text_filename_base}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)

        # Generate audio file using gTTS
        audio_path = os.path.join(OUTPUT_FOLDER, f"{text_filename_base}.mp3")
        if clean_text.strip():  # Only generate audio if there's text
            tts = gTTS(text=clean_text, lang='en', slow=False)
            tts.save(audio_path)

        return JSONResponse(content={
            "extracted_text": clean_text,
            "message": "OCR processed successfully"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.get("/output/{filename}")
async def get_file(filename: str):
    file_location = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_location):
        if filename.endswith('.mp3'):
            return FileResponse(path=file_location, filename=filename, media_type="audio/mpeg")
        elif filename.endswith('.txt'):
            return FileResponse(path=file_location, filename=filename, media_type="text/plain")
        else:
            return FileResponse(path=file_location, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/saved_files/")
async def list_saved_files():
    files = []
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith('.txt'):
            base = filename[:-4]
            audio_file = f"{base}.mp3"
            files.append({
                "base": base,
                "text_url": f"/output/{filename}",
                "audio_url": f"/output/{audio_file}" if os.path.exists(os.path.join(OUTPUT_FOLDER, audio_file)) else None
            })
    return JSONResponse(content={"files": files})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
