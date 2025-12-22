"""
Visual Layout Generator Prompts
Separate from template system - uses reference image placeholders
"""

def get_visual_layout_prompt(elements_mapping, scene_description, style, color_scheme, dimensions):
    """
    Generate prompt for visual layout method using reference image with placeholders
    
    Args:
        elements_mapping: Dict of placeholder -> actual content/instruction
            e.g., {"[LOGO]": "Reserve space", "[BRAND]": "Mosaic as metal letters"}
        scene_description: User's scene description
        style: Visual style (modern, minimalist, etc.)
        color_scheme: Color palette
        dimensions: (width, height) tuple
    
    Returns:
        Complete prompt for generation with reference image
    """
    
    base_prompt = f"""
REFERENCE IMAGE INSTRUCTION:
Use the uploaded reference image as the EXACT composition guide. The reference shows a layout with placeholder labels in [BRACKETS].

SCENE TYPE:
{scene_description if scene_description else "A professional commercial photograph of a modern architectural space"}

PHOTOGRAPHIC SETUP:
Shot at {dimensions[0]}x{dimensions[1]}px using a 35mm lens at f/2.8 for natural depth of field. Professional three-point lighting with soft shadows. {style} aesthetic with {color_scheme} color palette.

PLACEHOLDER REPLACEMENT INSTRUCTIONS:
The reference image contains placeholder text in [BRACKETS]. Replace each placeholder with the specified real-world element, maintaining the EXACT position, scale, and perspective shown in the reference:

"""

    # Add each element's replacement instruction
    for placeholder, instruction in elements_mapping.items():
        base_prompt += f"\n• {placeholder} → {instruction}"
    
    base_prompt += """

CRITICAL REQUIREMENTS:

Spatial Accuracy:
Maintain the EXACT spatial layout from the reference image. Each element must appear in the same position, with the same scale and perspective as shown. The reference defines the composition—do not deviate from these positions.

Material & Physics:
All text exists as physical 3D materials integrated into the architecture:
- Dimensional letters cast realistic shadows with soft penumbral edges
- Materials respond to lighting (metal reflects, neon glows, vinyl is matte)
- Shadows follow the scene's perspective and light sources
- If there's floor reflectivity, dimensional elements show subtle reflections

Text as Architecture:
Do not render placeholder text literally (no "[LOGO]" text in output). Instead, replace each placeholder with the specified real-world implementation. Text should look like professionally installed architectural signage:
- Metal letters: Brushed finish, mounted 2-3 inches from surface, catching edge highlights
- Neon text: Individual tube letters with soft glow falloff, warm white or colored gas
- Vinyl text: Flat application directly on glass/smooth surface, matte finish
- Embossed: Subtle depth variation, highlight on raised edges

Photography Quality:
This must look like an unedited photograph of a real space:
- Unified lighting from practical sources (windows, lamps, ambient)
- Natural depth of field with subtle background blur
- Atmospheric effects (light rays, ambient occlusion)
- Proper perspective with consistent vanishing points
- No floating UI elements, no digital buttons, no graphic overlays

Shadow Integration:
Text elements must cast shadows appropriate to their depth:
- Letters 2-6 inches from wall: soft-edged shadows with visible penumbra
- Flush text (vinyl): minimal to no shadow
- Backlit neon: glow halo instead of traditional shadow
- All shadows follow perspective and match scene lighting direction

Material Authenticity:
- Metal: Brushed texture, edge highlights, anisotropic reflections
- Neon: Soft warm glow, slight oversaturation at edges, tube thickness visible
- Vinyl: Matte surface, crisp edges, no reflections
- Glass etching: Semi-transparent with light diffusion

FINAL CHECK:
- Maintain exact spatial positions from reference
- Replace all [PLACEHOLDER] text with specified real-world implementations
- No literal rendering of bracket placeholders
- All text exists as physical architectural elements
- Shadows and lighting are physically accurate
- Scene looks like unedited professional photography
"""

    return base_prompt


def get_placeholder_replacement_map(logo_space=False, brand_name="", main_message="", tagline="", cta_text=""):
    """
    Generate the mapping of placeholders to actual content
    
    Args:
        logo_space: Whether to reserve logo space
        brand_name: Client/brand name
        main_message: Main advertising message
        tagline: Company tagline
        cta_text: Call-to-action text
    
    Returns:
        Dict mapping placeholders to instructions
    """
    
    mapping = {}
    
    if logo_space:
        mapping["[LOGO]"] = "Reserve a clean, well-lit area with subtle surface texture for logo overlay (do not generate logo text or graphics)"
    
    if brand_name:
        mapping["[BRAND NAME]"] = f'"{brand_name}" rendered as brushed-metal dimensional letters mounted 2 inches off the surface, catching environmental light on edges, casting soft shadows'
    
    if main_message:
        mapping["[MAIN MESSAGE]"] = f'"{main_message}" constructed from individual white neon tubes mounted to concrete or textured wall, with soft warm glow and visible tube thickness'
    
    if tagline:
        mapping["[TAGLINE]"] = f'"{tagline}" as subtle embossed or etched text, minimally raised from surface, integrated seamlessly into architectural material'
    
    if cta_text:
        mapping["[CTA]"] = f'"{cta_text}" as small vinyl lettering applied directly to glass surface or frosted partition, matte finish, understated and non-digital'
    
    return mapping


def get_scene_style_guidance(style, color_scheme):
    """
    Get style-specific scene descriptions
    
    Args:
        style: Visual style
        color_scheme: Color palette
    
    Returns:
        Scene description text
    """
    
    style_descriptions = {
        "modern & minimalist": "a clean, minimalist architectural interior with concrete walls, large windows, and geometric simplicity",
        "modern": "a contemporary space with clean lines, natural materials, and balanced composition",
        "luxury": "an upscale interior with premium materials, dramatic lighting, and sophisticated design",
        "professional": "a corporate environment with professional finishes, neutral tones, and refined details",
        "creative": "an artistic space with unique architectural features, interesting textures, and creative lighting"
    }
    
    color_descriptions = {
        "brand colors": "using the brand's established color palette integrated naturally into materials and lighting",
        "monochrome": "with a sophisticated monochromatic palette featuring gradients from deep blacks to bright whites",
        "warm tones": "featuring warm color temperature with amber lighting, wood tones, and inviting atmosphere",
        "cool tones": "with cool color palette featuring blues, grays, and crisp white lighting",
        "vibrant": "incorporating bold, saturated colors through lighting, materials, and architectural accents"
    }
    
    style_key = style.lower() if style else "modern"
    color_key = color_scheme.lower() if color_scheme else "brand colors"
    
    scene = style_descriptions.get(style_key, style_descriptions["modern"])
    colors = color_descriptions.get(color_key, color_descriptions["brand colors"])
    
    return f"{scene}, {colors}"
