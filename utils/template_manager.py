"""
Template-based advertisement generation system
Creates templates with designated spots for logos, taglines, and other brand elements
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional

class TemplateManager:
    """Manages advertisement templates with placeholder areas for brand elements"""
    
    def __init__(self):
        self.templates_dir = "templates"
        self.custom_templates_dir = "templates/custom"
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.custom_templates_dir, exist_ok=True)
        self.load_default_templates()
    
    def load_default_templates(self):
        """Load default template configurations"""
        self.templates = {
            "billboard_horizontal": {
                "name": "Billboard Horizontal",
                "dimensions": (1920, 1080),
                "logo_area": {"x": 50, "y": 50, "width": 300, "height": 150},
                "title_area": {"x": 400, "y": 50, "width": 1000, "height": 200},
                "tagline_area": {"x": 400, "y": 250, "width": 800, "height": 80},
                "content_area": {"x": 50, "y": 350, "width": 1200, "height": 500},
                "cta_area": {"x": 1300, "y": 750, "width": 400, "height": 150},
                "background_prompt": "Create vibrant background design for outdoor billboard with high contrast and bold visual elements"
            },
            "social_media_square": {
                "name": "Social Media Square",
                "dimensions": (1080, 1080),
                "logo_area": {"x": 50, "y": 50, "width": 200, "height": 100},
                "title_area": {"x": 50, "y": 180, "width": 980, "height": 160},
                "tagline_area": {"x": 50, "y": 360, "width": 800, "height": 70},
                "content_area": {"x": 50, "y": 450, "width": 980, "height": 350},
                "cta_area": {"x": 50, "y": 820, "width": 300, "height": 100},
                "background_prompt": "Create modern, mobile-friendly background design with engaging colors and clean layout"
            },
            "web_banner_wide": {
                "name": "Web Banner Wide",
                "dimensions": (728, 300),
                "logo_area": {"x": 20, "y": 20, "width": 150, "height": 75},
                "title_area": {"x": 200, "y": 20, "width": 400, "height": 100},
                "tagline_area": {"x": 200, "y": 120, "width": 350, "height": 40},
                "content_area": {"x": 20, "y": 170, "width": 500, "height": 100},
                "cta_area": {"x": 550, "y": 200, "width": 150, "height": 60},
                "background_prompt": "Create clean web-optimized background design with professional appearance and clear visual hierarchy"
            }
        }
    
    def get_available_templates(self) -> Dict:
        """Return list of available templates including custom ones"""
        templates = {}
        
        # Add built-in templates
        for k, v in self.templates.items():
            templates[k] = v["name"]
        
        # Add custom templates
        custom_templates = self.get_custom_templates()
        for template_name in custom_templates:
            template_id = f"custom_{template_name.lower().replace(' ', '_')}"
            templates[template_id] = f"📝 {template_name} (Custom)"
        
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
        """Get specific template configuration"""
        # Check if it's a custom template
        if template_id.startswith("custom_"):
            template_name = template_id[7:].replace('_', ' ').title()
            custom_template = self.load_custom_template(template_name)
            if custom_template:
                # Convert custom template format to standard format
                return self._convert_custom_template(custom_template)
        
        # Return built-in template
        return self.templates.get(template_id)
    
    def _convert_custom_template(self, custom_template: Dict) -> Dict:
        """Convert custom template format to standard template format"""
        # Extract element positions for compatibility
        elements = custom_template.get("elements", [])
        
        # Find key areas from elements
        logo_area = None
        title_area = None
        tagline_area = None
        content_area = None
        cta_area = None
        
        for element in elements:
            if element["type"] == "logo":
                logo_area = {
                    "x": element["position"]["x"],
                    "y": element["position"]["y"], 
                    "width": element["size"]["width"],
                    "height": element["size"]["height"]
                }
            elif element["type"] == "text" and "client_name" in element.get("content", ""):
                title_area = {
                    "x": element["position"]["x"],
                    "y": element["position"]["y"],
                    "width": element["size"]["width"], 
                    "height": element["size"]["height"]
                }
            elif element["type"] == "text" and "tagline" in element.get("content", ""):
                tagline_area = {
                    "x": element["position"]["x"],
                    "y": element["position"]["y"],
                    "width": element["size"]["width"],
                    "height": element["size"]["height"]
                }
            elif element["type"] == "text" and "prompt" in element.get("content", ""):
                content_area = {
                    "x": element["position"]["x"],
                    "y": element["position"]["y"],
                    "width": element["size"]["width"],
                    "height": element["size"]["height"]
                }
            elif element["type"] == "button":
                cta_area = {
                    "x": element["position"]["x"],
                    "y": element["position"]["y"],
                    "width": element["size"]["width"],
                    "height": element["size"]["height"]
                }
        
        # Provide defaults if areas not found
        dimensions = custom_template.get("dimensions", [1080, 1080])
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
                                 content_prompt: str) -> str:
        """Generate AI prompt for template background creation"""
        template = self.get_template(template_id)
        if not template:
            return ""
        
        background_prompt = f"""
        Create a professional advertisement background design.
        Style: {style}
        Color scheme: {color_scheme}
        Content theme: {content_prompt}
        
        DESIGN REQUIREMENTS:
        - Dimensions: {template['dimensions'][0]}x{template['dimensions'][1]} pixels
        - Create background that complements the content theme: {content_prompt}
        - Use appropriate colors for the {color_scheme} color scheme
        - Include subtle thematic elements related to: {content_prompt}
        - Create depth with gradients and lighting effects
        - Make background complementary to the advertising message
        - Style should be: {style}
        
        CONTENT RESTRICTIONS:
        - DO NOT include any readable text, letters, or words
        - DO NOT include company logos or brand names
        - DO NOT include specific prices, percentages, or numbers
        - Focus on atmospheric design elements that support the theme
        
        TEMPLATE AREAS (keep these areas visually clean for text overlay):
        - Logo area: top-left ({template['logo_area']['width']}x{template['logo_area']['height']} pixels)
        - Title area: main heading space for company name
        - Content area: central space for main message
        - Button area: call-to-action space
        
        Create a professional advertisement background that enhances the {content_prompt} theme and supports excellent text readability.
        """
        
        return background_prompt.strip()
    
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
                "prompt": main_message,
                "cta_text": cta_text,
                "client_website": website
            })
        
        # Use standard template application for built-in templates
        return self._apply_standard_elements(background_image, template, logo, client_name, tagline, main_message, cta_text, website, color_scheme)
    
    def _apply_custom_elements(self, background_image: Image.Image, template: Dict, data: Dict) -> Image.Image:
        """Apply custom template elements with advanced positioning"""
        result_image = background_image.copy()
        draw = ImageDraw.Draw(result_image)
        
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
                position = element.get("position", {})
                size = element.get("size", {})
                content = element.get("content", "")
                style = element.get("style", {})
                
                # Replace template variables in content
                for var, value in data.items():
                    if value and f"{{{{{var}}}}}" in content:
                        content = content.replace(f"{{{{{var}}}}}", str(value))
                
                # Apply element based on type
                if element_type == "text" and content and not content.startswith("{{"):
                    self._draw_custom_text(draw, content, position, size, style, fonts)
                
                elif element_type == "logo" and data.get("logo"):
                    self._draw_custom_logo(result_image, data["logo"], position, size, style)
                
                elif element_type == "button" and content and not content.startswith("{{"):
                    self._draw_custom_button(draw, content, position, size, style, fonts, data.get("client_website"))
                
                elif element_type == "shape":
                    self._draw_custom_shape(draw, position, size, style)
                    
            except Exception as e:
                # Continue with other elements if one fails
                continue
        
        return result_image
    
    def _draw_custom_text(self, draw, text: str, position: Dict, size: Dict, style: Dict, fonts: Dict):
        """Draw custom text element"""
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
        stroke_width = 2 if font_size > 40 else 1
        
        draw.text((x, y), text, font=font, fill=color, stroke_width=stroke_width, stroke_fill="black")
    
    def _draw_custom_logo(self, image: Image.Image, logo: Image.Image, position: Dict, size: Dict, style: Dict):
        """Draw custom logo element"""
        x, y = position.get('x', 0), position.get('y', 0)
        width, height = size.get('width', 200), size.get('height', 100)
        
        # Resize logo to fit
        resized_logo = self._resize_logo_to_area(logo, {'width': width, 'height': height})
        if resized_logo:
            image.paste(resized_logo, (x, y), resized_logo if resized_logo.mode == 'RGBA' else None)
    
    def _draw_custom_button(self, draw, text: str, position: Dict, size: Dict, style: Dict, fonts: Dict, website: str = ""):
        """Draw custom button element"""
        x, y = position.get('x', 0), position.get('y', 0)
        width, height = size.get('width', 200), size.get('height', 60)
        bg_color = style.get('bg_color', '#FF6600')
        text_color = style.get('text_color', '#FFFFFF')
        border_radius = style.get('border_radius', 10)
        
        # Draw button background
        draw.rounded_rectangle([x, y, x + width, y + height], radius=border_radius, fill=bg_color)
        
        # Draw button text
        font = fonts['medium']
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x + (width - text_width) // 2
        text_y = y + (height - text_height) // 2
        
        draw.text((text_x, text_y), text, font=font, fill=text_color)
        
        # Draw website below button if provided
        if website:
            website_y = y + height + 10
            draw.text((x, website_y), website, font=fonts['small'], fill="#CCCCCC")
    
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
        
        # Apply title (client name) - this is the only required field
        if client_name.strip():
            try:
                title_area = template["title_area"]
                display_name = client_name.upper() if len(client_name) < 20 else client_name
                self._draw_text_in_area(draw, display_name, title_area, title_font, fill=colors["primary"], stroke_width=3, stroke_fill="#000000")
            except Exception as e:
                # Fallback with default font
                try:
                    draw.text((template["title_area"]["x"] + 20, template["title_area"]["y"] + 20), client_name.upper(), fill=colors["primary"])
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
        
        # Apply main message - only if provided (dynamic content)
        if main_message.strip():
            try:
                content_area = template["content_area"]
                # Make promotional messages more prominent
                is_promotional = any(keyword in main_message.lower() for keyword in ['sale', 'off', '%', 'discount', 'deal', 'special', 'limited'])
                display_message = main_message.upper() if is_promotional else main_message
                text_color = colors["accent"] if is_promotional else colors["primary"]
                self._draw_text_in_area(draw, display_message, content_area, content_font, fill=text_color, stroke_width=2, stroke_fill="#000000")
            except Exception as e:
                try:
                    # Fallback with prominent positioning
                    display_message = main_message.upper() if any(keyword in main_message.lower() for keyword in ['sale', 'off', '%']) else main_message
                    draw.text((template["content_area"]["x"] + 20, template["content_area"]["y"] + 20), display_message, fill=colors["accent"])
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