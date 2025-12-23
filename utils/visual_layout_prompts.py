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

Seamless Integration Philosophy:
This must look like a professionally composed advertisement photograph where ALL elements feel natural and cohesive:
- Text should feel like an organic part of the scene, not added later
- Elements should complement the background's mood, lighting, and atmosphere
- Use the scene's existing light sources to illuminate text naturally
- Integrate elements within the depth layers of the scene, not floating on top
- Match the scene's color temperature and tonal range

Natural Text Implementation:
Do not render placeholder text literally (no "[LOGO]" text in output). Replace each placeholder using techniques that blend with the scene type:

CRITICAL - NO BACKGROUNDS OR BLOCKS:
- Text must be rendered DIRECTLY on the scene with NO background boxes, containers, or panels
- NO solid color blocks behind text
- NO semi-transparent rectangles or shapes containing text
- NO borders, frames, or outlines around text areas
- Text should be standalone typography that interacts directly with the scene
- If readability is needed, use subtle text shadows or soft glows, NOT background boxes

For NATURE/OUTDOOR scenes:
- Clean, elegant typography rendered directly onto the scene without any background
- Use complementary text colors that contrast naturally with the background
- Subtle drop shadows or soft outer glow for readability (NOT background boxes)
- Position text in areas with natural contrast (light text on darker areas, dark text on lighter areas)
- Text should feel like it's painted or etched into the scene, not placed on top
- Match the scene's golden/warm lighting with appropriate text colors
- Allow background elements (trees, sky, animals) to be visible around text edges

For ARCHITECTURAL/INTERIOR scenes:
- Text integrated as physical signage or environmental graphics
- Metal letters: Brushed finish catching ambient light, soft shadows following scene lighting
- Glass etching: Semi-transparent with scene elements visible behind
- Light projection: Text as projected light on surfaces, following perspective
- Consider surface materials (concrete, glass, wood) when rendering text

For CREATIVE/ARTISTIC scenes:
- Typography that enhances artistic vision without dominating
- NO background blocks - text rendered directly on scene
- Blend modes: text integrates with scene lighting and colors
- Respect composition flow and visual hierarchy
- Text placement that works with (not against) scene elements
- Artistic coherence between background and foreground

Universal Text Quality:
- Sharp, professional typography with clean edges - NO BACKGROUND BLOCKS OR CONTAINERS
- Text rendered directly onto the scene without any backdrop, panel, or box
- Natural shadows or soft glows for readability (subtle drop shadow, NOT background rectangles)
- Color contrast achieved through smart text color selection, not background blocks
- Scale proportional to scene perspective and viewing distance
- Each text element stands alone without geometric shapes or containers behind it

Lighting Unity:
- All text shares the scene's lighting environment
- Text brightness matches scene exposure (not artificially bright against dark backgrounds)
- Text colors harmonize with scene color temperature
- Atmospheric effects (haze, fog, bokeh) affect text naturally
- NO artificial contrast created by background boxes - use natural scene contrast instead

FINAL CHECK:
- Maintain exact spatial positions from reference
- Replace all [PLACEHOLDER] text with specified real-world implementations
- No literal rendering of bracket placeholders
- ABSOLUTELY NO background boxes, blocks, panels, or containers behind any text
- All text rendered directly on the scene without geometric backdrops
- Elements feel naturally integrated into the scene, not collaged on top
- Unified lighting and color temperature across entire composition
- Text and graphics enhance rather than overpower the background
- Professional advertisement quality with seamless composition
- Scene maintains photographic authenticity and artistic coherence
- Text readability achieved through color contrast and subtle shadows, NOT background boxes
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
        mapping["[BRAND NAME]"] = f'"{brand_name}" as clean white or light-colored text rendered directly on the scene without any background box - use elegant sans-serif typography with subtle drop shadow for depth'
    
    if main_message:
        mapping["[MAIN MESSAGE]"] = f'"{main_message}" as clear, readable text integrated directly into the scene without background blocks - choose text color that naturally contrasts with the background area, add soft shadow if needed for clarity'
    
    if tagline:
        mapping["[TAGLINE]"] = f'"{tagline}" as refined text rendered directly on scene without any container - use subtle styling with natural contrast against background'
    
    if cta_text:
        mapping["[CTA]"] = f'"{cta_text}" displayed on a clean, simple button with rounded edges and solid fill (white or light color) - the button itself should blend naturally with the scene, avoiding harsh geometric shapes'
    
    return mapping


def get_scene_style_guidance(style, color_scheme):
    """
    Get default scene descriptions (used as fallback when no custom instructions provided)
    
    Args:
        style: Visual style
        color_scheme: Color palette
    
    Returns:
        Default scene description text (use only if user provides no custom instructions)
    """
    
    # These are DEFAULT examples - only use when user doesn't provide custom instructions
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
