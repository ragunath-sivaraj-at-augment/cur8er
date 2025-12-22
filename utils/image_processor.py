from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io
import numpy as np
from typing import Tuple, Optional
import streamlit as st

class ImageProcessor:
    """
    Handles image processing tasks for ad generation
    
    SIMPLIFIED FOR TEMPLATE SYSTEM:
    - Logo processing: Minimal conversion to RGBA
    - Placement & sizing: Handled by template_manager
    - Reference images: Used directly with Nano Banana Pro
    - Background processing: Handled by AI + templates
    """
    
    @staticmethod
    def process_logo(uploaded_file) -> Optional[Image.Image]:
        """Minimal logo processing for template system"""
        try:
            # Handle PIL Image objects directly (after MediaFileStorageError fix)
            if isinstance(uploaded_file, Image.Image):
                logo = uploaded_file
            # Handle file upload objects (legacy support)
            elif hasattr(uploaded_file, 'seek') and hasattr(uploaded_file, 'read'):
                uploaded_file.seek(0)  # Reset file pointer
                logo = Image.open(uploaded_file)
            else:
                st.error("Invalid logo file format")
                return None
            
            # Convert to RGBA for transparency support in templates
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # That's it! Template manager handles sizing and placement
            return logo
            
        except Exception as e:
            st.error(f"Error processing logo: {str(e)}")
            return None
    
    # ========================================
    # DEPRECATED FUNCTIONS - Template System Handles These Tasks
    # ========================================
    # The following functions are no longer needed since:
    # 1. Template system handles logo placement and sizing
    # 2. Reference images provide better AI guidance
    # 3. Templates ensure precise brand element positioning
    
    @staticmethod
    def remove_background_basic(image: Image.Image) -> Image.Image:
        """DEPRECATED: Basic background removal - templates handle logo placement better"""
        # Templates place logos with proper transparency handling
        return image
    
    @staticmethod
    def resize_logo(logo: Image.Image, max_size: int = 200) -> Image.Image:
        """DEPRECATED: Logo resizing - template_manager._resize_logo_to_area() handles this"""
        # Template manager has smarter resizing for specific template areas
        return logo
    
    @staticmethod
    def add_logo_to_ad(ad_image: Image.Image, logo: Image.Image, 
                       position: str = "bottom-right") -> Image.Image:
        """DEPRECATED: Logo placement - templates provide precise positioning"""
        # Templates handle logo placement with perfect positioning
        return ad_image
    
    @staticmethod
    def apply_brand_colors(image: Image.Image, primary_color: str, 
                          secondary_color: str = None) -> Image.Image:
        """Apply brand colors to the image (basic color overlay)"""
        try:
            # This is a placeholder for brand color application
            # In practice, this would involve more sophisticated color manipulation
            return image
        except Exception:
            return image
    
    @staticmethod
    def enhance_image_quality(image: Image.Image) -> Image.Image:
        """Apply quality enhancements to the generated image"""
        try:
            # Apply subtle sharpening
            enhanced = image.filter(ImageFilter.UnsharpMask(
                radius=1, 
                percent=150, 
                threshold=3
            ))
            
            # Enhance contrast slightly
            enhanced = ImageOps.autocontrast(enhanced, cutoff=0.5)
            
            return enhanced
            
        except Exception:
            return image
    
    @staticmethod
    def add_text_overlay(image: Image.Image, text: str, position: str = "center",
                        font_size: int = None, color: str = "white") -> Image.Image:
        """Add text overlay to image"""
        try:
            # Make a copy
            result = image.copy()
            draw = ImageDraw.Draw(result)
            
            # Calculate font size if not provided
            if font_size is None:
                font_size = min(result.size) // 20
            
            # Try to load a good font
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position
            img_width, img_height = result.size
            
            positions = {
                "center": (img_width // 2 - text_width // 2, img_height // 2 - text_height // 2),
                "top": (img_width // 2 - text_width // 2, img_height // 10),
                "bottom": (img_width // 2 - text_width // 2, img_height - img_height // 10 - text_height),
                "top-left": (img_width // 20, img_height // 20),
                "top-right": (img_width - text_width - img_width // 20, img_height // 20),
                "bottom-left": (img_width // 20, img_height - img_height // 20 - text_height),
                "bottom-right": (img_width - text_width - img_width // 20, 
                               img_height - img_height // 20 - text_height)
            }
            
            x, y = positions.get(position, positions["center"])
            
            # Add text with outline for better visibility
            outline_color = "black" if color == "white" else "white"
            
            # Draw outline
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x + adj, y + adj2), text, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=color)
            
            return result
            
        except Exception as e:
            st.error(f"Error adding text overlay: {str(e)}")
            return image
    
    @staticmethod
    def create_border(image: Image.Image, border_width: int = 5, 
                     border_color: str = "white") -> Image.Image:
        """Add a border to the image"""
        try:
            return ImageOps.expand(image, border=border_width, fill=border_color)
        except Exception:
            return image
    
    @staticmethod
    def resize_for_platform(image: Image.Image, platform: str) -> Image.Image:
        """Resize image for specific social media platforms"""
        platform_sizes = {
            "instagram_post": (1080, 1080),
            "instagram_story": (1080, 1920),
            "facebook_post": (1200, 630),
            "facebook_cover": (820, 312),
            "twitter_post": (1200, 675),
            "linkedin_post": (1200, 627),
            "youtube_thumbnail": (1280, 720)
        }
        
        target_size = platform_sizes.get(platform.lower())
        if target_size:
            return image.resize(target_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def apply_filter(image: Image.Image, filter_type: str) -> Image.Image:
        """Apply various filters to the image"""
        try:
            if filter_type == "blur":
                return image.filter(ImageFilter.GaussianBlur(radius=2))
            elif filter_type == "sharpen":
                return image.filter(ImageFilter.SHARPEN)
            elif filter_type == "emboss":
                return image.filter(ImageFilter.EMBOSS)
            elif filter_type == "edge":
                return image.filter(ImageFilter.FIND_EDGES)
            elif filter_type == "smooth":
                return image.filter(ImageFilter.SMOOTH)
            else:
                return image
        except Exception:
            return image
    
    @staticmethod
    def save_processed_image(image: Image.Image, filename: str, 
                           format: str = "PNG", quality: int = 95) -> bool:
        """Save processed image to file"""
        try:
            # Ensure assets directory exists
            import os
            os.makedirs("assets/generated_ads", exist_ok=True)
            
            filepath = f"assets/generated_ads/{filename}"
            
            if format.upper() == "JPEG" or format.upper() == "JPG":
                # Convert RGBA to RGB for JPEG
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                image.save(filepath, format="JPEG", quality=quality)
            else:
                image.save(filepath, format=format.upper())
            
            return True
            
        except Exception as e:
            st.error(f"Error saving image: {str(e)}")
            return False