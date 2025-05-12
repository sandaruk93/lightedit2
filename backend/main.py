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
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
import re

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

def apply_preset_to_image(image: Image.Image, preset: dict) -> Image.Image:
    """Apply Lightroom-style preset adjustments to an image."""
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Apply basic adjustments
    basic = preset["Basic"]
    
    # Exposure
    if basic["Exposure"] != 0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1 + basic["Exposure"] / 100)
    
    # Contrast
    if basic["Contrast"] != 0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1 + basic["Contrast"] / 100)
    
    # Convert to numpy array for more complex adjustments
    img_array = np.array(image)
    
    # Highlights and Shadows
    if basic["Highlights"] != 0 or basic["Shadows"] != 0:
        # Convert to LAB color space
        lab = Image.fromarray(img_array).convert('LAB')
        l, a, b = lab.split()
        
        # Apply highlights adjustment
        if basic["Highlights"] != 0:
            l_array = np.array(l)
            mask = l_array > 128
            l_array[mask] = np.clip(l_array[mask] * (1 + basic["Highlights"] / 100), 0, 255)
            l = Image.fromarray(l_array.astype(np.uint8))
        
        # Apply shadows adjustment
        if basic["Shadows"] != 0:
            l_array = np.array(l)
            mask = l_array < 128
            l_array[mask] = np.clip(l_array[mask] * (1 + basic["Shadows"] / 100), 0, 255)
            l = Image.fromarray(l_array.astype(np.uint8))
        
        # Merge channels back
        lab = Image.merge('LAB', (l, a, b))
        img_array = np.array(lab.convert('RGB'))
    
    # Temperature and Tint
    if basic["Temperature"] != 0 or basic["Tint"] != 0:
        # Temperature (warm/cool)
        if basic["Temperature"] != 0:
            temp_factor = 1 + basic["Temperature"] / 100
            img_array[:, :, 0] = np.clip(img_array[:, :, 0] * temp_factor, 0, 255)  # Red
            img_array[:, :, 2] = np.clip(img_array[:, :, 2] / temp_factor, 0, 255)  # Blue
        
        # Tint (green/magenta)
        if basic["Tint"] != 0:
            tint_factor = 1 + basic["Tint"] / 100
            img_array[:, :, 1] = np.clip(img_array[:, :, 1] * tint_factor, 0, 255)  # Green
    
    # Vibrance and Saturation
    if basic["Vibrance"] != 0 or basic["Saturation"] != 0:
        # Convert to HSV
        hsv = Image.fromarray(img_array).convert('HSV')
        h, s, v = hsv.split()
        s_array = np.array(s)
        
        # Apply vibrance (affects muted colors more)
        if basic["Vibrance"] != 0:
            mask = s_array < 128
            s_array[mask] = np.clip(s_array[mask] * (1 + basic["Vibrance"] / 100), 0, 255)
        
        # Apply saturation
        if basic["Saturation"] != 0:
            s_array = np.clip(s_array * (1 + basic["Saturation"] / 100), 0, 255)
        
        s = Image.fromarray(s_array.astype(np.uint8))
        hsv = Image.merge('HSV', (h, s, v))
        img_array = np.array(hsv.convert('RGB'))
    
    # Clarity (local contrast)
    if basic["Clarity"] != 0:
        # Convert to grayscale for edge detection
        gray = Image.fromarray(img_array).convert('L')
        gray_array = np.array(gray)
        
        # Apply unsharp mask
        blur = Image.fromarray(gray_array).filter(ImageFilter.GaussianBlur(radius=2))
        blur_array = np.array(blur)
        mask = np.abs(gray_array - blur_array)
        
        # Apply clarity adjustment
        clarity_factor = 1 + basic["Clarity"] / 100
        img_array = np.clip(img_array + (img_array - blur_array[:, :, np.newaxis]) * (clarity_factor - 1), 0, 255)
    
    # Convert back to PIL Image
    result_image = Image.fromarray(img_array.astype(np.uint8))
    
    return result_image

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

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def create_xmp_file(preset_data: dict, xmp_filename: str) -> str:
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

    # Create a pretty XML string
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
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
        
        # Apply preset to image and save preview
        with Image.open(file_path) as img:
            preview_img = apply_preset_to_image(img, preset_data)
            preview_path = UPLOAD_DIR / f"preview_{preset_id}.jpg"
            preview_img.save(preview_path, "JPEG", quality=95)
        
        return {
            "preset_id": preset_id,
            "style_description": style_description,
            "xmp_url": f"/presets/{xmp_filename}",
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