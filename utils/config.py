from typing import Dict, Tuple, List
import json
import os

class EnvironmentManager:
    """Manages environment variables with support for both .env files and Streamlit secrets"""
    
    @staticmethod
    def get_config_value(key: str, default: str = None) -> str:
        """
        Get configuration value from either Streamlit secrets or environment variables
        Priority: Streamlit secrets > Environment variables > Default
        """
        try:
            # Try Streamlit secrets first (for deployed apps)
            import streamlit as st
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except ImportError:
            # Streamlit not available, continue to env vars
            pass
        except Exception:
            # Secrets not configured or error accessing them
            pass
        
        # Fall back to environment variables (for local development)
        value = os.getenv(key, default)
        return value
    
    @staticmethod
    def is_streamlit_deployment() -> bool:
        """Check if running in Streamlit Cloud/deployment environment"""
        try:
            import streamlit as st
            return hasattr(st, 'secrets') and bool(st.secrets)
        except ImportError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_all_api_keys() -> Dict[str, str]:
        """Get all API keys from the environment"""
        keys = {
            'OPENAI_API_KEY': EnvironmentManager.get_config_value('OPENAI_API_KEY'),
            'GOOGLE_API_KEY': EnvironmentManager.get_config_value('GOOGLE_API_KEY'),
            'NANO_BANANA_API_KEY': EnvironmentManager.get_config_value('NANO_BANANA_API_KEY')
        }
        # Filter out None values
        return {k: v for k, v in keys.items() if v is not None}

class Config:
    """Configuration settings for the ad creator application"""
    
    # Environment manager instance
    env = EnvironmentManager()
    
    # Predefined ad sizes with dimensions
    AD_SIZES = {
        "Square (1080x1080) - Instagram Post": (1080, 1080),
        "Landscape (1920x1080) - YouTube Thumbnail": (1920, 1080),
        "Portrait (1080x1920) - Instagram Story": (1080, 1920),
        "Banner (728x90) - Web Banner": (728, 90),
        "Leaderboard (970x250) - Web Header": (970, 250),
        "Facebook Cover (820x312)": (820, 312),
        "LinkedIn Post (1200x627)": (1200, 627),
        "Facebook Post (1200x630)": (1200, 630),
        "Twitter Header (1500x500)": (1500, 500),
        "Pinterest Pin (736x1128)": (736, 1128),
        "A4 Print (2480x3508)": (2480, 3508),
        "Letter Print (2550x3300)": (2550, 3300)
    }
    
    # Ad mediums and their characteristics
    AD_MEDIUMS = {
        "Social Media - Instagram": {
            "recommended_sizes": ["Square (1080x1080)", "Portrait (1080x1920)"],
            "color_profile": "sRGB",
            "text_style": "bold, engaging"
        },
        "Social Media - Facebook": {
            "recommended_sizes": ["Facebook Post (1200x630)", "Facebook Cover (820x312)"],
            "color_profile": "sRGB",
            "text_style": "clear, informative"
        },
        "Social Media - Twitter/X": {
            "recommended_sizes": ["Twitter Header (1500x500)", "Landscape (1920x1080)"],
            "color_profile": "sRGB",
            "text_style": "concise, impactful"
        },
        "Social Media - LinkedIn": {
            "recommended_sizes": ["LinkedIn Post (1200x627)"],
            "color_profile": "sRGB",
            "text_style": "professional, corporate"
        },
        "Digital Display - Web Banner": {
            "recommended_sizes": ["Banner (728x90)", "Leaderboard (970x250)"],
            "color_profile": "sRGB",
            "text_style": "attention-grabbing"
        },
        "Digital Display - Mobile App": {
            "recommended_sizes": ["Banner (320x50)", "Square (300x300)"],
            "color_profile": "sRGB",
            "text_style": "mobile-friendly"
        },
        "Print - Magazine": {
            "recommended_sizes": ["A4 Print (2480x3508)", "Letter Print (2550x3300)"],
            "color_profile": "CMYK",
            "text_style": "high-contrast, readable"
        },
        "Print - Newspaper": {
            "recommended_sizes": ["Letter Print (2550x3300)"],
            "color_profile": "CMYK",
            "text_style": "clear, newspaper-style"
        },
        "Outdoor - Billboard": {
            "recommended_sizes": ["Custom Size"],
            "color_profile": "sRGB",
            "text_style": "large, bold, visible from distance"
        },
        "Email Marketing": {
            "recommended_sizes": ["Banner (600x200)", "Square (400x400)"],
            "color_profile": "sRGB",
            "text_style": "compelling, action-oriented"
        },
        "YouTube/Video Platform": {
            "recommended_sizes": ["Landscape (1920x1080)", "YouTube Thumbnail (1280x720)"],
            "color_profile": "sRGB",
            "text_style": "eye-catching, clickable"
        }
    }
    
    # Style presets with their characteristics
    STYLE_PRESETS = {
        "Modern & Minimalist": {
            "color_palette": ["#FFFFFF", "#F5F5F5", "#333333", "#007AFF"],
            "typography": "clean, sans-serif",
            "layout": "lots of whitespace, simple composition",
            "keywords": "clean, minimalist, modern, simple, elegant"
        },
        "Bold & Vibrant": {
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"],
            "typography": "bold, impact fonts",
            "layout": "high contrast, dynamic composition",
            "keywords": "vibrant, energetic, bold, colorful, dynamic"
        },
        "Elegant & Professional": {
            "color_palette": ["#2C3E50", "#34495E", "#BDC3C7", "#ECF0F1"],
            "typography": "serif, professional fonts",
            "layout": "balanced, sophisticated",
            "keywords": "professional, elegant, sophisticated, corporate, refined"
        },
        "Retro & Vintage": {
            "color_palette": ["#D4A574", "#8B4513", "#F4E4BC", "#A0522D"],
            "typography": "vintage, decorative fonts",
            "layout": "nostalgic, textured",
            "keywords": "retro, vintage, nostalgic, classic, timeless"
        },
        "Futuristic & Tech": {
            "color_palette": ["#00FFFF", "#FF00FF", "#00FF00", "#1E1E1E"],
            "typography": "geometric, tech fonts",
            "layout": "geometric, high-tech",
            "keywords": "futuristic, tech, digital, cyber, modern"
        },
        "Natural & Organic": {
            "color_palette": ["#8FBC8F", "#228B22", "#F5F5DC", "#DEB887"],
            "typography": "organic, handwritten fonts",
            "layout": "natural, flowing",
            "keywords": "natural, organic, eco-friendly, green, sustainable"
        },
        "Luxury & Premium": {
            "color_palette": ["#FFD700", "#000000", "#FFFFFF", "#C0C0C0"],
            "typography": "luxury, premium fonts",
            "layout": "sophisticated, premium",
            "keywords": "luxury, premium, exclusive, high-end, sophisticated"
        },
        "Playful & Fun": {
            "color_palette": ["#FF69B4", "#00CED1", "#FFD700", "#98FB98"],
            "typography": "playful, rounded fonts",
            "layout": "fun, energetic, playful",
            "keywords": "playful, fun, energetic, cheerful, vibrant"
        }
    }
    
    # Color schemes
    COLOR_SCHEMES = {
        "Brand Colors": "Use the client's brand colors as primary palette",
        "Warm Tones": ["#FF6B6B", "#FF8E53", "#FF6B35", "#F7931E"],
        "Cool Tones": ["#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
        "Monochrome": ["#FFFFFF", "#F8F9FA", "#E9ECEF", "#6C757D", "#343A40", "#000000"],
        "High Contrast": ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"],
        "Pastel": ["#FFE5E5", "#E5F3FF", "#E5FFE5", "#FFFFE5", "#F0E5FF"]
    }
    
    # File type configurations
    FILE_FORMATS = {
        "PNG": {
            "extension": ".png",
            "mime_type": "image/png",
            "supports_transparency": True,
            "best_for": "logos, graphics with transparency"
        },
        "JPEG": {
            "extension": ".jpg",
            "mime_type": "image/jpeg",
            "supports_transparency": False,
            "best_for": "photos, detailed images"
        },
        "WebP": {
            "extension": ".webp",
            "mime_type": "image/webp",
            "supports_transparency": True,
            "best_for": "web optimization"
        },
        "PDF": {
            "extension": ".pdf",
            "mime_type": "application/pdf",
            "supports_transparency": False,
            "best_for": "print materials"
        }
    }
    
    @classmethod
    def get_dimensions(cls, size_name: str) -> Tuple[int, int]:
        """Get dimensions for a predefined size"""
        return cls.AD_SIZES.get(size_name, (1080, 1080))
    
    @classmethod
    def get_recommended_sizes(cls, medium: str) -> List[str]:
        """Get recommended sizes for a specific medium"""
        medium_config = cls.AD_MEDIUMS.get(medium, {})
        return medium_config.get("recommended_sizes", ["Square (1080x1080) - Instagram Post"])
    
    @classmethod
    def get_style_config(cls, style_name: str) -> Dict:
        """Get configuration for a style preset"""
        return cls.STYLE_PRESETS.get(style_name, cls.STYLE_PRESETS["Modern & Minimalist"])
    
    @classmethod
    def get_color_scheme(cls, scheme_name: str) -> List[str]:
        """Get colors for a color scheme"""
        return cls.COLOR_SCHEMES.get(scheme_name, ["#FFFFFF", "#000000"])
    
    @classmethod
    def save_user_preferences(cls, preferences: Dict, filename: str = "user_preferences.json"):
        """Save user preferences to file"""
        try:
            os.makedirs("assets", exist_ok=True)
            with open(f"assets/{filename}", 'w') as f:
                json.dump(preferences, f, indent=2)
            return True
        except Exception:
            return False
    
    @classmethod
    def load_user_preferences(cls, filename: str = "user_preferences.json") -> Dict:
        """Load user preferences from file"""
        try:
            with open(f"assets/{filename}", 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    @classmethod
    def get_default_prompt_templates(cls) -> Dict[str, str]:
        """Get default prompt templates for different types of ads"""
        return {
            "Product Sale": "A professional advertisement for {product_name} featuring a {discount}% discount. Modern design with bold typography, vibrant colors, and clear pricing information. High-quality product photography with attractive sale badges.",
            
            "Service Promotion": "An elegant advertisement promoting {service_name} services. Professional and trustworthy design with client testimonials, service benefits, and clear call-to-action. Corporate color scheme with modern typography.",
            
            "Event Advertisement": "An exciting advertisement for {event_name} event. Dynamic and energetic design with event details, date, location, and registration information. Eye-catching graphics and vibrant color palette.",
            
            "Brand Awareness": "A sophisticated brand awareness advertisement for {brand_name}. Clean and minimalist design showcasing brand values, logo prominence, and memorable tagline. Professional color scheme matching brand identity.",
            
            "Holiday Campaign": "A festive advertisement for {holiday_name} campaign. Seasonal design elements, appropriate color scheme, special offers, and holiday-themed graphics. Warm and inviting atmosphere.",
            
            "New Product Launch": "An innovative advertisement announcing the launch of {product_name}. Modern and cutting-edge design highlighting product features, benefits, and availability. Technology-inspired color palette and typography."
        }
    
    # Application settings
    APP_CONFIG = {
        "title": "Cur8er",
        "version": "1.0.0",
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "supported_image_formats": ["PNG", "JPG", "JPEG", "SVG", "WebP"],
        "default_ai_model": "DALL-E 3",
        "cache_generated_images": True,
        "auto_save_preferences": True
    }