from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.responses import Response
import shutil
import os
from typing import List, Optional, Dict
import json
import datetime
from PIL import Image, ImageEnhance
import io
import uuid
import re
from preset_generator import create_preset_from_prompt, match_prompt_to_preset
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Full Stack App API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "processed")
XMP_DIR = os.getenv("XMP_DIR", "xmp_files")
DNG_DIR = os.getenv("DNG_DIR", "dng_files")

for directory in [UPLOAD_DIR, PROCESSED_DIR, XMP_DIR, DNG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Create metadata file if it doesn't exist
METADATA_FILE = os.path.join(UPLOAD_DIR, "metadata.json")
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w") as f:
        json.dump([], f)

def process_image(image_path: str, style_description: str) -> str:
    """Process the image and return the path to the processed image."""
    # Generate a unique ID for this processing
    process_id = str(uuid.uuid4())
    
    # Load the image
    img = Image.open(image_path)
    
    # Generate XMP content using the preset generator
    xmp_content = create_preset_from_prompt(style_description)
    
    # Save the XMP file
    xmp_path = os.path.join(XMP_DIR, f"{process_id}.xmp")
    with open(xmp_path, "w") as f:
        f.write(xmp_content)
    
    # Create a basic preview image
    processed_path = os.path.join(PROCESSED_DIR, f"{process_id}.jpg")
    img.save(processed_path, quality=95)
    
    # Create DNG file (in a real implementation, this would be a proper DNG conversion)
    dng_path = os.path.join(DNG_DIR, f"{process_id}.dng")
    with open(dng_path, "wb") as f:
        f.write(b"DNG")  # Placeholder for actual DNG file
    
    return process_id

def generate_lightroom_settings(style_description: str) -> Dict[str, float]:
    """Generate Lightroom-style settings based on the style description."""
    settings = {
        "Exposure": 0.0,
        "Contrast": 0.0,
        "Highlights": 0.0,
        "Shadows": 0.0,
        "Whites": 0.0,
        "Blacks": 0.0,
        "Clarity": 0.0,
        "Vibrance": 0.0,
        "Saturation": 0.0,
        "Temperature": 0.0,
        "Tint": 0.0,
    }
    
    # Convert style description to lowercase for easier matching
    style_lower = style_description.lower()
    
    # Apply settings based on keywords
    if "moody" in style_lower or "dark" in style_lower:
        settings.update({
            "Exposure": -0.5,
            "Contrast": 0.3,
            "Highlights": -0.4,
            "Shadows": -0.2,
            "Blacks": -0.3,
            "Clarity": 0.2,
            "Vibrance": -0.1,
            "Temperature": -0.2,
        })
    
    if "vintage" in style_lower or "film" in style_lower:
        settings.update({
            "Exposure": 0.2,
            "Contrast": 0.4,
            "Highlights": -0.3,
            "Shadows": 0.2,
            "Clarity": 0.3,
            "Vibrance": -0.2,
            "Saturation": -0.1,
            "Temperature": 0.3,
            "Tint": 0.1,
        })
    
    if "dramatic" in style_lower or "high contrast" in style_lower:
        settings.update({
            "Exposure": 0.1,
            "Contrast": 0.6,
            "Highlights": -0.4,
            "Shadows": -0.4,
            "Whites": 0.2,
            "Blacks": -0.2,
            "Clarity": 0.4,
            "Vibrance": 0.2,
        })
    
    if "soft" in style_lower or "dreamy" in style_lower:
        settings.update({
            "Exposure": 0.3,
            "Contrast": -0.2,
            "Highlights": -0.3,
            "Shadows": 0.3,
            "Clarity": -0.2,
            "Vibrance": 0.1,
            "Temperature": 0.1,
        })
    
    if "cinematic" in style_lower:
        settings.update({
            "Exposure": 0.1,
            "Contrast": 0.4,
            "Highlights": -0.3,
            "Shadows": 0.2,
            "Clarity": 0.2,
            "Vibrance": 0.1,
            "Temperature": -0.1,
        })
    
    return settings

def generate_xmp_content(style_description: str, settings: Dict[str, float]) -> str:
    """Generate XMP content with Lightroom settings."""
    # Format settings as XML attributes
    settings_xml = "\n".join([
        f'    <crs:{key}>{value}</crs:{key}>'
        for key, value in settings.items()
    ])
    
    return f'''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c140 79.160451, 2017/05/06-01:08:21">
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">
<rdf:Description rdf:about="">
<dc:description>{style_description}</dc:description>
{settings_xml}
</rdf:Description>
</rdf:RDF>
</x:xmpmeta>'''

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Full Stack App API"}

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    style_description: str = Form(...)
):
    try:
        # Save the original file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the image
        process_id = process_image(file_path, style_description)
        
        # Save metadata
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)
        
        metadata.append({
            "filename": file.filename,
            "style_description": style_description,
            "upload_time": str(datetime.datetime.now()),
            "process_id": process_id
        })
        
        with open(METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "filename": file.filename,
            "style_description": style_description,
            "process_id": process_id,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/")
async def list_files():
    try:
        files = os.listdir(UPLOAD_DIR)
        # Filter out metadata.json
        files = [f for f in files if f != "metadata.json"]
        
        # Load metadata
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)
        
        # Add metadata to response
        files_with_metadata = []
        for file in files:
            file_metadata = next((item for item in metadata if item["filename"] == file), None)
            if file_metadata:
                files_with_metadata.append({
                    "filename": file,
                    "style_description": file_metadata["style_description"],
                    "upload_time": file_metadata["upload_time"],
                    "process_id": file_metadata["process_id"]
                })
        
        return {"files": files_with_metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/processed/{process_id}")
async def get_processed_image(process_id: str):
    try:
        processed_path = os.path.join(PROCESSED_DIR, f"{process_id}.jpg")
        if os.path.exists(processed_path):
            return FileResponse(processed_path)
        raise HTTPException(status_code=404, detail="Processed image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/xmp/{process_id}")
async def download_xmp(process_id: str):
    try:
        xmp_path = os.path.join(XMP_DIR, f"{process_id}.xmp")
        if os.path.exists(xmp_path):
            return FileResponse(
                xmp_path,
                media_type="application/xml",
                filename=f"style_{process_id}.xmp"
            )
        raise HTTPException(status_code=404, detail="XMP file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/dng/{process_id}")
async def download_dng(process_id: str):
    try:
        dng_path = os.path.join(DNG_DIR, f"{process_id}.dng")
        if os.path.exists(dng_path):
            return FileResponse(
                dng_path,
                media_type="image/x-adobe-dng",
                filename=f"style_{process_id}.dng"
            )
        raise HTTPException(status_code=404, detail="DNG file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            # Get process_id from metadata
            with open(METADATA_FILE, "r") as f:
                metadata = json.load(f)
            
            process_id = next((item["process_id"] for item in metadata if item["filename"] == filename), None)
            
            # Delete all related files
            os.remove(file_path)
            if process_id:
                for directory in [PROCESSED_DIR, XMP_DIR, DNG_DIR]:
                    related_file = os.path.join(directory, f"{process_id}.jpg")
                    if os.path.exists(related_file):
                        os.remove(related_file)
            
            # Remove from metadata
            metadata = [item for item in metadata if item["filename"] != filename]
            
            with open(METADATA_FILE, "w") as f:
                json.dump(metadata, f, indent=2)
            
            return {"message": f"File {filename} deleted successfully"}
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_preset/")
async def generate_preset(
    file: UploadFile = File(...),
    style_description: str = Form(...),
    return_preview: bool = Query(True, description="Whether to return a preview image")
):
    """
    Generate a Lightroom preset from an image and style description.
    Returns both the XMP file and a preview image.
    """
    try:
        # Generate a unique ID for this preset
        preset_id = str(uuid.uuid4())
        
        # Read and process the image
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Get the preset settings
        settings = match_prompt_to_preset(style_description)
        
        # Apply the settings to create a preview
        if settings["Exposure"] != 0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.0 + settings["Exposure"])
        
        if settings["Contrast"] != 0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.0 + settings["Contrast"])
        
        if settings["Vibrance"] != 0 or settings["Saturation"] != 0:
            enhancer = ImageEnhance.Color(img)
            saturation_factor = 1.0 + (settings["Vibrance"] + settings["Saturation"]) / 2
            img = enhancer.enhance(saturation_factor)
        
        # Generate XMP content
        xmp_content = create_preset_from_prompt(style_description)
        
        # Save the preview image
        preview_path = os.path.join(PROCESSED_DIR, f"{preset_id}_preview.jpg")
        img.save(preview_path, quality=95)
        
        # Save the XMP file
        xmp_path = os.path.join(XMP_DIR, f"{preset_id}.xmp")
        with open(xmp_path, "w") as f:
            f.write(xmp_content)
        
        # Prepare the response
        response_data = {
            "preset_id": preset_id,
            "style_description": style_description,
            "xmp_url": f"/download/xmp/{preset_id}",
            "preview_url": f"/processed/{preset_id}_preview.jpg" if return_preview else None
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/preset/{preset_id}")
async def download_preset(preset_id: str):
    """
    Download the XMP preset file.
    """
    try:
        xmp_path = os.path.join(XMP_DIR, f"{preset_id}.xmp")
        if os.path.exists(xmp_path):
            return FileResponse(
                xmp_path,
                media_type="application/xml",
                filename=f"preset_{preset_id}.xmp"
            )
        raise HTTPException(status_code=404, detail="Preset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 