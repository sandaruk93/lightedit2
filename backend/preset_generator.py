from typing import Dict
import re

# Define preset templates for different styles
PRESET_TEMPLATES = {
    "moody": {
        "Exposure": -0.5,
        "Contrast": 0.3,
        "Highlights": -0.4,
        "Shadows": -0.2,
        "Blacks": -0.3,
        "Clarity": 0.2,
        "Vibrance": -0.1,
        "Temperature": -0.2,
        "Tint": 0.0,
        "Saturation": -0.1,
        "Whites": 0.0,
    },
    "vintage": {
        "Exposure": 0.2,
        "Contrast": 0.4,
        "Highlights": -0.3,
        "Shadows": 0.2,
        "Clarity": 0.3,
        "Vibrance": -0.2,
        "Saturation": -0.1,
        "Temperature": 0.3,
        "Tint": 0.1,
        "Whites": 0.1,
        "Blacks": 0.0,
    },
    "dramatic": {
        "Exposure": 0.1,
        "Contrast": 0.6,
        "Highlights": -0.4,
        "Shadows": -0.4,
        "Whites": 0.2,
        "Blacks": -0.2,
        "Clarity": 0.4,
        "Vibrance": 0.2,
        "Temperature": 0.0,
        "Tint": 0.0,
        "Saturation": 0.1,
    },
    "soft": {
        "Exposure": 0.3,
        "Contrast": -0.2,
        "Highlights": -0.3,
        "Shadows": 0.3,
        "Clarity": -0.2,
        "Vibrance": 0.1,
        "Temperature": 0.1,
        "Tint": 0.0,
        "Saturation": 0.0,
        "Whites": 0.0,
        "Blacks": 0.0,
    },
    "cinematic": {
        "Exposure": 0.1,
        "Contrast": 0.4,
        "Highlights": -0.3,
        "Shadows": 0.2,
        "Clarity": 0.2,
        "Vibrance": 0.1,
        "Temperature": -0.1,
        "Tint": 0.0,
        "Saturation": 0.0,
        "Whites": 0.1,
        "Blacks": -0.1,
    }
}

def match_prompt_to_preset(prompt: str) -> Dict[str, float]:
    """
    Match a prompt to the most appropriate preset and return the settings.
    Returns a combination of presets if multiple styles are detected.
    """
    prompt = prompt.lower()
    matched_settings = {
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
    
    # Count how many presets we match
    match_count = 0
    
    # Check for each preset style
    for style, settings in PRESET_TEMPLATES.items():
        if style in prompt:
            match_count += 1
            # Average the settings if multiple matches
            for key in matched_settings:
                matched_settings[key] += settings[key]
    
    # If we found matches, average the settings
    if match_count > 0:
        for key in matched_settings:
            matched_settings[key] /= match_count
    
    return matched_settings

def generate_xmp_content(prompt: str, settings: Dict[str, float]) -> str:
    """
    Generate XMP content with Lightroom settings in the correct XML structure.
    """
    # Format settings as XML attributes
    settings_xml = "\n".join([
        f'    <crs:{key}>{value:.2f}</crs:{key}>'
        for key, value in settings.items()
    ])
    
    return f'''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c140 79.160451, 2017/05/06-01:08:21">
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">
<rdf:Description rdf:about="">
<dc:description>{prompt}</dc:description>
{settings_xml}
</rdf:Description>
</rdf:RDF>
</x:xmpmeta>'''

def create_preset_from_prompt(prompt: str) -> str:
    """
    Main function to create an XMP preset from a prompt.
    Returns the XMP content as a string.
    """
    # Match prompt to preset settings
    settings = match_prompt_to_preset(prompt)
    
    # Generate XMP content
    xmp_content = generate_xmp_content(prompt, settings)
    
    return xmp_content 