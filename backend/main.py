from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import json
from datetime import datetime
from typing import Optional
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
PRESET_DIR = Path("presets")
UPLOAD_DIR.mkdir(exist_ok=True)
PRESET_DIR.mkdir(exist_ok=True)

def generate_xmp_preset(style_description: str) -> dict:
    """Generate Lightroom preset values based on style description."""
    # Base preset values
    preset = {
        "Basic": {
            "Exposure": 0.0,
            "Contrast": 0,
            "Highlights": 0,
            "Shadows": 0,
            "Whites": 0,
            "Blacks": 0,
            "Clarity": 0,
            "Vibrance": 0,
            "Saturation": 0,
            "Temperature": 0,
            "Tint": 0
        },
        "ToneCurve": {
            "Enabled": True,
            "Points": [
                [0, 0],
                [255, 255]
            ]
        },
        "HSL": {
            "Hue": {
                "Red": 0,
                "Orange": 0,
                "Yellow": 0,
                "Green": 0,
                "Aqua": 0,
                "Blue": 0,
                "Purple": 0,
                "Magenta": 0
            },
            "Saturation": {
                "Red": 0,
                "Orange": 0,
                "Yellow": 0,
                "Green": 0,
                "Aqua": 0,
                "Blue": 0,
                "Purple": 0,
                "Magenta": 0
            },
            "Luminance": {
                "Red": 0,
                "Orange": 0,
                "Yellow": 0,
                "Green": 0,
                "Aqua": 0,
                "Blue": 0,
                "Purple": 0,
                "Magenta": 0
            }
        },
        "SplitToning": {
            "Enabled": True,
            "HighlightHue": 0,
            "HighlightSaturation": 0,
            "ShadowHue": 0,
            "ShadowSaturation": 0,
            "Balance": 0
        },
        "Detail": {
            "Sharpness": 0,
            "LuminanceSmoothing": 0,
            "ColorNoiseReduction": 0
        }
    }

    # Apply style-specific adjustments based on the description
    style_lower = style_description.lower()
    
    if "cinematic" in style_lower:
        preset["Basic"].update({
            "Contrast": 15,
            "Highlights": -20,
            "Shadows": 10,
            "Clarity": 10,
            "Vibrance": 5,
            "Temperature": 5
        })
        preset["ToneCurve"]["Points"] = [
            [0, 0],
            [64, 60],
            [192, 200],
            [255, 255]
        ]
        preset["SplitToning"].update({
            "HighlightHue": 45,
            "HighlightSaturation": 10,
            "ShadowHue": 215,
            "ShadowSaturation": 15
        })

    elif "vintage" in style_lower:
        preset["Basic"].update({
            "Exposure": 0.5,
            "Contrast": 10,
            "Highlights": -15,
            "Shadows": 15,
            "Clarity": -5,
            "Vibrance": -10,
            "Saturation": -15,
            "Temperature": 10
        })
        preset["ToneCurve"]["Points"] = [
            [0, 0],
            [85, 90],
            [170, 160],
            [255, 255]
        ]
        preset["SplitToning"].update({
            "HighlightHue": 40,
            "HighlightSaturation": 20,
            "ShadowHue": 200,
            "ShadowSaturation": 10
        })

    elif "dramatic" in style_lower:
        preset["Basic"].update({
            "Exposure": -0.5,
            "Contrast": 25,
            "Highlights": -30,
            "Shadows": 20,
            "Clarity": 15,
            "Vibrance": 10,
            "Temperature": -5
        })
        preset["ToneCurve"]["Points"] = [
            [0, 0],
            [64, 50],
            [192, 210],
            [255, 255]
        ]
        preset["SplitToning"].update({
            "HighlightHue": 30,
            "HighlightSaturation": 15,
            "ShadowHue": 210,
            "ShadowSaturation": 20
        })

    elif "dreamy" in style_lower:
        preset["Basic"].update({
            "Exposure": 0.5,
            "Contrast": -10,
            "Highlights": -20,
            "Shadows": 15,
            "Clarity": -10,
            "Vibrance": 5,
            "Temperature": 5
        })
        preset["ToneCurve"]["Points"] = [
            [0, 0],
            [85, 95],
            [170, 165],
            [255, 255]
        ]
        preset["SplitToning"].update({
            "HighlightHue": 45,
            "HighlightSaturation": 15,
            "ShadowHue": 220,
            "ShadowSaturation": 10
        })

    return preset

def create_xmp_file(preset_data: dict, preset_id: str) -> str:
    """Create an XMP file with the preset data."""
    # Create the root element
    root = ET.Element("x:xmpmeta", {
        "xmlns:x": "adobe:ns:meta/",
        "x:xmptk": "Adobe XMP Core 5.6-c140 79.160451, 2017/05/06-01:08:21"
    })
    
    # Create the RDF element
    rdf = ET.SubElement(root, "rdf:RDF", {
        "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xmlns:crs": "http://ns.adobe.com/camera-raw-settings/1.0/"
    })
    
    # Create the Description element
    desc = ET.SubElement(rdf, "rdf:Description", {
        "rdf:about": "",
        "crs:PresetType": "Normal",
        "crs:Cluster": "",
        "crs:UUID": str(uuid.uuid4()),
        "crs:SupportsAmount": "False",
        "crs:RequiresRGBTables": "False",
        "crs:Group": "User Presets",
        "crs:Name": f"Preset_{preset_id}"
    })
    
    # Add all preset values
    for section, values in preset_data.items():
        for key, value in values.items():
            if isinstance(value, (int, float, bool)):
                desc.set(f"crs:{section}{key}", str(value).lower())
            elif isinstance(value, list):
                # Handle tone curve points
                if key == "Points":
                    for i, point in enumerate(value):
                        desc.set(f"crs:{section}{key}{i}", f"{point[0]},{point[1]}")
    
    # Create a pretty XML string
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
    # Save the XMP file
    xmp_path = PRESET_DIR / f"preset_{preset_id}.xmp"
    with open(xmp_path, "w") as f:
        f.write(xml_str)
    
    return str(xmp_path)

@app.post("/generate_preset/")
async def generate_preset(
    file: UploadFile = File(...),
    style_description: str = Form(...)
):
    try:
        # Generate a unique ID for this preset
        preset_id = str(uuid.uuid4())
        
        # Save the uploaded file
        file_path = UPLOAD_DIR / f"{preset_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate preset values
        preset_data = generate_xmp_preset(style_description)
        
        # Create XMP file
        xmp_path = create_xmp_file(preset_data, preset_id)
        
        # For now, we'll just copy the original image as the preview
        # In a real implementation, you would process the image with the preset
        preview_path = UPLOAD_DIR / f"preview_{preset_id}.jpg"
        shutil.copy(file_path, preview_path)
        
        return {
            "preset_id": preset_id,
            "style_description": style_description,
            "xmp_url": f"/presets/preset_{preset_id}.xmp",
            "preview_url": f"/uploads/preview_{preset_id}.jpg"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/presets/{filename}")
async def get_preset(filename: str):
    preset_path = PRESET_DIR / filename
    if not preset_path.exists():
        raise HTTPException(status_code=404, detail="Preset not found")
    return FileResponse(preset_path)

@app.get("/uploads/{filename}")
async def get_upload(filename: str):
    upload_path = UPLOAD_DIR / filename
    if not upload_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(upload_path)

@app.get("/files/")
async def list_files():
    files = []
    for file in UPLOAD_DIR.glob("*.jpg"):
        files.append({
            "filename": file.name,
            "style_description": "Generated preset",  # In a real app, store this in a database
            "upload_time": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
        })
    return {"files": files}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    file_path.unlink()
    return {"message": "File deleted successfully"} 