"""
Centralized prompt templates for AI-native and overlay mode generation
Based on Google Gemini best practices for high-fidelity text rendering

MODE SEPARATION:
- AI-NATIVE MODE: AI renders text as physical scene elements (get_ai_native_prompt)
- OVERLAY MODE: AI generates background only, text added via PIL (get_overlay_mode_prompt)

This file handles template-based generation only.
Non-template prompts are managed in prompts.py (PromptBuilder class).
"""

def get_ai_native_prompt(
    content_prompt,
    width,
    height,
    template_style,
    design_rules,
    text_elements,
    has_logo=False
):
    """
    AI-native prompt optimized for Gemini 3 Pro Image (Nano Banana Pro).
    Uses "Diegetic" prompt engineering: text as physical assets with material anchors.
    Narrative "Director's Vision" approach instead of numbered lists.
    """

    # Base scene description (narrative, not keywords)
    base_scene = (
        content_prompt.strip()
        if content_prompt
        else "a sophisticated commercial space showcasing modern brand architecture"
    )

    # Priority sorting for hierarchical composition
    priority_order = {"highest": 0, "high": 1, "medium": 2, "low": 3}
    sorted_elements = sorted(
        text_elements,
        key=lambda x: priority_order.get(x.get("priority", "medium"), 2),
    )

    # Build narrative prompt with material anchors (Gemini's recommended approach)
    base_prompt = f"""
A professional commercial wide-angle photograph of {base_scene}, captured at {width}x{height}px resolution. This is a real physical environment with {template_style.get('style', 'modern')} architecture, shot on a 35mm lens at f/2.8 for natural depth of field with three-point lighting setup.

**ENVIRONMENTAL BRANDING:**
This scene features permanent architectural branding integrated into the physical space. All text exists as tangible materials—not digital overlays or graphics. The letters have mass, texture, and depth. They cast subtle shadows onto the surfaces behind them. Light from the environment hits the edges and faces of the text, creating realistic highlights and shadow gradients.

"""

    # Add text elements with material anchor descriptions
    if sorted_elements:
        base_prompt += "**PHYSICAL TEXT INSTALLATIONS:**\n\n"
        
        for i, elem in enumerate(sorted_elements, 1):
            content = elem['content']
            priority = elem['priority']
            placement = elem.get('placement_hint', 'prominent architectural surface')
            integration = elem.get('integration', 'mounted signage')
            style_hint = elem.get('style_hint', '')
            elem_type = elem.get('type', 'text')
            
            # Convert generic "CTA" to physical descriptions
            is_cta = elem_type == "cta" or "call" in integration.lower() or "cta" in integration.lower()
            
            # Material anchor: specific physical description
            if is_cta:
                # Avoid "CTA button" - use physical alternatives
                material_desc = "small vinyl lettering applied directly to a glass surface or subtle directory sign text"
                physical_nature = "These letters are tiny, understated, and non-digital—like the kind you'd see on a building directory or etched into frosted glass"
            elif priority == "highest":
                # Main message gets dramatic treatment
                material_desc = f"letters constructed from {style_hint if style_hint else 'white neon tubes mounted to concrete'}"
                physical_nature = f"These letters are 3D objects, 6-8 inches deep, that protrude from the {placement}. Each letter casts a distinct shadow with soft penumbral edges. The material has texture and reflectivity"
            elif priority == "high":
                # Brand name gets premium materials
                material_desc = f"{style_hint if style_hint else 'brushed-metal letters pinned 2 inches off a smooth surface'}"
                physical_nature = "These dimensional letters create separation from the wall, with shadows falling naturally based on the scene's light sources. The metal catches highlights from environmental lighting"
            else:
                # Supporting text is subtle
                material_desc = f"{style_hint if style_hint else 'subtle etched or embossed lettering'}"
                physical_nature = "This text is minimally raised or recessed, integrated seamlessly into the architectural surface"
            
            base_prompt += f"{i}. \"{content}\"\n"
            base_prompt += f"   Location: {placement}\n"
            base_prompt += f"   Material: {material_desc}\n"
            base_prompt += f"   Integration: {integration}\n"
            base_prompt += f"   Physical Nature: {physical_nature}\n"
            
            # The "Shadow Trick" - force 3D treatment
            if priority in ["highest", "high"]:
                base_prompt += f"   Lighting Response: The text \"{content}\" must cast visible shadows onto the surface behind it. "
                base_prompt += f"The shadows should be soft-edged and follow the perspective of the scene. "
                base_prompt += f"If there's a reflective floor, the letters should show subtle reflections.\n"
            
            base_prompt += f"   CRITICAL: Spell exactly as \"{content}\" with perfect accuracy.\n\n"

    # Logo handling if needed
    if has_logo:
        base_prompt += """**LOGO SPACE RESERVATION:**
Create a clean, well-lit area with appropriate architectural context where a logo will be overlaid post-generation. This space should have realistic lighting and surface texture that will make an overlaid logo feel naturally integrated. Do not generate any logo yourself—just ensure the lighting, surface material, and composition in that area will complement a later logo addition. Think of it as a prepared mounting surface.

"""

    # Design principles as narrative guidance
    if design_rules:
        base_prompt += "**SCENE PHILOSOPHY:**\n"
        for rule in design_rules:
            base_prompt += f"{rule.lower()} "
        base_prompt += "\n\n"

    # Final quality requirements using narrative style (avoiding prohibitions)
    base_prompt += """**PHOTOGRAPHIC REQUIREMENTS:**

Lighting & Atmosphere: Unified lighting across all elements from the same light sources. The text materials respond to light realistically—metal reflects, neon glows, vinyl appears matte. Use atmospheric depth with subtle depth of field, light rays, or ambient occlusion. Every surface should feel lit by practical lights within the scene.

Spatial Coherence: Maintain perfect perspective consistency. The text follows the same vanishing points as the architecture. If a wall recedes into the distance, text on that wall must also recede at the same angle. All elements exist in proper spatial relationships with believable depth and layering.

Material Authenticity: The text is made of real materials with appropriate physical properties. Metal text has brushed texture and edge highlights. Neon has soft glow falloff. Vinyl has slight matte finish. Embossed text has subtle depth variation. Each material interacts with light correctly—reflections, refractions, shadows.

Shadow Integration: Text must cast shadows appropriate to its depth and the scene's lighting. A letter 6 inches from the wall casts a different shadow than one flush against it. Shadows have soft penumbral edges and follow perspective. If there's floor reflectivity, dimensional text shows subtle reflections.

Photographic Authenticity: This must look like an unedited photograph of a real space—not a mockup, composite, or digital rendering. Everything should feel intentional and professionally installed. The highest priority text dominates the composition naturally through scale, placement, and lighting, not through artificial emphasis.

**FINAL CHECK:** Avoid digital overlays; the image must look like a raw photograph taken in a real physical space. No floating UI elements. No rounded black rectangles. No graphic design buttons. Only physical architectural elements with text existing as tangible, three-dimensional materials that cast shadows and respond to light.

Spell all text exactly as specified above with perfect accuracy.
"""

    return base_prompt




def get_overlay_mode_prompt(content_prompt, width, height, template_style, spatial_guidance, zone_styles):
    """
    Generate prompt for overlay mode where text is added via PIL after background generation
    
    Args:
        content_prompt: User's content description
        width, height: Image dimensions
        template_style: Dict with style and color_scheme
        spatial_guidance: List of zone descriptions
        zone_styles: List of zone-specific styling hints
    
    Returns:
        Complete prompt string for background generation
    """
    base_prompt = f"{content_prompt}\n\n**COMPOSITION GUIDELINES:**\n"
    
    # Add zone-specific styling if available
    if zone_styles:
        base_prompt += f"**ZONE STYLING:**\n"
        for zone_style in zone_styles:
            base_prompt += f"- {zone_style}\n"
        base_prompt += f"\n**CRITICAL INTEGRATION REQUIREMENTS:**\n"
        base_prompt += f"- Create visual space and context in each zone where elements will appear\n"
        base_prompt += f"- In zones with 'blended' style: use soft lighting, subtle textures, and gentle color transitions\n"
        base_prompt += f"- In zones with 'prominent' style: create visual anchors or frames using light, shadow, or environmental elements\n"
        base_prompt += f"- Design the scene so text/logos appear to be part of the 3D environment (like signs, projections, or integrated displays)\n"
        base_prompt += f"- Add environmental lighting sources (windows, lamps, glow) that will realistically illuminate overlaid elements\n"
        base_prompt += f"- Create depth layers: foreground objects, middle ground (where text lives), and background elements\n"
        base_prompt += f"- Use atmospheric effects (fog, light rays, bokeh) to blend overlaid elements into the scene\n"
        base_prompt += f"- Ensure color grading and tone will make white/colored text feel naturally lit by the scene's light sources\n"
        base_prompt += f"- NO text, letters, or typography in the generated image - text will be added as natural overlays\n"
    elif spatial_guidance:
        unique_zones = list(set(spatial_guidance))
        zones_text = ", ".join(unique_zones)
        base_prompt += f"- Text and UI elements will be overlaid in these areas: {zones_text}\n"
        base_prompt += f"- In these zones, use softer colors, subtle patterns, or blurred backgrounds to ensure text readability\n"
        base_prompt += f"- Place main visual interest and detailed elements in areas that won't have text overlay\n"
        base_prompt += f"- Create depth and lighting that will make overlaid text appear naturally integrated into the scene\n"
    else:
        base_prompt += f"- Keep visual elements balanced and not overly busy, as text and other elements will be overlaid\n"
    
    base_prompt += f"- Use color gradients and depth that complement text placement without competing\n"
    base_prompt += f"- Ensure the background style harmonizes with overlaid elements for a cohesive, professional look\n"
    base_prompt += f"- Create visual flow that guides the eye naturally around the placement of text elements\n"
    base_prompt += f"- Design lighting and atmosphere that will make overlaid elements feel like they belong in the scene, not pasted on top"
    
    return base_prompt
