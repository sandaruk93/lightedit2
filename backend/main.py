from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import csv

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
CONFIG_DIR = Path("config")
UPLOAD_DIR.mkdir(exist_ok=True)
PRESET_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# Default preset values if CSV is not available
DEFAULT_PRESETS = {
    "cinematic": {
        "Basic": {
            "Exposure": 0.2,
            "Contrast": 15,
            "Highlights": -20,
            "Shadows": 10,
            "Clarity": 10,
            "Vibrance": 5,
            "Temperature": 10,
            "Tint": 2
        },
        "ToneCurve": {
            "Enabled": True,
            "Points": [[0, 0], [64, 60], [192, 200], [255, 255]]
        },
        "SplitToning": {
            "Enabled": True,
            "HighlightHue": 45,
            "HighlightSaturation": 10,
            "ShadowHue": 215,
            "ShadowSaturation": 15,
            "Balance": 25
        }
    },
    # ... other default presets ...
}

def load_preset_configs() -> Dict[str, dict]:
    """Load preset configurations from CSV file."""
    config_path = CONFIG_DIR / "presets.csv"
    if not config_path.exists():
        return DEFAULT_PRESETS

    presets = {}
    try:
        with open(config_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                preset_name = row['preset_name'].lower()
                presets[preset_name] = {
                    "Basic": {
                        "Exposure": float(row.get('exposure', 0)),
                        "Contrast": int(row.get('contrast', 0)),
                        "Highlights": int(row.get('highlights', 0)),
                        "Shadows": int(row.get('shadows', 0)),
                        "Whites": int(row.get('whites', 0)),
                        "Blacks": int(row.get('blacks', 0)),
                        "Clarity": int(row.get('clarity', 0)),
                        "Vibrance": int(row.get('vibrance', 0)),
                        "Saturation": int(row.get('saturation', 0)),
                        "Temperature": int(row.get('temperature', 0)),
                        "Tint": int(row.get('tint', 0))
                    },
                    "ToneCurve": {
                        "Enabled": True,
                        "Points": [
                            [0, 0],
                            [int(row.get('curve_midpoint', 128)), int(row.get('curve_midvalue', 128))],
                            [255, 255]
                        ]
                    },
                    "SplitToning": {
                        "Enabled": True,
                        "HighlightHue": int(row.get('highlight_hue', 0)),
                        "HighlightSaturation": int(row.get('highlight_saturation', 0)),
                        "ShadowHue": int(row.get('shadow_hue', 0)),
                        "ShadowSaturation": int(row.get('shadow_saturation', 0)),
                        "Balance": int(row.get('split_toning_balance', 0))
                    },
                    "ColorAdjustments": {
                        "Enabled": True,
                        "Adjustments": row.get('color_adjustments', 'None')
                    }
                }
        return presets
    except Exception as e:
        print(f"Error loading preset configs: {e}")
        return DEFAULT_PRESETS

def generate_xmp_preset(style_description: str) -> dict:
    """Generate Lightroom preset values based on style description."""
    # Load preset configurations
    presets = load_preset_configs()
    
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
            "Points": [[0, 0], [255, 255]]
        },
        "SplitToning": {
            "Enabled": True,
            "HighlightHue": 0,
            "HighlightSaturation": 0,
            "ShadowHue": 0,
            "ShadowSaturation": 0,
            "Balance": 0
        }
    }

    # Find the best matching preset
    style_lower = style_description.lower()
    best_match = None
    best_score = 0

    for preset_name in presets:
        if preset_name in style_lower:
            best_match = preset_name
            break

    if best_match:
        # Apply the matching preset
        preset["Basic"].update(presets[best_match]["Basic"])
        preset["ToneCurve"] = presets[best_match]["ToneCurve"]
        preset["SplitToning"] = presets[best_match]["SplitToning"]

    return preset

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def create_xmp_file(preset_data: dict, xmp_filename: str) -> str:
    # Create the root element with dc namespace
    root = ET.Element("x:xmpmeta", {
        "xmlns:x": "adobe:ns:meta/",
        "x:xmptk": "Adobe XMP Core 5.6-c140 79.160451, 2017/05/06-01:08:21",
        "xmlns:dc": "http://purl.org/dc/elements/1.1/"
    })
    
    # Create the RDF element
    rdf = ET.SubElement(root, "rdf:RDF", {
        "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xmlns:crs": "http://ns.adobe.com/camera-raw-settings/1.0/"
    })
    
    # Create the Description element with Lightroom expected tags
    desc = ET.SubElement(rdf, "rdf:Description", {
        "rdf:about": "",
        "crs:PresetType": "Normal",
        "crs:Cluster": "",
        "crs:UUID": str(uuid.uuid4()),
        "crs:SupportsAmount": "False",
        "crs:RequiresRGBTables": "False",
        "crs:Group": "User Presets",
        "crs:Name": f"Preset_{xmp_filename}",
        "crs:Version": "13.0",
        "crs:ProcessVersion": "11.0"
    })

    # Map to Lightroom's expected tags
    basic = preset_data["Basic"]
    desc.set("crs:Exposure2012", str(basic["Exposure"]))
    desc.set("crs:Contrast2012", str(basic["Contrast"]))
    desc.set("crs:Highlights2012", str(basic["Highlights"]))
    desc.set("crs:Shadows2012", str(basic["Shadows"]))
    desc.set("crs:Whites2012", str(basic.get("Whites", 0)))
    desc.set("crs:Blacks2012", str(basic.get("Blacks", 0)))
    desc.set("crs:Clarity2012", str(basic["Clarity"]))
    desc.set("crs:Vibrance", str(basic["Vibrance"]))
    desc.set("crs:Saturation", str(basic["Saturation"]))
    desc.set("crs:Temperature", str(basic["Temperature"]))
    desc.set("crs:Tint", str(basic["Tint"]))

    # Add color adjustments if present
    if "ColorAdjustments" in preset_data and preset_data["ColorAdjustments"]["Enabled"]:
        color_adjustments = preset_data["ColorAdjustments"]["Adjustments"]
        if color_adjustments != "None":
            # Parse color adjustments string and set HSL values
            adjustments = color_adjustments.split(", ")
            for adjustment in adjustments:
                if ":" in adjustment:
                    color, value = adjustment.split(":")
                    if color == "All":
                        # Apply to all colors
                        for c in ["Red", "Orange", "Yellow", "Green", "Aqua", "Blue", "Purple", "Magenta"]:
                            desc.set(f"crs:Hue{c}", value)
                    else:
                        # Apply to specific color
                        desc.set(f"crs:Hue{color}", value)

    # Debug print the XML string
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    print("\n--- XMP XML DEBUG ---\n", xml_str, "\n--- END XMP XML DEBUG ---\n")
    
    # Save the XMP file
    xmp_path = PRESET_DIR / xmp_filename
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
        
        # Prepare XMP file name
        original_name = os.path.splitext(file.filename)[0]
        preset_slug = slugify(style_description)
        xmp_filename = f"{original_name}-preset-{preset_slug}.xmp"
        
        # Create XMP file
        xmp_path = create_xmp_file(preset_data, xmp_filename)
        
        return {
            "preset_id": preset_id,
            "style_description": style_description,
            "xmp_url": f"/presets/{xmp_filename}",
            "preview_url": f"/uploads/{preset_id}_{file.filename}"
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
