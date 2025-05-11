from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from PIL import Image
import io
import shutil

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the LightEdit API"}

@app.post("/generate_preset/")
async def generate_preset(
    file: UploadFile = File(...),
    style_description: str = None
):
    try:
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, f"{request_id}_original.jpg")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process image (placeholder for actual processing)
        output_path = os.path.join(OUTPUT_DIR, f"{request_id}_processed.jpg")
        xmp_path = os.path.join(OUTPUT_DIR, f"{request_id}.xmp")
        
        # For now, just copy the original image as processed
        shutil.copy(file_path, output_path)
        
        # Create a dummy XMP file
        with open(xmp_path, "w") as f:
            f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            f.write("<x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Adobe XMP Core 5.6-c140 79.160451, 2017/05/06-01:08:21'>\n")
            f.write("  <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>\n")
            f.write("    <rdf:Description rdf:about=''>\n")
            f.write(f"      <dc:description>{style_description}</dc:description>\n")
            f.write("    </rdf:Description>\n")
            f.write("  </rdf:RDF>\n")
            f.write("</x:xmpmeta>")
        
        return {
            "preset_id": request_id,
            "style_description": style_description,
            "xmp_url": f"/download/xmp/{request_id}",
            "preview_url": f"/download/preview/{request_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/xmp/{request_id}")
async def download_xmp(request_id: str):
    xmp_path = os.path.join(OUTPUT_DIR, f"{request_id}.xmp")
    if not os.path.exists(xmp_path):
        raise HTTPException(status_code=404, detail="XMP file not found")
    return FileResponse(xmp_path, filename=f"preset_{request_id}.xmp")

@app.get("/download/preview/{request_id}")
async def download_preview(request_id: str):
    preview_path = os.path.join(OUTPUT_DIR, f"{request_id}_processed.jpg")
    if not os.path.exists(preview_path):
        raise HTTPException(status_code=404, detail="Preview image not found")
    return FileResponse(preview_path)

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 