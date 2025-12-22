"""
Template-based advertisement generation system
Creates templates with designated spots for logos, taglines, and other brand elements
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
from .prompts import PromptBuilder
from .template_prompts import get_ai_native_prompt, get_overlay_mode_prompt

class TemplateManager:
    """Manages advertisement templates with placeholder areas for brand elements"""
    
    # Zone-to-position mapping for flexible template layouts
    ZONE_POSITIONS = {
        'top-left': (0.05, 0.05),
        'top-center': (0.4, 0.05),
        'top-right': (0.75, 0.05),
        'center-left': (0.05, 0.4),
        'center': (0.35, 0.4),
        'center-right': (0.75, 0.4),
        'bottom-left': (0.05, 0.75),
        'bottom-center': (0.35, 0.75),
        'bottom-right': (0.7, 0.8),
    }
    
    def __init__(self):
        self.templates_dir = "templates"
        self.custom_templates_dir = "templates/custom"
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.custom_templates_dir, exist_ok=True)
        # Removed load_default_templates() - only using custom templates now
    
    def _resolve_position(self, position: Dict, dimensions: List[int]) -> Dict:
        """Convert zone-based or relative position to absolute pixels
        
        Supports:
        - Absolute: {"x": 100, "y": 200}
        - Zone-based: {"zone": "top-left", "style": "...", "integration": "..."}
        """
        width, height = dimensions if isinstance(dimensions, list) else [dimensions.get('width', 1920), dimensions.get('height', 1080)]
        
        # If already absolute position, return as-is
        if 'x' in position and 'y' in position:
            return position
        
        # If zone-based, convert to pixels
        if 'zone' in position:
            zone = position.get('zone', 'center')
            if zone in self.ZONE_POSITIONS:
                x_ratio, y_ratio = self.ZONE_POSITIONS[zone]
                return {
                    'x': int(width * x_ratio),
                    'y': int(height * y_ratio),
                    'zone': zone,  # Keep zone info for AI
                    'style': position.get('style', ''),
                    'integration': position.get('integration', '')
                }
        
        # Fallback to center
        return {'x': int(width * 0.35), 'y': int(height * 0.4)}
    
    def get_available_templates(self) -> Dict:
        """Return list of available custom templates"""
        templates = {}
        
        # Only add custom templates (removed built-in templates)
        custom_templates = self.get_custom_templates()
        for template_name in custom_templates:
            template_id = f"custom_{template_name.lower().replace(' ', '_')}"
            templates[template_id] = f"📝 {template_name}"
        
        return templates
    
    def get_custom_templates(self) -> List[str]:
        """Get list of custom template names"""
        if not os.path.exists(self.custom_templates_dir):
            return []
        
        templates = []
        for filename in os.listdir(self.custom_templates_dir):
            if filename.endswith('.json'):
                template_name = filename[:-5].replace('_', ' ').title()
                templates.append(template_name)
        return templates
    
    def load_custom_template(self, template_name: str) -> Optional[Dict]:
        """Load custom template from file"""
        try:
            filename = f"{template_name.replace(' ', '_').lower()}.json"
            filepath = os.path.join(self.custom_templates_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get specific template configuration - only custom templates supported"""
        # All templates are custom templates now
        if template_id.startswith("custom_"):
            template_name = template_id[7:].replace('_', ' ').title()
            custom_template = self.load_custom_template(template_name)
            if custom_template:
                # Convert custom template format to standard format
                return self._convert_custom_template(custom_template)
        
        # No built-in templates anymore
        return None
    
    def get_template_variables(self, template_id: str) -> List[Dict[str, str]]:
        """Extract all variables from a template and return metadata for form generation
        
        Returns:
            List of dicts with keys: 'variable', 'label', 'type', 'placeholder'
        """
        # Standard variables that are always included
        standard_vars = {
            '{{logo}}': {
                'variable': 'logo',
                'label': 'Company Logo',
                'type': 'file',
                'placeholder': 'Upload logo image'
            },
            '{{client_name}}': {
                'variable': 'client_name',
                'label': 'Company Name',
                'type': 'text',
                'placeholder': 'Enter company name...'
            },
            '{{client_tagline}}': {
                'variable': 'client_tagline',
                'label': 'Tagline',
                'type': 'text',
                'placeholder': 'Your company slogan...'
            },
            '{{main_message}}': {
                'variable': 'main_message',
                'label': 'Main Message',
                'type': 'textarea',
                'placeholder': 'Enter the main advertisement message...'
            },
            '{{prompt}}': {  # Legacy support
                'variable': 'main_message',
                'label': 'Main Message',
                'type': 'textarea',
                'placeholder': 'Enter the main advertisement message...'
            },
            '{{cta_text}}': {
                'variable': 'cta_text',
                'label': 'Call-to-Action Text',
                'type': 'text',
                'placeholder': 'e.g., SHOP NOW, LEARN MORE...'
            },
            '{{client_website}}': {
                'variable': 'client_website',
                'label': 'Website',
                'type': 'text',
                'placeholder': 'https://example.com'
            }
        }
        
        # Get template elements - only custom templates now
        template = None
        if template_id.startswith("custom_"):
            template_name = template_id[7:].replace('_', ' ').title()
            template = self.load_custom_template(template_name)
        
        if not template:
            return []
        
        # Extract variables from template elements
        found_variables = {}
        
        # Check custom template elements
        if "elements" in template:
            for element in template["elements"]:
                content = element.get("content", "")
                # Find all {{variable}} patterns
                import re
                matches = re.findall(r'\{\{([^}]+)\}\}', content)
                for var_name in matches:
                    var_key = f"{{{{{var_name}}}}}"
                    if var_key in standard_vars:
                        found_variables[var_name] = standard_vars[var_key]
                    else:
                        # Custom variable not in standard list
                        found_variables[var_name] = {
                            'variable': var_name,
                            'label': var_name.replace('_', ' ').title(),
                            'type': 'text',
                            'placeholder': f'Enter {var_name.replace("_", " ")}...'
                        }
        
        # Return list of unique variables
        return list(found_variables.values())
    
    def _convert_custom_template(self, custom_template: Dict) -> Dict:
        """Convert custom template format to standard template format"""
        # Extract element positions for compatibility
        elements = custom_template.get("elements", [])
        dimensions = custom_template.get("dimensions", [1080, 1080])
        
        # Find key areas from elements
        logo_area = None
        title_area = None
        tagline_area = None
        content_area = None
        cta_area = None
        
        for element in elements:
            # NEW STRUCTURE: placement_hint at element level (no position dict)
            if "placement_hint" in element:
                # For AI-native templates with semantic positioning, skip area extraction
                # These templates don't need pixel-based areas
                continue
            
            # OLD STRUCTURE: position dict exists
            if "position" not in element:
                continue
                
            # Resolve position (zone or pixel)
            position = self._resolve_position(element["position"], dimensions)
            
            # Get size with fallback defaults
            size = element.get("size", {})
            elem_width = size.get("width", 300)
            elem_height = size.get("height", 100)
            
            if element["type"] == "logo":
                logo_area = {
                    "x": position["x"],
                    "y": position["y"], 
                    "width": elem_width,
                    "height": elem_height
                }
            elif element["type"] == "text" and "client_name" in element.get("content", ""):
                title_area = {
                    "x": position["x"],
                    "y": position["y"],
                    "width": elem_width, 
                    "height": elem_height
                }
            elif element["type"] == "text" and "tagline" in element.get("content", ""):
                tagline_area = {
                    "x": position["x"],
                    "y": position["y"],
                    "width": elem_width,
                    "height": elem_height
                }
            elif element["type"] == "text" and ("main_message" in element.get("content", "") or "prompt" in element.get("content", "")):
                content_area = {
                    "x": position["x"],
                    "y": position["y"],
                    "width": elem_width,
                    "height": elem_height
                }
            elif element["type"] in ["button", "cta"]:
                cta_area = {
                    "x": position["x"],
                    "y": position["y"],
                    "width": elem_width,
                    "height": elem_height
                }
        
        # Provide defaults if areas not found
        width, height = dimensions
        
        return {
            "name": custom_template.get("name", "Custom Template"),
            "dimensions": dimensions,
            "logo_area": logo_area or {"x": 50, "y": 50, "width": 200, "height": 100},
            "title_area": title_area or {"x": width//4, "y": 50, "width": width//2, "height": height//8},
            "tagline_area": tagline_area or {"x": width//4, "y": height//5, "width": width//2, "height": height//15},
            "content_area": content_area or {"x": 50, "y": height//2, "width": int(width*0.8), "height": height//4},
            "cta_area": cta_area or {"x": width-350, "y": height-150, "width": 300, "height": 100},
            "background_prompt": f"Create {custom_template.get('background_style', {}).get('style', 'modern')} background design with {custom_template.get('background_style', {}).get('color_scheme', 'brand')} colors",
            "custom_elements": elements  # Store full custom elements for advanced rendering
        }
    
    
    def create_template_background(self, template_id: str, style: str, color_scheme: str, 
                                 content_prompt: str, template_data: Dict = None, data: Dict = None) -> str:
        """Generate AI prompt for template background creation
        
        Supports two modes:
        1. OVERLAY MODE (default): AI generates background, text added as overlays
        2. AI-NATIVE MODE: AI generates everything including text as part of scene (for cinematic templates)
        
        AI-native mode activated when template has 'design_rules' field.
        
        Args:
            data: Dict with actual values (client_name, main_message, etc.) for AI-native mode
        """
        template = template_data if template_data else self.get_template(template_id)
        if not template:
            return ""
        
        # Check if this is an AI-native cinematic template
        design_rules = template.get("design_rules", [])
        is_ai_native = bool(design_rules)
        data = data or {}
        
        # Get dimensions
        dimensions = template.get("dimensions", [1920, 1080])
        width = dimensions[0] if isinstance(dimensions, list) and len(dimensions) >= 2 else 1920
        height = dimensions[1] if isinstance(dimensions, list) and len(dimensions) >= 2 else 1080
        
        # Analyze element positions to guide AI composition
        elements = template.get("custom_elements", []) or template.get("elements", [])
        spatial_guidance = []
        zone_styles = []  # Collect zone-specific styling hints
        text_elements_for_ai = []  # For AI-native mode: collect actual text content
        
        if elements:
            # Identify key zones where elements will be placed
            for element in elements:
                elem_type = element.get("type")
                content = element.get("content", "")
                
                # NEW STRUCTURE: placement_hint, priority, integration at element level
                if "placement_hint" in element:
                    placement_hint = element.get("placement_hint", "")
                    priority = element.get("priority", "medium")
                    integration = element.get("integration", "")
                    
                    if elem_type in ["text", "button", "cta", "logo"]:
                        # For AI-native mode: collect text content and replace variables
                        if is_ai_native and content:
                            # Replace template variables with actual values
                            actual_content = content
                            for var_name, var_value in data.items():
                                placeholder = f"{{{{{var_name}}}}}"
                                if placeholder in actual_content and var_value:
                                    actual_content = actual_content.replace(placeholder, var_value)
                            
                            # Only include if not still a template variable
                            if not actual_content.startswith("{{") and actual_content.strip():
                                # Get style_hint from element style dict
                                element_style = element.get("style", {})
                                visual_hint = element_style.get("style_hint", "")
                                
                                text_elem = {
                                    "type": elem_type,
                                    "content": actual_content,
                                    "placement_hint": placement_hint,
                                    "priority": priority,
                                    "integration": integration,
                                    "style_hint": visual_hint
                                }
                                text_elements_for_ai.append(text_elem)
                
                # OLD STRUCTURE: position dict with zone/priority (backward compatibility)
                elif "position" in element:
                    position_config = element.get("position", {})
                    style_hint = element.get("style_hint", "")
                    
                    # Check if zone-based positioning BEFORE resolving
                    if 'zone' in position_config:
                        zone = position_config.get('zone', '')
                        elem_style = position_config.get('style', '') or style_hint
                        integration = position_config.get('integration', '')
                        priority = position_config.get('priority', 'medium')
                        
                        if elem_type in ["text", "button", "cta", "logo"]:
                            zone_desc = f"{elem_type} in {zone}"
                            if elem_style:
                                zone_desc += f" (style: {elem_style})"
                            if integration:
                                zone_desc += f" ({integration})"
                            zone_styles.append(zone_desc)
                            spatial_guidance.append(zone)
                            
                            # For AI-native mode: collect text content and replace variables
                            if is_ai_native and content:
                                # Replace template variables with actual values
                                actual_content = content
                                for var_name, var_value in data.items():
                                    placeholder = f"{{{{{var_name}}}}}"
                                    if placeholder in actual_content and var_value:
                                        actual_content = actual_content.replace(placeholder, var_value)
                                
                                # Only include if not still a template variable
                                if not actual_content.startswith("{{") and actual_content.strip():
                                    # Get style_hint from element style dict, ignore font specs
                                    element_style = element.get("style", {})
                                    visual_hint = element_style.get("style_hint", "") or elem_style
                                    
                                    text_elem = {
                                        "zone": zone,
                                        "type": elem_type,
                                        "content": actual_content,
                                        "style_hint": visual_hint,
                                        "integration": integration,
                                        "priority": priority
                                    }
                                    text_elements_for_ai.append(text_elem)
                    else:
                        # Pixel-based - resolve and calculate relative position
                        position = self._resolve_position(position_config, [width, height])
                        x = position.get('x', 0)
                        y = position.get('y', 0)
                        
                        # Fallback to relative position calculation
                        if y < height * 0.3:
                            vertical = "top"
                        elif y < height * 0.7:
                            vertical = "center"
                        else:
                            vertical = "bottom"
                        
                        if x < width * 0.3:
                            horizontal = "left"
                        elif x < width * 0.7:
                            horizontal = "center-horizontal"
                        else:
                            horizontal = "right"
                        
                        if elem_type in ["text", "button"]:
                            spatial_guidance.append(f"{vertical} {horizontal}")
        
        # MODE 1: AI-NATIVE CINEMATIC MODE - AI generates EVERYTHING including text
        if is_ai_native and text_elements_for_ai:
            has_logo = data.get('logo') or any(elem.get('type') == 'logo' for elem in elements)
            template_style = template.get('background_style', {})
            
            base_prompt = get_ai_native_prompt(
                content_prompt=content_prompt,
                width=width,
                height=height,
                template_style=template_style,
                design_rules=design_rules,
                text_elements=text_elements_for_ai,
                has_logo=has_logo
            )
            
            if style and style != "Professional":
                base_prompt += f"\nOverall style: {style}"
            if color_scheme and color_scheme != "Brand Colors":
                base_prompt += f"\nColor scheme: {color_scheme}"
                
            return base_prompt
        
        # MODE 2: OVERLAY MODE - AI generates background only, text added separately  
        if content_prompt and content_prompt.strip():
            template_style = template.get('background_style', {})
            
            base_prompt = get_overlay_mode_prompt(
                content_prompt=content_prompt.strip(),
                width=width,
                height=height,
                template_style=template_style,
                spatial_guidance=spatial_guidance,
                zone_styles=zone_styles
            )
            
            # Add style and color scheme guidance if specified
            if style and style != "Professional":
                base_prompt += f"\n\nStyle: {style}."
            if color_scheme and color_scheme != "Brand Colors":
                base_prompt += f" Color scheme: {color_scheme}."
            
            return base_prompt
        
        # Fallback: If no custom prompt, use template-based generation
        theme_keywords = PromptBuilder.extract_theme_keywords(content_prompt)
        base_prompt = PromptBuilder.build_template_background_prompt(
            template, style, color_scheme, theme_keywords
        )
        
        return base_prompt
    
    def apply_brand_elements(self, background_image: Image.Image, template_id: str,
                           logo: Optional[Image.Image] = None, 
                           client_name: str = "", 
                           tagline: str = "",
                           main_message: str = "",
                           cta_text: str = "",
                           website: str = "",
                           color_scheme: str = "Brand Colors") -> Image.Image:
        """Apply brand elements to template background - all fields except client_name are optional"""
        template = self.get_template(template_id)
        if not template or not background_image:
            return background_image
        
        # Check if this is a custom template with advanced elements
        if template.get("custom_elements"):
            return self._apply_custom_elements(background_image, template, {
                "logo": logo,
                "client_name": client_name,
                "client_tagline": tagline,
                "main_message": main_message,  # This maps to {{main_message}} in template
                "cta_text": cta_text,
                "client_website": website
            })
        
        # Use standard template application for built-in templates
        return self._apply_standard_elements(background_image, template, logo, client_name, tagline, main_message, cta_text, website, color_scheme)
    
    def _apply_custom_elements(self, background_image: Image.Image, template: Dict, data: Dict) -> Image.Image:
        """Apply custom template elements with advanced positioning
        
        Supports two modes:
        1. OVERLAY MODE: Elements rendered as PIL overlays (default)
        2. AI-NATIVE MODE: Skip text overlays - only add logo (text already generated by AI when design_rules present)
        """
        # Check if AI-native template (text already in image)
        design_rules = template.get("design_rules", [])
        is_ai_native = bool(design_rules)
        
        if is_ai_native:
            # AI-native mode: Only apply logo, skip all text elements
            result_image = background_image.copy()
            elements = template.get("elements", [])
            dimensions = template.get("dimensions", [1920, 1080])
            
            for element in elements:
                if element.get("type") == "logo" and data.get("logo"):
                    # Apply just the logo
                    position_config = element.get("position", {})
                    position = self._resolve_position(position_config, dimensions)
                    size = element.get("size", {})
                    
                    logo = data.get("logo")
                    if logo:
                        # Resize and place logo
                        resized_logo = self._resize_logo_to_area(logo, size)
                        if resized_logo:
                            x, y = position.get('x', 0), position.get('y', 0)
                            result_image.paste(resized_logo, (x, y), resized_logo if resized_logo.mode == 'RGBA' else None)
            
            return result_image
        
        # OVERLAY MODE: Continue with normal PIL overlay rendering
        result_image = background_image.copy()
        draw = ImageDraw.Draw(result_image)
        
        # Get dimensions for position resolution
        dimensions = template.get("dimensions", [1920, 1080])
        
        try:
            # Load fonts
            fonts = {
                'small': self._get_font(20),
                'medium': self._get_font(30),
                'large': self._get_font(60),
                'xlarge': self._get_font(80)
            }
        except:
            fonts = {size: ImageDraw.getfont() for size in ['small', 'medium', 'large', 'xlarge']}
        
        # Process each custom element
        for element in template.get("custom_elements", []):
            try:
                element_type = element.get("type")
                position_config = element.get("position", {})
                size = element.get("size", {})
                content = element.get("content", "")
                style = element.get("style", {})
                
                # Resolve position (supports both pixel and zone-based)
                position = self._resolve_position(position_config, dimensions)
                
                # Replace template variables in content
                for var, value in data.items():
                    # Only replace if value exists and is not empty after stripping
                    if value and str(value).strip() and f"{{{{{var}}}}}" in content:
                        content = content.replace(f"{{{{{var}}}}}", str(value))
                
                # Apply element based on type - skip if empty or still has unreplaced variables
                if element_type == "text" and content and content.strip() and not content.startswith("{{"):
                    self._draw_custom_text(draw, content, position, size, style, fonts)
                
                elif element_type == "logo" and data.get("logo"):
                    self._draw_custom_logo(result_image, data["logo"], position, size, style)
                
                elif element_type == "button" and content and content.strip() and not content.startswith("{{"):
                    self._draw_custom_button(draw, content, position, size, style, fonts, data.get("client_website"))
                
                elif element_type == "shape":
                    self._draw_custom_shape(draw, position, size, style)
                    
            except Exception as e:
                # Continue with other elements if one fails
                continue
        
        return result_image
    
    def _draw_custom_text(self, draw, text: str, position: Dict, size: Dict, style: Dict, fonts: Dict):
        """Draw custom text element with seamless blending"""
        from PIL import Image as PILImage, ImageFilter
        
        font_size = style.get('font_size', 30)
        color = style.get('color', '#FFFFFF')
        
        # Select appropriate font
        if font_size <= 25:
            font = fonts['small']
        elif font_size <= 40:
            font = fonts['medium']
        elif font_size <= 70:
            font = fonts['large']
        else:
            font = fonts['xlarge']
        
        x, y = position.get('x', 0), position.get('y', 0)
        width = size.get('width', 500)
        height = size.get('height', 100)
        
        # Get the actual text bounding box for precise backdrop sizing
        bbox = draw.textbbox((x, y), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create a semi-transparent backdrop with rounded corners
        padding_h = 20
        padding_v = 15
        backdrop_x = max(0, x - padding_h)
        backdrop_y = max(0, y - padding_v)
        backdrop_width = text_width + (padding_h * 2)
        backdrop_height = text_height + (padding_v * 2)
        
        # Draw soft shadow for the backdrop (multiple layers for blur effect)
        shadow_layers = 4
        for i in range(shadow_layers, 0, -1):
            shadow_alpha = 40 - (i * 8)  # Decreasing opacity for softer shadow
            shadow_offset = i * 3
            draw.rounded_rectangle(
                [backdrop_x + shadow_offset, backdrop_y + shadow_offset, 
                 backdrop_x + backdrop_width + shadow_offset, backdrop_y + backdrop_height + shadow_offset],
                radius=12,
                fill=(0, 0, 0, shadow_alpha)
            )
        
        # Draw MORE transparent backdrop for better scene integration
        backdrop_alpha = 75  # More transparent for better blending with scene
        draw.rounded_rectangle(
            [backdrop_x, backdrop_y, backdrop_x + backdrop_width, backdrop_y + backdrop_height],
            radius=12,
            fill=(10, 10, 15, backdrop_alpha)  # Slightly blue-tinted for depth
        )
        
        # Add subtle inner glow/highlight for atmospheric effect
        inner_glow_alpha = 20
        draw.rounded_rectangle(
            [backdrop_x + 2, backdrop_y + 2, backdrop_x + backdrop_width - 2, backdrop_y + backdrop_height - 2],
            radius=10,
            outline=(255, 255, 255, inner_glow_alpha),
            width=2
        )
        
        # Draw text with soft shadow for depth
        shadow_offset = 3
        shadow_blur = 2
        for offset in range(shadow_blur, 0, -1):
            shadow_alpha = 100 - (offset * 20)
            draw.text((x + shadow_offset + offset, y + shadow_offset + offset), 
                     text, font=font, fill=(0, 0, 0, shadow_alpha))
        
        # Draw main text with subtle stroke for definition
        stroke_width = 2 if font_size > 40 else 1
        draw.text((x, y), text, font=font, fill=color, stroke_width=stroke_width, stroke_fill=(0, 0, 0, 150))
    
    def _draw_custom_logo(self, image: Image.Image, logo: Image.Image, position: Dict, size: Dict, style: Dict):
        """Draw custom logo element"""
        x, y = position.get('x', 0), position.get('y', 0)
        width, height = size.get('width', 200), size.get('height', 100)
        
        # Resize logo to fit
        resized_logo = self._resize_logo_to_area(logo, {'width': width, 'height': height})
        if resized_logo:
            image.paste(resized_logo, (x, y), resized_logo if resized_logo.mode == 'RGBA' else None)
    
    def _draw_custom_button(self, draw, text: str, position: Dict, size: Dict, style: Dict, fonts: Dict, website: str = ""):
        """Draw custom button element with professional blending and scene integration"""
        from PIL import Image as PILImage
        
        x, y = position.get('x', 0), position.get('y', 0)
        width, height = size.get('width', 200), size.get('height', 60)
        bg_color = style.get('bg_color', '#FF6600')
        text_color = style.get('text_color', '#FFFFFF')
        border_radius = style.get('border_radius', 10)
        
        # Draw multi-layer soft shadow for natural depth and atmospheric integration
        shadow_layers = 5
        for i in range(shadow_layers, 0, -1):
            shadow_alpha = 50 - (i * 8)  # Gradually decreasing opacity
            shadow_offset = i * 3
            draw.rounded_rectangle(
                [x + shadow_offset, y + shadow_offset, x + width + shadow_offset, y + height + shadow_offset],
                radius=border_radius + 2,
                fill=(0, 0, 0, shadow_alpha)
            )
        
        # Parse bg_color if it's hex
        if isinstance(bg_color, str) and bg_color.startswith('#'):
            bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
        else:
            bg_rgb = (255, 102, 0)  # Default orange
        
        # Add atmospheric glow around button for integration
        glow_padding = 8
        for glow_layer in range(3, 0, -1):
            glow_alpha = 15 + (glow_layer * 5)
            glow_offset = glow_layer * 3
            draw.rounded_rectangle(
                [x - glow_offset, y - glow_offset, 
                 x + width + glow_offset, y + height + glow_offset],
                radius=border_radius + glow_offset,
                fill=bg_rgb + (glow_alpha,)
            )
        
        # Draw button background with gradient effect (lighter at top)
        draw.rounded_rectangle([x, y, x + width, y + height], radius=border_radius, fill=bg_rgb + (245,))
        
        # Add subtle highlight at top for 3D depth
        highlight_height = height // 3
        draw.rounded_rectangle(
            [x, y, x + width, y + highlight_height],
            radius=border_radius,
            fill=(255, 255, 255, 40)
        )
        
        # Add subtle inner border for definition
        draw.rounded_rectangle(
            [x + 2, y + 2, x + width - 2, y + height - 2],
            radius=border_radius - 2,
            outline=(255, 255, 255, 60),
            width=2
        )
        border_color = tuple(max(0, c - 30) for c in bg_rgb)  # Slightly darker
        draw.rounded_rectangle(
            [x, y, x + width, y + height],
            radius=border_radius,
            outline=border_color + (200,),
            width=2
        )
        
        # Draw button text with shadow
        font = fonts['medium']
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x + (width - text_width) // 2
        text_y = y + (height - text_height) // 2
        
        # Text shadow
        draw.text((text_x + 2, text_y + 2), text, font=font, fill=(0, 0, 0, 120))
        
        # Main text
        draw.text((text_x, text_y), text, font=font, fill=text_color)
        
        # Draw website below button if provided - with backdrop for visibility
        if website and website.strip():
            website_font = fonts['small']
            website_y = y + height + 15
            
            # Get website text dimensions
            website_bbox = draw.textbbox((0, 0), website, font=website_font)
            website_width = website_bbox[2] - website_bbox[0]
            website_height = website_bbox[3] - website_bbox[1]
            
            # Center website below button
            website_x = x + (width - website_width) // 2
            
            # Draw semi-transparent backdrop behind website
            padding = 8
            draw.rounded_rectangle(
                [website_x - padding, website_y - padding, 
                 website_x + website_width + padding, website_y + website_height + padding],
                radius=4,
                fill=(0, 0, 0, 80)
            )
            
            # Draw website text with shadow
            draw.text((website_x + 1, website_y + 1), website, font=website_font, fill=(0, 0, 0, 100))
            draw.text((website_x, website_y), website, font=website_font, fill="#FFFFFF")
    
    def _draw_custom_shape(self, draw, position: Dict, size: Dict, style: Dict):
        """Draw custom shape element"""
        x, y = position.get('x', 0), position.get('y', 0)
        width, height = size.get('width', 100), size.get('height', 100)
        fill_color = style.get('fill_color', '#333333')
        border_color = style.get('border_color', '#666666')
        
        # For now, just draw rectangles (can be extended for other shapes)
        draw.rectangle([x, y, x + width, y + height], fill=fill_color, outline=border_color)
    
    def _get_text_colors(self, color_scheme: str):
        """Get appropriate text colors based on color scheme"""
        color_schemes = {
            "Brand Colors": {"primary": "#FFFFFF", "secondary": "#E0E0E0", "accent": "#FFD700", "cta_bg": "#FF6600"},
            "Warm Tones": {"primary": "#FFFFFF", "secondary": "#FFF8DC", "accent": "#FFD700", "cta_bg": "#FF4500"},
            "Cool Tones": {"primary": "#FFFFFF", "secondary": "#E6F3FF", "accent": "#00BFFF", "cta_bg": "#1E90FF"},
            "Monochrome": {"primary": "#FFFFFF", "secondary": "#CCCCCC", "accent": "#888888", "cta_bg": "#333333"},
            "High Contrast": {"primary": "#FFFFFF", "secondary": "#FFFF00", "accent": "#00FF00", "cta_bg": "#FF0000"},
            "Pastel": {"primary": "#FFFFFF", "secondary": "#F0F8FF", "accent": "#DDA0DD", "cta_bg": "#98FB98"}
        }
        return color_schemes.get(color_scheme, color_schemes["Brand Colors"])
    
    def _apply_standard_elements(self, background_image: Image.Image, template: Dict, 
                                logo: Optional[Image.Image], client_name: str, tagline: str, 
                                main_message: str, cta_text: str, website: str, color_scheme: str = "Brand Colors") -> Image.Image:
        """Apply brand elements to template background - all fields except client_name are optional"""
        if not template or not background_image:
            return background_image
        
        # Get dynamic colors based on color scheme
        colors = self._get_text_colors(color_scheme)
        
        # Create a copy to work with
        result_image = background_image.copy()
        draw = ImageDraw.Draw(result_image)
        
        try:
            # Load fonts (fallback to default if custom fonts not available)
            title_font = self._get_font(60)
            tagline_font = self._get_font(30)
            content_font = self._get_font(40)
            cta_font = self._get_font(35)
        except:
            # Fallback to default fonts
            title_font = tagline_font = content_font = cta_font = ImageDraw.getfont()
        
        # Apply logo if provided
        if logo:
            try:
                logo_area = template["logo_area"]
                resized_logo = self._resize_logo_to_area(logo, logo_area)
                if resized_logo:
                    result_image.paste(resized_logo, (logo_area["x"], logo_area["y"]), resized_logo if resized_logo.mode == 'RGBA' else None)
            except Exception as e:
                pass  # Continue without logo if there's an error
        
        # Apply main message FIRST (so it can be overlaid by company name if needed)
        if main_message.strip():
            try:
                content_area = template["content_area"]
                # Make promotional messages more prominent
                is_promotional = any(keyword in main_message.lower() for keyword in ['sale', 'off', '%', 'discount', 'deal', 'special', 'limited'])
                display_message = main_message.upper() if is_promotional else main_message
                text_color = colors["accent"] if is_promotional else colors["secondary"]  # Use secondary color to not compete with company name
                self._draw_text_in_area(draw, display_message, content_area, content_font, fill=text_color, stroke_width=1, stroke_fill="#000000")
            except Exception as e:
                try:
                    # Fallback with prominent positioning
                    display_message = main_message.upper() if any(keyword in main_message.lower() for keyword in ['sale', 'off', '%']) else main_message
                    draw.text((template["content_area"]["x"] + 20, template["content_area"]["y"] + 20), display_message, fill=colors["secondary"])
                except:
                    pass
        
        # Apply tagline - only if provided
        if tagline.strip():
            try:
                tagline_area = template["tagline_area"]
                self._draw_text_in_area(draw, tagline, tagline_area, tagline_font, fill=colors["secondary"], stroke_width=1, stroke_fill="#000000")
            except Exception as e:
                try:
                    draw.text((template["tagline_area"]["x"] + 20, template["tagline_area"]["y"] + 20), tagline, fill=colors["secondary"])
                except:
                    pass
        
        # Apply title (client name) - RENDER LAST for maximum visibility and priority
        if client_name and client_name.strip():
            try:
                title_area = template["title_area"]
                display_name = client_name.upper()
                # Use the strongest color and maximum stroke for company name visibility
                self._draw_text_in_area(draw, display_name, title_area, title_font, fill="#FFFFFF", stroke_width=4, stroke_fill="#000000")
                # Debug: Confirm client name was applied
                print(f"DEBUG: Client name '{display_name}' applied to title area at {title_area}")
            except Exception as e:
                # CRITICAL fallback to ensure client name is ALWAYS visible
                print(f"DEBUG: Title area rendering failed: {e}")
                try:
                    # Use a prominent position if template fails
                    fallback_x = template["title_area"]["x"] + 20 if "title_area" in template else 50
                    fallback_y = template["title_area"]["y"] + 20 if "title_area" in template else 50
                    display_name = client_name.upper()
                    # Draw with maximum visibility
                    draw.text((fallback_x, fallback_y), display_name, fill="#FFFFFF", font=title_font)
                    # Add a background rectangle to ensure visibility
                    bbox = draw.textbbox((fallback_x, fallback_y), display_name, font=title_font)
                    draw.rectangle([bbox[0]-10, bbox[1]-5, bbox[2]+10, bbox[3]+5], fill="#000000", outline="#FFFFFF", width=2)
                    draw.text((fallback_x, fallback_y), display_name, fill="#FFFFFF", font=title_font)
                    print(f"DEBUG: Client name '{display_name}' applied via fallback with background at ({fallback_x}, {fallback_y})")
                except Exception as fallback_error:
                    print(f"DEBUG: Even fallback failed: {fallback_error}")
        else:
            # This should NEVER happen - client name is required
            print(f"DEBUG: WARNING - No client name provided! client_name='{client_name}'")
            # Force a placeholder so user knows something is wrong
            try:
                title_area = template["title_area"]
                warning_text = "[COMPANY NAME MISSING]"
                draw.rectangle([title_area["x"], title_area["y"], title_area["x"] + 400, title_area["y"] + 60], fill="#FF0000", outline="#FFFFFF", width=3)
                draw.text((title_area["x"] + 10, title_area["y"] + 10), warning_text, fill="#FFFFFF", font=title_font)
                print("DEBUG: Added missing client name warning in red background")
            except:
                pass
        
        # Apply CTA - only if provided
        if cta_text.strip():
            try:
                cta_area = template["cta_area"]
                # Use dynamic button color based on color scheme
                button_color = colors["cta_bg"]
                draw.rounded_rectangle([cta_area["x"], cta_area["y"], 
                                      cta_area["x"] + cta_area["width"], 
                                      cta_area["y"] + cta_area["height"]], 
                                     radius=15, fill=button_color, outline="#000000", width=2)
                self._draw_text_in_area(draw, cta_text.upper(), cta_area, cta_font, fill="#FFFFFF", stroke_width=1, stroke_fill="#000000")
                
                # Add website if provided and CTA exists
                if website.strip():
                    website_y = cta_area["y"] + cta_area["height"] + 15
                    try:
                        draw.text((cta_area["x"], website_y), website, fill=colors["secondary"], font=self._get_font(20))
                    except:
                        draw.text((cta_area["x"], website_y), website, fill=colors["secondary"])
            except Exception as e:
                try:
                    # Fallback CTA
                    draw.text((template["cta_area"]["x"] + 20, template["cta_area"]["y"] + 20), cta_text.upper(), fill=colors["cta_bg"])
                except:
                    pass
        
        return result_image
    
    def _get_font(self, size: int):
        """Get font with fallback"""
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.load_default()
            except:
                return ImageDraw.getfont()
    
    def _resize_logo_to_area(self, logo: Image.Image, area: Dict) -> Image.Image:
        """Resize logo to fit in designated area"""
        max_width = area["width"]
        max_height = area["height"]
        
        # Calculate scaling factor
        width_ratio = max_width / logo.width
        height_ratio = max_height / logo.height
        scale_ratio = min(width_ratio, height_ratio)
        
        new_width = int(logo.width * scale_ratio)
        new_height = int(logo.height * scale_ratio)
        
        return logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _draw_text_in_area(self, draw, text: str, area: Dict, font, fill="white", stroke_width=0, stroke_fill="black"):
        """Draw text centered in specified area with better error handling"""
        try:
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate centered position
            x = area["x"] + (area["width"] - text_width) // 2
            y = area["y"] + (area["height"] - text_height) // 2
            
            # Ensure text fits in area
            if text_width > area["width"] or text_height > area["height"]:
                # Try smaller font if text doesn't fit
                try:
                    smaller_font = self._get_font(max(12, int(font.size * 0.8)))
                    bbox = draw.textbbox((0, 0), text, font=smaller_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = area["x"] + (area["width"] - text_width) // 2
                    y = area["y"] + (area["height"] - text_height) // 2
                    font = smaller_font
                except:
                    # Use default positioning if font scaling fails
                    x = area["x"] + 10
                    y = area["y"] + 10
            
            # Draw text with stroke for better visibility
            if stroke_width > 0:
                # Draw stroke
                for dx in [-stroke_width, 0, stroke_width]:
                    for dy in [-stroke_width, 0, stroke_width]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=fill)
            
        except Exception as e:
            # Fallback: draw simple text at area start
            try:
                draw.text((area["x"] + 10, area["y"] + 10), text, fill=fill)
            except:
                pass  # Skip if even fallback fails