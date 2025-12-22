"""
Visual Layout Builder
Drag-and-drop canvas system for creating reference images
"""

from PIL import Image, ImageDraw, ImageFont
import io
from typing import List, Tuple, Dict

class LayoutElement:
    """Represents a draggable element on the canvas"""
    def __init__(self, label: str, x: int, y: int, width: int, height: int, element_type: str):
        self.label = label  # e.g., "[LOGO]", "[BRAND NAME]"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.element_type = element_type  # logo, brand, message, tagline, cta
        
    def to_dict(self):
        return {
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "type": self.element_type
        }
    
    @staticmethod
    def from_dict(data):
        return LayoutElement(
            data["label"],
            data["x"],
            data["y"],
            data["width"],
            data["height"],
            data["type"]
        )


class VisualLayoutCanvas:
    """Canvas for creating visual layout reference images"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.elements: List[LayoutElement] = []
        self.background_color = '#2a2a2a'
        self.text_color = 'white'
        self.box_color = 'white'
        
    def add_element(self, element: LayoutElement):
        """Add an element to the canvas"""
        self.elements.append(element)
    
    def remove_element(self, index: int):
        """Remove an element by index"""
        if 0 <= index < len(self.elements):
            del self.elements[index]
    
    def clear(self):
        """Clear all elements"""
        self.elements = []
    
    def get_default_elements(self) -> List[LayoutElement]:
        """Get default element positions"""
        return [
            LayoutElement("[LOGO]", 100, 80, 200, 120, "logo"),
            LayoutElement("[BRAND NAME]", self.width//2 - 200, 200, 400, 100, "brand"),
            LayoutElement("[MAIN MESSAGE]", self.width//2 - 400, self.height//2 - 80, 800, 160, "message"),
            LayoutElement("[TAGLINE]", self.width//2 - 250, self.height//2 + 100, 500, 60, "tagline"),
            LayoutElement("[CTA]", self.width//2 - 150, self.height - 200, 300, 80, "cta"),
        ]
    
    def render_to_image(self) -> Image.Image:
        """
        Render the current layout to a PIL Image
        
        Returns:
            PIL Image with placeholder boxes and labels
        """
        # Create canvas
        img = Image.new('RGB', (self.width, self.height), color=self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts
        try:
            font_large = ImageFont.truetype("arial.ttf", 80)
            font_medium = ImageFont.truetype("arial.ttf", 60)
            font_small = ImageFont.truetype("arial.ttf", 40)
        except:
            # Fallback to default
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw each element
        for elem in self.elements:
            # Select font based on element type
            if elem.element_type == "message":
                font = font_large
            elif elem.element_type in ["brand", "tagline"]:
                font = font_medium
            else:
                font = font_small
            
            # Draw box
            draw.rectangle(
                [elem.x, elem.y, elem.x + elem.width, elem.y + elem.height],
                outline=self.box_color,
                width=3
            )
            
            # Draw label centered in box
            bbox = draw.textbbox((0, 0), elem.label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = elem.x + (elem.width - text_width) // 2
            text_y = elem.y + (elem.height - text_height) // 2
            
            draw.text((text_x, text_y), elem.label, fill=self.text_color, font=font)
        
        # Add instruction text at bottom
        instruction = "Visual Layout Reference - AI will use this composition"
        try:
            inst_font = ImageFont.truetype("arial.ttf", 30)
        except:
            inst_font = font_small
        
        draw.text((self.width//2 - 300, self.height - 50), instruction, 
                 fill='#888888', font=inst_font)
        
        return img
    
    def to_bytes(self, format='PNG') -> bytes:
        """
        Convert rendered image to bytes for download/upload
        
        Returns:
            Image bytes
        """
        img = self.render_to_image()
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()
    
    def save_layout(self) -> Dict:
        """
        Save layout configuration as JSON-serializable dict
        
        Returns:
            Layout configuration
        """
        return {
            "width": self.width,
            "height": self.height,
            "elements": [elem.to_dict() for elem in self.elements]
        }
    
    @staticmethod
    def load_layout(config: Dict) -> 'VisualLayoutCanvas':
        """
        Load layout from saved configuration
        
        Args:
            config: Layout configuration dict
        
        Returns:
            VisualLayoutCanvas instance
        """
        canvas = VisualLayoutCanvas(config["width"], config["height"])
        canvas.elements = [LayoutElement.from_dict(e) for e in config["elements"]]
        return canvas


class SimpleLayoutBuilder:
    """Simplified builder for quick layout creation without complex drag-drop"""
    
    @staticmethod
    def create_layout(
        dimensions: Tuple[int, int],
        include_logo: bool = True,
        include_brand: bool = True,
        include_message: bool = True,
        include_tagline: bool = False,
        include_cta: bool = True,
        layout_style: str = "centered"
    ) -> Image.Image:
        """
        Create a simple layout based on selections
        
        Args:
            dimensions: (width, height)
            include_*: Which elements to include
            layout_style: "centered", "left-aligned", "asymmetric"
        
        Returns:
            PIL Image reference
        """
        width, height = dimensions
        canvas = VisualLayoutCanvas(width, height)
        
        if layout_style == "centered":
            y_offset = 150
            
            if include_logo:
                canvas.add_element(LayoutElement("[LOGO]", 100, 80, 200, 120, "logo"))
                
            if include_brand:
                canvas.add_element(LayoutElement("[BRAND NAME]", width//2 - 200, y_offset, 400, 100, "brand"))
                y_offset += 150
            
            if include_message:
                canvas.add_element(LayoutElement("[MAIN MESSAGE]", width//2 - 400, y_offset, 800, 160, "message"))
                y_offset += 200
                
            if include_tagline:
                canvas.add_element(LayoutElement("[TAGLINE]", width//2 - 250, y_offset, 500, 60, "tagline"))
                y_offset += 100
                
            if include_cta:
                canvas.add_element(LayoutElement("[CTA]", width//2 - 150, height - 200, 300, 80, "cta"))
        
        elif layout_style == "left-aligned":
            x_base = 150
            y_offset = 150
            
            if include_logo:
                canvas.add_element(LayoutElement("[LOGO]", x_base, 80, 200, 120, "logo"))
                
            if include_brand:
                canvas.add_element(LayoutElement("[BRAND NAME]", x_base, y_offset, 500, 100, "brand"))
                y_offset += 150
                
            if include_message:
                canvas.add_element(LayoutElement("[MAIN MESSAGE]", x_base, y_offset, 900, 160, "message"))
                y_offset += 200
                
            if include_tagline:
                canvas.add_element(LayoutElement("[TAGLINE]", x_base, y_offset, 600, 60, "tagline"))
                y_offset += 100
                
            if include_cta:
                canvas.add_element(LayoutElement("[CTA]", x_base, height - 200, 300, 80, "cta"))
        
        elif layout_style == "asymmetric":
            if include_logo:
                canvas.add_element(LayoutElement("[LOGO]", width - 350, 80, 200, 120, "logo"))
                
            if include_brand:
                canvas.add_element(LayoutElement("[BRAND NAME]", 200, 250, 400, 100, "brand"))
                
            if include_message:
                canvas.add_element(LayoutElement("[MAIN MESSAGE]", width//2 - 300, height//2 - 80, 700, 160, "message"))
                
            if include_tagline:
                canvas.add_element(LayoutElement("[TAGLINE]", width - 650, height//2 + 100, 500, 60, "tagline"))
                
            if include_cta:
                canvas.add_element(LayoutElement("[CTA]", 200, height - 200, 300, 80, "cta"))
        
        return canvas.render_to_image()
