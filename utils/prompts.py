"""
Centralized Prompt Management System
Contains all AI prompts used throughout the application for easy editing and maintenance
"""

class PromptTemplates:
    """Centralized storage for all AI generation prompts"""
    
    # Template Background Generation Prompts
    # NOTE: This is ONLY for OVERLAY MODE (template_prompts.py handles AI-NATIVE mode)
    TEMPLATE_BACKGROUND_BASE = """
    Create a clean, professional advertisement background design for OVERLAY MODE.
    Style: {style}
    Color scheme: {color_scheme}
    Theme inspiration: {theme_keywords}
    
    OVERLAY MODE REQUIREMENTS:
    - Dimensions: {width}x{height} pixels
    - Create BACKGROUND ONLY - absolutely no text, logos, or readable content
    - Use {color_scheme} color palette with {style} aesthetic
    - Include subtle visual elements that suggest: {theme_keywords}
    - Create depth with gradients, lighting effects, and abstract shapes
    - Design must support text overlay without visual conflicts
    
    OVERLAY MODE RESTRICTIONS:
    - NO text, letters, words, numbers, or symbols of any kind
    - NO company names, logos, or brand elements
    - NO prices, percentages, sale announcements, or promotional text
    - NO readable content whatsoever
    - Create ABSTRACT background that suggests the theme through color and mood only
    
    TEMPLATE OVERLAY ZONES (keep completely clear):
    - Logo placement: top-left area ({logo_width}x{logo_height} pixels)
    - Company name area: space reserved for text overlay
    - Main message area: central space for promotional content
    - Call-to-action area: button placement zone
    
    Create an atmospheric, text-free background that complements {theme_keywords} through visual mood and {color_scheme} colors only.
    The template system will add all text, logos, and promotional content as overlays.
    
    NOTE: This prompt is for OVERLAY mode only. AI-native cinematic templates use a different prompting system (template_prompts.py).
    """
    
    # Enhanced Prompt Building for Non-Template Generation
    ENHANCED_PROMPT_BASE = "Create a professional advertisement for {client_name}. The company name '{client_name}' must be prominently displayed as the main brand element."
    
    # Company name requirements
    COMPANY_NAME_REQUIREMENTS = [
        "CRITICAL: The company name '{client_name}' must be clearly visible and prominent in the advertisement.",
        "Display '{client_name}' as the primary brand element with large, readable typography.",
        "Position the company name '{client_name}' prominently in the upper portion of the design.",
        "Use high contrast colors to ensure '{client_name}' stands out against the background."
    ]
    
    # Medium-specific enhancements
    MEDIUM_ENHANCEMENTS = {
        "billboard": "Create bold, high-impact design optimized for large-scale outdoor display. Use large, readable typography with maximum contrast and minimal text elements. Focus on simple, powerful visual hierarchy that works at distance viewing.",
        "outdoor": "Create bold, high-impact design optimized for large-scale outdoor display. Use large, readable typography with maximum contrast and minimal text elements. Focus on simple, powerful visual hierarchy that works at distance viewing.",
        "social media": "Create engaging design optimized for mobile social media feeds. Use attention-grabbing visuals with clear focal points for thumb-stopping appeal.",
        "web": "Create clean web-optimized design with clear clickable visual elements.",
        "banner": "Create clean web-optimized design with clear clickable visual elements.",
        "default": "Create professional advertisement design for {medium} format."
    }
    
    # Style and visual guidance
    STYLE_GUIDANCE = "Style: {style} with professional execution."
    
    # Color scheme guidance
    COLOR_SCHEME_GUIDANCE = {
        "brand colors": "Color scheme: Use {client_name}'s brand colors for consistency and recognition.",
        "default": "Color scheme: {color_scheme}."
    }
    
    # Format guidance based on dimensions
    FORMAT_GUIDANCE = {
        "square": "Format: Square design ({width}x{height} pixels) with centered composition.",
        "landscape": "Format: Landscape design ({width}x{height} pixels) with horizontal layout.",
        "portrait": "Format: Portrait design ({width}x{height} pixels) with vertical layout."
    }
    
    # Typography guidance
    TYPOGRAPHY_GUIDANCE = {
        "billboard": "Typography: Bold, minimal text with high readability and clear hierarchy.",
        "default": "Typography: Attractive text elements with clear information hierarchy."
    }
    
    # Call-to-action guidance
    CTA_GUIDANCE = {
        "with_website_billboard": "Include prominent call-to-action text directing to {website}.",
        "with_website_default": "Include clear call-to-action button directing to {website}.",
        "without_website": "Include clear call-to-action element."
    }
    
    # Final quality guidelines
    QUALITY_GUIDELINES = {
        "base": [
            "Create flat advertisement design, not a mockup or 3D visualization.",
            "Design should be the actual advertisement content, ready for use.",
            "MUST include the actual company name '{client_name}' prominently in the design.",
            "DO NOT add fake or generic company names - use only the provided client name '{client_name}'.",
            "Ensure the company name '{client_name}' is the most prominent text element."
        ],
        "billboard": "Requirements: High contrast, bold visuals, minimal text, maximum impact. Company name '{client_name}' must be the largest text element.",
        "social_media": "Requirements: Mobile-optimized, engaging visuals, clear focal point. Company name '{client_name}' must be clearly readable on mobile devices.",
        "default": "Requirements: Professional design with clear brand message. Company name '{client_name}' must be the primary brand identifier.",
        "output": "Output: Clean, flat advertisement design without frames, mockups, or 3D effects. Company name '{client_name}' prominently displayed."
    }
    
    # Nano Banana Pro Advanced Features Prompts
    NANO_BANANA_PRO_ENHANCEMENTS = {
        "search_grounding": "Use current real-world knowledge and verified information. Ensure factual accuracy for any maps, diagrams, or informational content.",
        "text_rendering": "Generate clear, professional text within the image. Use appropriate typography with proper font selection and natural text placement. Ensure text is readable and well-integrated into the design.",
        "quality_enhancement": [
            "Create enterprise-grade visual asset with 4K quality and sharp details.",
            "Maintain strong brand consistency and creative control.",
            "Use advanced composition with proper lighting and perspective.",
            "Professional design suitable for commercial use."
        ]
    }
    
    # Auto-detection keywords for advanced features
    DETECTION_KEYWORDS = {
        "search": ['infographic', 'facts', 'map', 'diagram', 'chart', 'data', 'real', 'accurate', 'current', 'geography', 'statistics'],
        "text": ['text', 'typography', 'sign', 'poster', 'banner', 'label', 'headline', 'slogan', 'tagline', 'words', 'font']
    }
    
    # Logo analysis prompts
    LOGO_ANALYSIS = {
        "basic": "Include company branding with {aspect_ratio} logo format. Templates will handle precise logo placement and sizing.",
        "fallback": "Include company branding with uploaded logo. Templates will handle logo placement."
    }
    
    # Theme extraction filters
    THEME_EXTRACTION = {
        "sale_terms": ['sale', 'off', '%', 'percent', 'discount', 'deal', 'special', 'limited', 'save'],
        "skip_words": ['the', 'and', 'for', 'with', 'get', 'now'],
        "fallback_themes": {
            "empty": "professional business theme",
            "no_words": "modern business theme"
        }
    }

class PromptBuilder:
    """Helper class to build prompts from templates"""
    
    @staticmethod
    def build_template_background_prompt(template, style, color_scheme, theme_keywords):
        """Build template background generation prompt"""
        return PromptTemplates.TEMPLATE_BACKGROUND_BASE.format(
            style=style,
            color_scheme=color_scheme,
            theme_keywords=theme_keywords,
            width=template['dimensions'][0],
            height=template['dimensions'][1],
            logo_width=template['logo_area']['width'],
            logo_height=template['logo_area']['height']
        ).strip()
    
    @staticmethod
    def build_enhanced_prompt(prompt, client_name, client_website, medium, style, 
                            color_scheme, include_text, include_cta, dimensions, 
                            logo_description="", client_tagline=""):
        """Build enhanced prompt for non-template generation with strong company name emphasis"""
        enhanced_parts = [PromptTemplates.ENHANCED_PROMPT_BASE.format(client_name=client_name)]
        
        # Add company name requirements FIRST
        for requirement in PromptTemplates.COMPANY_NAME_REQUIREMENTS:
            enhanced_parts.append(requirement.format(client_name=client_name))
        
        # Add tagline if provided
        if client_tagline and client_tagline.strip():
            enhanced_parts.append(f"Include the tagline: '{client_tagline}' beneath or near the company name '{client_name}'.")
        
        # Medium-specific enhancements
        medium_lower = medium.lower()
        if "billboard" in medium_lower or "outdoor" in medium_lower:
            enhanced_parts.append(PromptTemplates.MEDIUM_ENHANCEMENTS["billboard"])
        elif "social media" in medium_lower:
            enhanced_parts.append(PromptTemplates.MEDIUM_ENHANCEMENTS["social media"])
        elif "web" in medium_lower or "banner" in medium_lower:
            enhanced_parts.append(PromptTemplates.MEDIUM_ENHANCEMENTS["web"])
        else:
            enhanced_parts.append(PromptTemplates.MEDIUM_ENHANCEMENTS["default"].format(medium=medium_lower))
        
        # Style guidance
        enhanced_parts.append(PromptTemplates.STYLE_GUIDANCE.format(style=style))
        
        # Color scheme guidance
        if color_scheme.lower() == "brand colors":
            enhanced_parts.append(PromptTemplates.COLOR_SCHEME_GUIDANCE["brand colors"].format(client_name=client_name))
        else:
            enhanced_parts.append(PromptTemplates.COLOR_SCHEME_GUIDANCE["default"].format(color_scheme=color_scheme))
        
        # Format guidance
        width, height = dimensions
        if width == height:
            enhanced_parts.append(PromptTemplates.FORMAT_GUIDANCE["square"].format(width=width, height=height))
        elif width > height:
            enhanced_parts.append(PromptTemplates.FORMAT_GUIDANCE["landscape"].format(width=width, height=height))
        else:
            enhanced_parts.append(PromptTemplates.FORMAT_GUIDANCE["portrait"].format(width=width, height=height))
        
        # Logo integration
        if logo_description:
            enhanced_parts.append(logo_description)
        
        # Typography guidance with company name emphasis
        if include_text:
            if "billboard" in medium_lower:
                enhanced_parts.append(PromptTemplates.TYPOGRAPHY_GUIDANCE["billboard"])
                enhanced_parts.append(f"Make '{client_name}' the largest and most prominent text element.")
            else:
                enhanced_parts.append(PromptTemplates.TYPOGRAPHY_GUIDANCE["default"])
                enhanced_parts.append(f"Ensure '{client_name}' has the highest visual hierarchy.")
        
        # CTA guidance
        if include_cta:
            if client_website:
                if "billboard" in medium_lower:
                    enhanced_parts.append(PromptTemplates.CTA_GUIDANCE["with_website_billboard"].format(website=client_website))
                else:
                    enhanced_parts.append(PromptTemplates.CTA_GUIDANCE["with_website_default"].format(website=client_website))
            else:
                enhanced_parts.append(PromptTemplates.CTA_GUIDANCE["without_website"])
        
        # Main message (secondary to company name)
        enhanced_parts.append(f"Secondary message: {prompt} (this should complement, not overshadow the company name '{client_name}')")
        
        # Quality guidelines with company name emphasis
        for guideline in PromptTemplates.QUALITY_GUIDELINES["base"]:
            enhanced_parts.append(guideline.format(client_name=client_name))
        
        if "billboard" in medium_lower:
            enhanced_parts.append(PromptTemplates.QUALITY_GUIDELINES["billboard"].format(client_name=client_name))
        elif "social media" in medium_lower:
            enhanced_parts.append(PromptTemplates.QUALITY_GUIDELINES["social_media"].format(client_name=client_name))
        else:
            enhanced_parts.append(PromptTemplates.QUALITY_GUIDELINES["default"].format(client_name=client_name))
        
        enhanced_parts.append(PromptTemplates.QUALITY_GUIDELINES["output"].format(client_name=client_name))
        
        return " ".join(enhanced_parts)
    
    @staticmethod
    def build_nano_banana_pro_prompt(base_prompt, use_search_grounding=False, text_rendering_mode=False):
        """Build enhanced prompt with Nano Banana Pro capabilities"""
        prompt_parts = [base_prompt]
        
        if use_search_grounding:
            prompt_parts.append(PromptTemplates.NANO_BANANA_PRO_ENHANCEMENTS["search_grounding"])
        
        if text_rendering_mode:
            prompt_parts.append(PromptTemplates.NANO_BANANA_PRO_ENHANCEMENTS["text_rendering"])
        
        prompt_parts.extend(PromptTemplates.NANO_BANANA_PRO_ENHANCEMENTS["quality_enhancement"])
        
        return " ".join(prompt_parts)
    
    @staticmethod
    def detect_advanced_features(prompt):
        """Auto-detect if advanced features should be enabled"""
        prompt_lower = prompt.lower()
        
        use_search = any(keyword in prompt_lower for keyword in PromptTemplates.DETECTION_KEYWORDS["search"])
        use_text = any(keyword in prompt_lower for keyword in PromptTemplates.DETECTION_KEYWORDS["text"])
        
        return use_search, use_text
    
    @staticmethod
    def extract_theme_keywords(content_prompt):
        """Extract theme keywords from content prompt, removing specific text to prevent duplication"""
        if not content_prompt.strip():
            return PromptTemplates.THEME_EXTRACTION["fallback_themes"]["empty"]
        
        filtered_prompt = content_prompt.lower()
        sale_terms = PromptTemplates.THEME_EXTRACTION["sale_terms"]
        skip_words = PromptTemplates.THEME_EXTRACTION["skip_words"]
        
        theme_words = []
        words = filtered_prompt.split()
        
        for word in words:
            if not any(term in word for term in sale_terms) and not word.isdigit():
                if len(word) > 2 and word not in skip_words:
                    theme_words.append(word)
        
        if not theme_words:
            return PromptTemplates.THEME_EXTRACTION["fallback_themes"]["no_words"]
        
        clean_theme = " ".join(theme_words[:5])
        return f"{clean_theme} theme with professional aesthetic"
    
    @staticmethod
    def analyze_logo_details(logo_file):
        """Generate logo analysis for AI prompt"""
        try:
            if hasattr(logo_file, 'seek') and hasattr(logo_file, 'read'):
                logo_file.seek(0)
                from PIL import Image
                logo_image = Image.open(logo_file)
                
                width, height = logo_image.size
                aspect_ratio = "square" if abs(width - height) < 50 else ("horizontal" if width > height else "vertical")
                
                return PromptTemplates.LOGO_ANALYSIS["basic"].format(aspect_ratio=aspect_ratio)
                
        except Exception:
            return PromptTemplates.LOGO_ANALYSIS["fallback"]