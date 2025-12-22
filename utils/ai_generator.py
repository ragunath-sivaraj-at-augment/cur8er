from openai import OpenAI
import requests
import io
from PIL import Image
import os
from typing import Optional, Tuple
import streamlit as st
import time
from .prompts import PromptBuilder
from .config import EnvironmentManager

class AIImageGenerator:
    """Handles AI image generation from multiple providers"""
    
    def __init__(self, model_name: str = "DALL-E 3"):
        self.model_name = model_name
        self.setup_model()
    
    def setup_model(self):
        """Initialize the selected AI model"""
        if "DALL-E" in self.model_name:
            self.setup_dalle()
        elif "Stable Diffusion" in self.model_name:
            self.setup_stable_diffusion()
        elif "Midjourney" in self.model_name:
            self.setup_midjourney()
        elif "Imagen" in self.model_name:
            self.setup_imagen()
        elif "Nano Banana" in self.model_name:
            self.setup_nano_banana()
    
    def setup_dalle(self):
        """Setup DALL-E API"""
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        
        api_key = EnvironmentManager.get_config_value("OPENAI_API_KEY")
        if not api_key:
            config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
            error_msg = f"OpenAI API key not found. Please add OPENAI_API_KEY to your {config_source}."
            st.error(f"❌ {error_msg}")
            st.info("🔑 Using demo mode instead. Add your API key to generate real images.")
            logger.error(error_msg)
            return False
        
        try:
            self.client = OpenAI(api_key=api_key)
            success_msg = f"DALL-E API configured successfully (key ends with: ...{api_key[-4:]})"
            st.success(f"✅ {success_msg}")
            logger.info(success_msg)
            return True
        except Exception as e:
            error_msg = f"Error setting up DALL-E API: {str(e)}"
            st.error(f"❌ {error_msg}")
            logger.error(error_msg)
            return False
    
    def setup_stable_diffusion(self):
        """Setup Stable Diffusion API (placeholder)"""
        # This would connect to Stable Diffusion API
        st.info("🔧 Stable Diffusion integration coming soon!")
        return False
    
    def setup_midjourney(self):
        """Setup Midjourney API (placeholder)"""
        # This would connect to Midjourney API
        st.info("🔧 Midjourney integration coming soon!")
        return False
    
    def setup_imagen(self):
        """Setup Google Imagen API via Gemini"""
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        
        try:
            api_key = EnvironmentManager.get_config_value("GOOGLE_API_KEY")
            
            if not api_key:
                config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                error_msg = f"Google API key not found. Add GOOGLE_API_KEY to your {config_source} for Imagen."
                st.warning(f"⚠️ {error_msg}")
                st.info("🔑 Using demo mode instead.")
                logger.warning(error_msg)
                return False
            
            try:
                # Use Google Generative AI for Imagen
                import google.generativeai as genai
                
                # Configure the API
                genai.configure(api_key=api_key)
                
                # Test the connection
                model = genai.GenerativeModel('gemini-pro')
                
                self.google_api_key = api_key
                
                success_msg = f"Google Imagen API configured successfully (key ends with: ...{api_key[-4:]})"
                st.success(f"✅ {success_msg}")
                logger.info(success_msg)
                return True
                
            except ImportError:
                error_msg = "Google Generative AI library not installed. Install with: pip install google-generativeai"
                st.warning(f"📦 {error_msg}")
                st.info("🔑 Using demo mode instead.")
                logger.warning(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error setting up Imagen API: {str(e)}"
            st.error(f"❌ {error_msg}")
            st.info("🔑 Using demo mode instead.")
            logger.error(error_msg)
            return False
    
    def setup_nano_banana(self):
        """Setup Nano Banana API - check if Google API key works"""
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        
        try:
            # Nano Banana can use Google API key (preferred) or dedicated key
            google_api_key = EnvironmentManager.get_config_value("GOOGLE_API_KEY")
            nano_api_key = EnvironmentManager.get_config_value("NANO_BANANA_API_KEY")  # Optional dedicated key
            
            if google_api_key:
                st.info("🔄 Using Google API key for Nano Banana...")
                # Test if Google API key can be used for Nano Banana
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=google_api_key)
                    
                    # Look for Google's image generation models instead of "nano banana"
                    models = list(genai.list_models())
                    image_models = [m for m in models if 'image' in str(m.name).lower() or 'vision' in str(m.name).lower() or 'imagen' in str(m.name).lower()]
                    
                    if image_models:
                        st.success(f"✅ Found Google image generation models: {len(image_models)}")
                        for model in image_models[:3]:  # Show first 3
                            st.info(f"   🎨 {model.name}")
                        self.google_api_key = google_api_key
                        self.nano_banana_models = image_models
                        logger.info(f"Google image models found for Nano Banana: {[m.name for m in image_models]}")
                        return True
                    else:
                        # Fallback to trying specific known models
                        known_image_models = [
                            'gemini-3-pro-image-preview',  # Nano Banana Pro
                            'gemini-2.5-flash-image',      # Nano Banana
                            'gemini-pro-vision',
                            'gemini-1.5-pro-vision-latest'
                        ]
                        
                        available_models = []
                        for model_name in known_image_models:
                            try:
                                test_model = genai.GenerativeModel(model_name)
                                available_models.append(model_name)
                                st.success(f"✅ Found working model: {model_name}")
                            except Exception as e:
                                st.info(f"   ❌ {model_name} not available: {str(e)[:50]}...")
                        
                        if available_models:
                            st.success(f"✅ Nano Banana can use {len(available_models)} Google image models")
                            self.google_api_key = google_api_key
                            self.nano_banana_model_names = available_models
                            logger.info(f"Available Google image models: {available_models}")
                            return True
                        else:
                            st.warning("⚠️ No Google image generation models found")
                            st.info("💡 Google API key available but no image models accessible")
                            self.google_api_key = google_api_key
                            logger.info("Google API key available but no image models")
                            return False
                        
                except Exception as e:
                    st.warning(f"⚠️ Could not test Google API: {str(e)}")
                    st.info("🍌 Will use basic demo mode")
                    logger.warning(f"Google API test failed: {str(e)}")
                    return False
                    
            elif nano_api_key:
                st.success(f"✅ Dedicated Nano Banana API key configured")
                self.nano_banana_api_key = nano_api_key
                logger.info("Dedicated Nano Banana API key found")
                return True
            else:
                config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                st.error(f"🍌 Nano Banana Pro cannot generate images without API key")
                st.info(f"💡 Add GOOGLE_API_KEY to your {config_source} to use Nano Banana Pro")
                logger.info("No API keys for Nano Banana")
                return False
                
        except Exception as e:
            st.warning(f"⚠️ Nano Banana setup error: {str(e)}")
            logger.error(f"Nano Banana setup error: {str(e)}")
            return False
    
    def generate_image(self, prompt: str, size: Tuple[int, int], client_logo: Optional[Image.Image] = None) -> Optional[Image.Image]:
        """Generate image based on the selected model"""
        try:
            st.info(f"🎯 Selected model: {self.model_name}")
            st.info(f"📏 Target size: {size[0]}x{size[1]}")
            
            if "DALL-E" in self.model_name:
                st.info("🎨 Attempting to generate with DALL-E...")
                if hasattr(self, 'client') and self.client:
                    st.success(f"✅ {self.model_name} API client is ready")
                else:
                    st.warning(f"⚠️ {self.model_name} API client not configured")
                return self.generate_dalle_image(prompt, size)
            elif "Stable Diffusion" in self.model_name:
                st.info("🎨 Attempting to generate with Stable Diffusion...")
                st.warning("🔧 Stable Diffusion not implemented yet - using demo")
                return self.generate_stable_diffusion_image(prompt, size)
            elif "Midjourney" in self.model_name:
                st.info("🎨 Attempting to generate with Midjourney...")
                st.warning("🔧 Midjourney not implemented yet - using demo")
                return self.generate_midjourney_image(prompt, size)
            elif "Imagen" in self.model_name:
                st.info("🎨 Starting Google Imagen generation...")
                
                # Create persistent status container
                status_container = st.container()
                
                if hasattr(self, 'google_api_key') and self.google_api_key:
                    with status_container:
                        st.success(f"✅ {self.model_name} API key is configured")
                        
                        # Show persistent progress tracking
                        with st.status("🔄 Google Imagen Generation Process", expanded=True) as status:
                            st.write("🔄 Initializing API connection...")
                            result = self.generate_imagen_image(prompt, size)
                            
                            if result:
                                # Save the generated image automatically
                                saved_path = self.save_generated_image(result, prompt)
                                if saved_path:
                                    st.write(f"💾 Image saved to: {saved_path}")
                                    status.update(label="✅ Generation Complete!", state="complete")
                                else:
                                    st.write("⚠️ Image generated but save failed")
                                    status.update(label="⚠️ Partial Success", state="complete")
                            else:
                                st.write("❌ Generation failed")
                                status.update(label="❌ Generation Failed", state="error")
                    
                    return result
                else:
                    with status_container:
                        st.warning(f"⚠️ {self.model_name} API key not configured - using demo mode")
                        with st.status("🍌 Demo Mode Generation", expanded=True) as status:
                            st.write("🔄 Creating demo image...")
                            result = self.generate_imagen_image(prompt, size)
                            
                            if result:
                                saved_path = self.save_generated_image(result, prompt, is_demo=True)
                                if saved_path:
                                    st.write(f"💾 Demo image saved to: {saved_path}")
                                    status.update(label="✅ Demo Complete!", state="complete")
                            
                    return result
            elif "Nano Banana" in self.model_name:
                st.info("🍌 Starting Nano Banana generation...")
                if hasattr(self, 'google_api_key') and self.google_api_key:
                    st.success("✅ Nano Banana using Google API for AI generation")
                elif hasattr(self, 'nano_banana_models') and self.nano_banana_models:
                    st.info("✅ Nano Banana models found via Google API")
                elif hasattr(self, 'nano_banana_api_key') and self.nano_banana_api_key:
                    st.success("✅ Dedicated Nano Banana API configured")
                else:
                    st.info("🍌 Using demo mode (add Google API key for AI generation)")
                return self.generate_nano_banana_image(prompt, size)
            else:
                st.error(f"❌ Unknown model: {self.model_name}")
                st.error("❌ Cannot generate images with unknown model")
                return None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            error_msg = f"Error in generate_image for {self.model_name}: {str(e)}"
            st.error(error_msg)
            logger.error(error_msg)
            st.error("❌ Image generation failed completely")
            return None
    
    def generate_dalle_image(self, prompt: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """Generate image using DALL-E API"""
        try:
            # Check if client is properly set up
            if not hasattr(self, 'client') or not self.client:
                st.error("❌ DALL-E API client not configured. Please check your OPENAI_API_KEY in the .env file.")
                return None
            
            # Convert custom sizes to DALL-E supported sizes
            dalle_size = self.convert_to_dalle_size(size)
            st.info(f"📏 DALL-E size: {dalle_size}")
            
            st.info("🔄 Sending request to OpenAI...")
            
            # === CAPTURE ALL API PARAMETERS ===
            if self.model_name == "DALL-E 3":
                api_params = {
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "size": dalle_size,
                    "quality": "hd",
                    "n": 1,
                }
                
                with st.expander("📡 DALL-E 3 API Call Details", expanded=False):
                    st.json({
                        "api_endpoint": "OpenAI Images API",
                        "method": "images.generate",
                        "parameters": api_params,
                        "prompt_length": len(prompt),
                        "prompt_word_count": len(prompt.split())
                    })
                    st.text_area("Full Prompt:", prompt, height=300)
                
                response = self.client.images.generate(**api_params)
            else:  # DALL-E 2
                api_params = {
                    "model": "dall-e-2",
                    "prompt": prompt,
                    "size": dalle_size,
                    "n": 1,
                }
                
                with st.expander("📡 DALL-E 2 API Call Details", expanded=False):
                    st.json({
                        "api_endpoint": "OpenAI Images API",
                        "method": "images.generate",
                        "parameters": api_params,
                        "prompt_length": len(prompt),
                        "prompt_word_count": len(prompt.split())
                    })
                    st.text_area("Full Prompt:", prompt, height=300)
                
                response = self.client.images.generate(**api_params)
            
            st.success("✅ Received response from OpenAI")
            image_url = response.data[0].url
            st.info(f"🔗 Downloading image from: {image_url[:50]}...")
            
            # Download and convert to PIL Image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                raise Exception(f"Failed to download image: HTTP {image_response.status_code}")
                
            image = Image.open(io.BytesIO(image_response.content))
            st.success(f"✅ Image downloaded: {image.size[0]}x{image.size[1]}")
            
            # Resize to exact dimensions if needed
            if image.size != size:
                st.info(f"🔄 Resizing from {image.size} to {size}")
                image = image.resize(size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            st.error(f"❌ DALL-E Error: {str(e)}")
            st.error("💡 Check your OPENAI_API_KEY configuration and try again.")
            return None
    
    def edit_dalle_image(self, image: Image.Image, prompt: str, mask: Optional[Image.Image] = None) -> Optional[Image.Image]:
        """
        Edit an existing image using DALL-E's image editing capability
        
        Args:
            image: The original image to edit (PIL Image)
            prompt: Description of the desired changes
            mask: Optional mask image (transparent areas will be edited). If None, entire image can be modified.
        
        Returns:
            Edited PIL Image or None if failed
        """
        try:
            # Check if client is properly set up
            if not hasattr(self, 'client') or not self.client:
                st.error("❌ DALL-E API client not configured. Please check your OPENAI_API_KEY in the .env file.")
                return None
            
            # DALL-E edit only works with DALL-E 2, not DALL-E 3
            if self.model_name == "DALL-E 3":
                st.warning("⚠️ DALL-E 3 doesn't support image editing. Using DALL-E 2 for this operation.")
            
            # Prepare image for DALL-E (must be PNG, RGBA, square, and < 4MB)
            st.info("🔄 Preparing image for editing...")
            
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # DALL-E edit requires square images (1024x1024 max)
            original_size = image.size
            max_size = 1024
            
            # Make it square by padding
            max_dim = max(image.size)
            if max_dim > max_size:
                # Scale down proportionally
                scale = max_size / max_dim
                new_width = int(image.size[0] * scale)
                new_height = int(image.size[1] * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create square canvas
            square_size = max(image.size)
            square_image = Image.new('RGBA', (square_size, square_size), (255, 255, 255, 0))
            # Center the image
            offset = ((square_size - image.size[0]) // 2, (square_size - image.size[1]) // 2)
            square_image.paste(image, offset)
            
            # Save to bytes
            image_bytes = io.BytesIO()
            square_image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            
            # Prepare mask if provided
            mask_bytes = None
            if mask:
                if mask.mode != 'RGBA':
                    mask = mask.convert('RGBA')
                # Make mask same size as image
                if mask.size != square_image.size:
                    mask = mask.resize(square_image.size, Image.Resampling.LANCZOS)
                mask_bytes = io.BytesIO()
                mask.save(mask_bytes, format='PNG')
                mask_bytes.seek(0)
            
            st.info("🔄 Sending edit request to OpenAI DALL-E 2...")
            
            # Call DALL-E edit API
            if mask_bytes:
                response = self.client.images.edit(
                    model="dall-e-2",
                    image=image_bytes,
                    mask=mask_bytes,
                    prompt=prompt,
                    n=1,
                    size="1024x1024"
                )
            else:
                response = self.client.images.edit(
                    model="dall-e-2",
                    image=image_bytes,
                    prompt=prompt,
                    n=1,
                    size="1024x1024"
                )
            
            st.success("✅ Received edited image from OpenAI")
            image_url = response.data[0].url
            
            # Download edited image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                raise Exception(f"Failed to download edited image: HTTP {image_response.status_code}")
            
            edited_image = Image.open(io.BytesIO(image_response.content))
            st.success(f"✅ Edited image downloaded: {edited_image.size[0]}x{edited_image.size[1]}")
            
            # Crop back to original aspect ratio if it was padded
            if edited_image.size != original_size:
                # Remove padding and resize to original size
                edited_image = edited_image.crop((offset[0], offset[1], 
                                                  offset[0] + image.size[0], 
                                                  offset[1] + image.size[1]))
                edited_image = edited_image.resize(original_size, Image.Resampling.LANCZOS)
            
            return edited_image
            
        except Exception as e:
            st.error(f"❌ DALL-E Edit Error: {str(e)}")
            st.error("💡 Make sure your image is in a supported format and try again.")
            return None
    
    def generate_stable_diffusion_image(self, prompt: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """Generate image using Stable Diffusion API (placeholder)"""
        st.info("🔧 Stable Diffusion integration in development")
        st.error("❌ Cannot generate images - API not implemented yet")
        return None
    
    def generate_midjourney_image(self, prompt: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """Generate image using Midjourney API (placeholder)"""
        st.info("🔧 Midjourney integration in development")
        st.error("❌ Cannot generate images - API not implemented yet")
        return None
    
    def generate_imagen_image(self, prompt: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """Generate image using Google Imagen API via Gemini"""
        try:
            if not hasattr(self, 'google_api_key') or not self.google_api_key:
                st.write("❌ Google Imagen API not configured")
                st.write("💡 Add GOOGLE_API_KEY to your .env file to generate real images.")
                return None
            
            try:
                import google.generativeai as genai
                import time
                
                # Configure the API
                genai.configure(api_key=self.google_api_key)
                
                # Show detailed status
                st.write("🔗 API configured successfully")
                st.write("🔄 Testing API connection...")
                
                # Check if user cancelled
                if 'cancel_generation' in st.session_state and st.session_state.cancel_generation:
                    st.write("❌ Generation cancelled by user")
                    return None
                
                # Try to use Imagen through different approaches
                success = False
                error_details = []
                
                # Method 1: Check Gemini capabilities
                st.write("📡 Method 1: Checking Gemini image generation...")
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    # Test basic connectivity
                    test_response = model.generate_content("Hello")
                    st.write("✅ Gemini API connection successful")
                    st.write("⚠️ Gemini Pro doesn't support image generation yet")
                    error_details.append("Gemini Pro: Text-only model")
                except Exception as e:
                    st.write(f"❌ Gemini connection failed: {str(e)[:100]}...")
                    error_details.append(f"Gemini API: {str(e)[:50]}...")
                
                # Method 2: Try direct Imagen API
                st.write("📡 Method 2: Attempting Vertex AI Imagen...")
                try:
                    import requests
                    
                    # This is likely to fail without proper Vertex AI setup
                    st.write("🔄 Checking Vertex AI access...")
                    time.sleep(1)  # Simulate checking
                    st.write("❌ Vertex AI requires service account setup")
                    error_details.append("Vertex AI: Service account required")
                    
                except Exception as e:
                    st.write(f"❌ Vertex AI failed: {str(e)[:100]}...")
                    error_details.append(f"Vertex AI: {str(e)[:50]}...")
                
                # Show summary of issues
                st.write("📋 **Issues Found:**")
                for i, error in enumerate(error_details, 1):
                    st.write(f"   {i}. {error}")
                
                st.write("💡 **Solutions:**")
                st.write("   • Get Vertex AI service account for real Imagen access")
                st.write("   • Or wait for Gemini image generation support")
                st.write("   • Cannot generate images without proper API access")
                
                st.write("❌ Image generation failed - no valid API access")
                
                return None
                
            except ImportError:
                st.write("❌ Google Generative AI library not installed")
                st.write("💡 Install with: pip install google-generativeai")
                st.write("❌ Cannot generate images without required library")
                return None
                
        except Exception as e:
            st.write(f"❌ Unexpected error: {str(e)}")
            st.write("❌ Image generation failed")
            return None
    

    
    def save_generated_image(self, image: Image.Image, prompt: str, is_demo: bool = False) -> str:
        """Save generated image to assets/generated_ads folder"""
        try:
            from datetime import datetime
            import re
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Clean prompt for filename (remove special characters)
            clean_prompt = re.sub(r'[^\w\s-]', '', prompt)[:50]
            clean_prompt = re.sub(r'\s+', '_', clean_prompt.strip())
            
            # Create filename
            demo_prefix = "DEMO_" if is_demo else ""
            model_name = self.model_name.replace(" ", "_")
            filename = f"{demo_prefix}{model_name}_{clean_prompt}_{timestamp}.png"
            
            # Full path
            filepath = os.path.join("assets", "generated_ads", filename)
            
            # Save image
            image.save(filepath, "PNG")
            
            return filepath
            
        except Exception as e:
            st.error(f"❌ Failed to save image: {str(e)}")
            return None
    
    def convert_to_imagen_size(self, size: Tuple[int, int]) -> str:
        """Convert custom size to Google Imagen supported aspect ratio"""
        width, height = size
        ratio = width / height
        
        # Google Imagen supported aspect ratios
        if ratio >= 1.5:
            return "16:9"  # Landscape
        elif ratio <= 0.67:
            return "9:16"  # Portrait
        elif 0.9 <= ratio <= 1.1:
            return "1:1"   # Square
        elif ratio > 1.1:
            return "4:3"   # Landscape-ish
        else:
            return "3:4"   # Portrait-ish
    
    def generate_nano_banana_image(self, prompt: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """Generate image using Google's image generation models via Nano Banana"""
        try:
            st.info("🍌 Nano Banana - Powered by Google's Image Generation")
            
            # Check if we have API access for real AI generation
            if hasattr(self, 'nano_banana_api_key') and self.nano_banana_api_key:
                st.info("🍌 Using dedicated Nano Banana API key...")
                st.warning("🔧 Direct Nano Banana API integration in development")
                st.info("🔄 Falling back to Google image models...")
                
            # Try Google image generation models
            if hasattr(self, 'nano_banana_models') and self.nano_banana_models:
                st.info("🍌 Using Google's image generation models...")
                
                # Create debug container for detailed information
                with st.expander("🔍 Nano Banana Debug Info", expanded=False):
                    # Show all available models in debug
                    st.write(f"📋 Available models ({len(self.nano_banana_models)}):")
                    for i, model_info in enumerate(self.nano_banana_models[:5]):  # Show first 5
                        model_name = model_info.name if hasattr(model_info, 'name') else str(model_info)
                        status = "🎯 **SELECTED**" if i == 0 else "   Available"
                        st.write(f"   {status}: {model_name}")
                    if len(self.nano_banana_models) > 5:
                        st.write(f"   ... and {len(self.nano_banana_models) - 5} more models")
                
                try:
                    import google.generativeai as genai
                    
                    # Prioritize models - FLASH FIRST for testing, then Gemini 3 Pro
                    model_priority = [
                        'gemini-2.5-flash-image',         # TEST FIRST: Fast and reliable
                        'gemini-2.5-flash-image-preview', # Flash variant
                        'gemini-3-pro-image-preview',     # NEXT: Latest gemini (switch to this later)
                        'imagen-4.0-ultra-generate-001',  # Ultra quality (if available)
                        'imagen-4.0-generate-001',        # High quality
                        'gemini-2.0-flash-exp-image-generation'  # Experimental fallback
                    ]
                    
                    # Find the best available model
                    selected_model = None
                    for priority_model in model_priority:
                        for model_info in self.nano_banana_models:
                            model_name = model_info.name if hasattr(model_info, 'name') else str(model_info)
                            if priority_model in model_name:
                                selected_model = model_info
                                break
                        if selected_model:
                            break
                    
                    # Fallback to first available if no priority match
                    if not selected_model:
                        selected_model = self.nano_banana_models[0]
                    
                    final_model_name = selected_model.name if hasattr(selected_model, 'name') else str(selected_model)
                    st.success(f"🎨 **SELECTED MODEL**: {final_model_name}")
                    
                    # Show model info and current testing strategy
                    if 'gemini-2.5-flash-image' in final_model_name:
                        st.info("⚡ **TESTING MODE**: Using Gemini 2.5 Flash - Fast and reliable for initial testing")
                        st.info("🔄 Will switch to Gemini 3 Pro once Flash is working reliably")
                    elif 'gemini-3-pro-image' in final_model_name:
                        st.info("🚀 Using Gemini 3 Pro Image - Latest Google multimodal AI (production mode)")
                    elif 'imagen-4.0-ultra' in final_model_name:
                        st.info("🌟 Using Imagen 4.0 Ultra - Highest quality Google image generation")
                    elif 'imagen-4.0' in final_model_name:
                        st.info("⭐ Using Imagen 4.0 - High quality Google image generation")
                    elif 'gemini-2.0-flash' in final_model_name:
                        st.info("🧪 Using Gemini 2.0 Flash - Experimental fallback")
                    
                    # Add note about current strategy
                    st.info("📝 **Strategy**: Testing with Flash first → Then switching to Gemini 3 Pro")
                    
                    model = genai.GenerativeModel(final_model_name)
                    
                    # Create a more detailed prompt for image generation
                    enhanced_prompt = f"Generate a high-quality advertisement image: {prompt}. Style: professional, modern, eye-catching design suitable for advertising."
                    
                    # === CAPTURE ALL API PARAMETERS ===
                    api_call_details = {
                        "api_provider": "Google Generative AI",
                        "model_name": final_model_name,
                        "method": "generate_content",
                        "generation_config": "default (no custom config for basic generation)",
                        "input_type": "text_prompt_only",
                        "prompt": enhanced_prompt,
                        "prompt_length": len(enhanced_prompt),
                        "prompt_word_count": len(enhanced_prompt.split()),
                        "original_prompt": prompt,
                        "original_prompt_length": len(prompt),
                        "enhancement_applied": True,
                        "target_size": {"width": size[0], "height": size[1]}
                    }
                    
                    with st.expander("📡 Google Gemini API Call Details", expanded=False):
                        st.json(api_call_details)
                        st.markdown("### Original Prompt")
                        st.text_area("User's prompt:", prompt, height=150, key="orig_prompt_nano")
                        st.markdown("### Enhanced Prompt (sent to API)")
                        st.text_area("Full prompt with enhancements:", enhanced_prompt, height=300, key="enh_prompt_nano")
                    
                    st.info(f"🔄 Generating image with prompt: {enhanced_prompt[:100]}...")
                    
                    # Try to generate image
                    try:
                        response = model.generate_content(enhanced_prompt)
                        st.success("✅ Image generation request completed")
                    except Exception as gen_error:
                        st.error(f"❌ Generation failed: {str(gen_error)}")
                        return None
                    
                    # Move all debugging into the debug container
                    with st.expander("🔍 Response Analysis", expanded=False):
                        # Debug: Show response structure
                        st.write(f"📥 Response type: {type(response)}")
                        
                        # Check for any text response that might indicate an error
                        try:
                            if hasattr(response, 'text') and response.text:
                                st.write(f"💬 Text response: {response.text[:200]}...")
                                if "cannot generate" in response.text.lower() or "unable to create" in response.text.lower():
                                    st.error("❌ Model explicitly refused to generate image")
                        except Exception as text_error:
                            st.write(f"⚠️ Could not access text response: {str(text_error)}")
                        
                        # Check if there are any parts at all
                        if not hasattr(response, 'parts') or not response.parts:
                            st.error("❌ No parts in response - model may not support image generation")
                            st.info("💡 Try a different model or prompt approach")
                        else:
                            st.write(f"📝 Response has {len(response.parts)} parts")
                            
                            # Check each part for image data - SAFELY
                            for i, part in enumerate(response.parts):
                                try:
                                    st.write(f"📋 Part {i+1}: {type(part)}")
                                    
                                    # Safely check for inline_data without converting to text
                                    if hasattr(part, 'inline_data'):
                                        try:
                                            inline = part.inline_data
                                            mime_type = getattr(inline, 'mime_type', 'unknown')
                                            
                                            # Safely get data length without converting to text
                                            data_length = 0
                                            if hasattr(inline, 'data'):
                                                try:
                                                    data_length = len(inline.data) if inline.data else 0
                                                except:
                                                    data_length = "unknown"
                                            
                                            st.write(f"   📎 Inline data: {mime_type}, {data_length} bytes")
                                        except Exception as inline_error:
                                            st.write(f"   📎 Has inline_data but error accessing: {str(inline_error)}")
                                    
                                    elif hasattr(part, 'text'):
                                        try:
                                            st.write(f"   💬 Text: {part.text[:100]}...")
                                        except Exception as text_error:
                                            st.write(f"   💬 Has text but error accessing: {str(text_error)}")
                                    else:
                                        st.write(f"   ❓ Unknown part type")
                                        
                                except Exception as part_debug_error:
                                    st.write(f"   ⚠️ Error debugging part {i+1}: {str(part_debug_error)}")
                    
                    # Process image data (simplified main flow)
                    if hasattr(response, 'parts') and response.parts:
                        for part in response.parts:
                            # Handle Google's response format properly
                            try:
                                if hasattr(part, 'inline_data'):
                                    inline_data = part.inline_data
                                    
                                    # Check if data exists
                                    if not hasattr(inline_data, 'data') or not inline_data.data:
                                        st.warning("⚠️ inline_data exists but no data property found")
                                        continue
                                    
                                    data_length = len(inline_data.data)
                                    mime_type = getattr(inline_data, 'mime_type', 'unknown')
                                    
                                    st.info(f"📄 Found {mime_type} data: {data_length} bytes")
                                    
                                    if data_length == 0:
                                        st.warning("⚠️ Received empty image data from model")
                                        continue
                                    
                                    if data_length < 100:
                                        st.warning(f"⚠️ Image data too small ({data_length} bytes)")
                                        continue
                                    
                                    # Process the image data
                                    try:
                                        import base64
                                        
                                        # Get the raw data
                                        raw_data = inline_data.data
                                        
                                        # Try different approaches to decode
                                        if isinstance(raw_data, str):
                                            # It's base64 encoded string
                                            image_bytes = base64.b64decode(raw_data)
                                        elif isinstance(raw_data, bytes):
                                            # It's already bytes
                                            image_bytes = raw_data
                                        else:
                                            # Try to convert to bytes
                                            image_bytes = bytes(raw_data)
                                        
                                        if len(image_bytes) < 100:
                                            st.warning("⚠️ Decoded image data too small")
                                            continue
                                        
                                        # Create PIL Image
                                        image = Image.open(io.BytesIO(image_bytes))
                                        
                                        # Resize if needed
                                        if image.size != size:
                                            st.info(f"🔄 Resizing from {image.size} to {size}")
                                            image = image.resize(size, Image.Resampling.LANCZOS)
                                        
                                        st.success(f"✅ Nano Banana image generated: {image.size[0]}x{image.size[1]}")
                                        return image
                                        
                                    except Exception as decode_error:
                                        st.error(f"❌ Image decoding failed: {str(decode_error)}")
                                        with st.expander("🔍 Decode Debug", expanded=False):
                                            st.write(f"Raw data type: {type(raw_data)}")
                                            st.write(f"Raw data length: {len(raw_data) if hasattr(raw_data, '__len__') else 'No length'}")
                                            if isinstance(raw_data, (str, bytes)):
                                                st.write(f"First 50 chars: {str(raw_data)[:50]}")
                                        continue
                                        
                            except Exception as part_error:
                                st.error(f"❌ Error processing part: {str(part_error)}")
                                with st.expander("🔍 Part Error Debug", expanded=False):
                                    st.write(f"Part type: {type(part)}")
                                    st.write(f"Part attributes: {dir(part)}")
                                    st.write(f"Has inline_data: {hasattr(part, 'inline_data')}")
                                continue
                    
                    st.error("❌ No valid image data found in any response part")
                    return None
                    
                    if hasattr(response, 'parts') and response.parts:
                        # Check if we got image data
                        for part in response.parts:
                            if hasattr(part, 'inline_data'):
                                st.success("✅ Nano Banana image generated via Google!")
                                st.info("🔄 Processing image data...")
                                
                                try:
                                    # Extract and process image data
                                    image_data = part.inline_data.data
                                    mime_type = part.inline_data.mime_type
                                    
                                    st.info(f"📄 Received {mime_type} image data")
                                    st.info(f"🔢 Data length: {len(image_data)} characters")
                                    
                                    # Convert base64 to PIL Image with better error handling
                                    import base64
                                    try:
                                        # Try direct base64 decode
                                        image_bytes = base64.b64decode(image_data)
                                        st.info(f"📦 Decoded to {len(image_bytes)} bytes")
                                        
                                        # Verify it's actual image data
                                        if len(image_bytes) < 100:
                                            raise ValueError("Image data too small to be valid")
                                        
                                        # Try to open as image
                                        image = Image.open(io.BytesIO(image_bytes))
                                        
                                    except Exception as decode_error:
                                        st.warning(f"⚠️ Standard decode failed: {str(decode_error)}")
                                        st.info("🔄 Trying alternative processing...")
                                        
                                        # Maybe the data is already bytes, not base64
                                        try:
                                            if isinstance(image_data, bytes):
                                                image = Image.open(io.BytesIO(image_data))
                                            else:
                                                # Try without base64 decode
                                                image_bytes = image_data.encode() if isinstance(image_data, str) else image_data
                                                image = Image.open(io.BytesIO(image_bytes))
                                        except Exception as alt_error:
                                            st.error(f"❌ Alternative processing failed: {str(alt_error)}")
                                            st.info("🔍 Debugging image data format...")
                                            st.write(f"Data type: {type(image_data)}")
                                            st.write(f"First 100 chars: {str(image_data)[:100]}")
                                            return None
                                    
                                    st.success(f"✅ Image processed: {image.size[0]}x{image.size[1]} pixels")
                                    
                                    # Resize to exact dimensions if needed
                                    if image.size != size:
                                        st.info(f"🔄 Resizing from {image.size} to {size}")
                                        image = image.resize(size, Image.Resampling.LANCZOS)
                                    
                                    return image
                                    
                                except Exception as processing_error:
                                    st.error(f"❌ Image processing failed: {str(processing_error)}")
                                    st.info("🔍 Debug info:")
                                    if 'image_data' in locals():
                                        st.write(f"   Data type: {type(image_data)}")
                                        st.write(f"   Data length: {len(str(image_data))}")
                                        st.write(f"   First 50 chars: {str(image_data)[:50]}")
                                    return None
                        
                        # No image data found, check for text response
                        if hasattr(response, 'text') or any(hasattr(part, 'text') for part in response.parts):
                            st.warning("💭 Model returned text instead of image")
                            st.info("💡 This model may not support image generation")
                        else:
                            st.warning("❓ Unknown response format")
                        
                        st.error("❌ No image data received from model")
                        return None
                        
                except Exception as api_error:
                    st.warning(f"🍌 Google API failed: {str(api_error)[:100]}...")
                    st.error("❌ Image generation failed")
                    return None
                    
            elif hasattr(self, 'nano_banana_model_names') and self.nano_banana_model_names:
                st.info("🍌 Using known Google image models...")
                try:
                    import google.generativeai as genai
                    
                    # Try each available model until one works
                    for model_name in self.nano_banana_model_names:
                        st.info(f"🎨 Trying model: {model_name}")
                        
                        try:
                            model = genai.GenerativeModel(model_name)
                            
                            # Enhanced prompt for image generation
                            enhanced_prompt = f"Create a professional advertisement image: {prompt}. High quality, modern design, suitable for marketing purposes."
                            
                            response = model.generate_content(enhanced_prompt)
                            
                            # Check for image data in response
                            if hasattr(response, 'parts') and response.parts:
                                for part in response.parts:
                                    if hasattr(part, 'inline_data'):
                                        st.success(f"✅ Image generated with {model_name}!")
                                        
                                        # Process the image data
                                        try:
                                            import base64
                                            image_data = part.inline_data.data
                                            mime_type = getattr(part.inline_data, 'mime_type', 'unknown')
                                            
                                            st.info(f"📄 Processing {mime_type} from {model_name}")
                                            
                                            # Try different decoding approaches
                                            try:
                                                # Standard base64 decode
                                                image_bytes = base64.b64decode(image_data)
                                                image = Image.open(io.BytesIO(image_bytes))
                                            except Exception:
                                                # Try direct bytes
                                                if isinstance(image_data, bytes):
                                                    image = Image.open(io.BytesIO(image_data))
                                                else:
                                                    # Try as raw string
                                                    image_bytes = image_data.encode() if isinstance(image_data, str) else image_data
                                                    image = Image.open(io.BytesIO(image_bytes))
                                            
                                            # Resize if needed
                                            if image.size != size:
                                                image = image.resize(size, Image.Resampling.LANCZOS)
                                            
                                            st.success(f"✅ {model_name} generated {image.size[0]}x{image.size[1]} image")
                                            return image
                                            
                                        except Exception as proc_error:
                                            st.warning(f"Processing failed for {model_name}: {str(proc_error)}")
                                            st.info(f"Debug: data type {type(image_data)}, length {len(str(image_data))}")
                                            continue
                            
                            st.info(f"❌ {model_name} didn't return image data")
                            
                        except Exception as model_error:
                            st.info(f"❌ {model_name} failed: {str(model_error)[:50]}...")
                            continue
                    
                    st.error("❌ None of the available models could generate images")
                    return None
                    
                except Exception as e:
                    st.error(f"❌ Error trying known models: {str(e)}")
                    return None
                    
            elif hasattr(self, 'google_api_key') and self.google_api_key:
                st.warning("⚠️ Google API key available but no image models found")
                st.error("❌ Cannot generate images without image-capable models")
                return None
            else:
                st.error("❌ No API configuration for Nano Banana")
                st.info("💡 Add GOOGLE_API_KEY to enable Google image generation")
                return None
                
        except Exception as e:
            st.error(f"❌ Nano Banana generation failed: {str(e)}")
            return None
    

    

    
    def convert_to_dalle_size(self, size: Tuple[int, int]) -> str:
        """Convert custom size to DALL-E supported format"""
        width, height = size
        
        # DALL-E 3 supported sizes
        dalle3_sizes = {
            (1024, 1024): "1024x1024",
            (1024, 1792): "1024x1792", 
            (1792, 1024): "1792x1024"
        }
        
        # DALL-E 2 supported sizes  
        dalle2_sizes = {
            (256, 256): "256x256",
            (512, 512): "512x512",
            (1024, 1024): "1024x1024"
        }
        
        # Find closest supported size
        if self.model_name == "DALL-E 3":
            return self.find_closest_size(size, dalle3_sizes)
        else:
            return self.find_closest_size(size, dalle2_sizes)
    
    def find_closest_size(self, target_size: Tuple[int, int], supported_sizes: dict) -> str:
        """Find the closest supported size"""
        target_ratio = target_size[0] / target_size[1]
        best_match = None
        best_diff = float('inf')
        
        for (w, h), size_str in supported_sizes.items():
            ratio = w / h
            diff = abs(ratio - target_ratio)
            if diff < best_diff:
                best_diff = diff
                best_match = size_str
        
        return best_match or "1024x1024"

class APIKeyManager:
    """Manages API keys for different services"""
    
    @staticmethod
    def get_openai_key():
        """Get OpenAI API key from environment variables only"""
        return os.getenv("OPENAI_API_KEY")
    
    @staticmethod
    def get_huggingface_key():
        """Get Hugging Face API key"""
        return os.getenv("HUGGINGFACE_API_KEY")
    
    @staticmethod
    def get_google_key():
        """Get Google API key for Gemini"""
        return os.getenv("GOOGLE_API_KEY")
    
    # @staticmethod
    # def get_nano_banana_key():
    #     """Get Nano Banana API key (placeholder)"""
    #     return os.getenv("NANO_BANANA_API_KEY")

# Model configurations
MODEL_CONFIGS = {
    "DALL-E 3": {
        "provider": "OpenAI",
        "max_size": (1792, 1024),
        "supported_ratios": ["1:1", "16:9", "9:16"],
        "quality": "HD",
        "requires_key": True
    },
    "DALL-E 2": {
        "provider": "OpenAI", 
        "max_size": (1024, 1024),
        "supported_ratios": ["1:1"],
        "quality": "Standard",
        "requires_key": True
    },
    "Stable Diffusion": {
        "provider": "Hugging Face",
        "max_size": (1024, 1024),
        "supported_ratios": ["1:1", "4:3", "3:4", "16:9"],
        "quality": "High",
        "requires_key": False
    },
    "Google Imagen": {
        "provider": "Google",
        "max_size": (1024, 1024),
        "supported_ratios": ["1:1", "4:3", "3:4", "16:9"],
        "quality": "High",
        "requires_key": True
    },
    "Nano Banana": {
        "provider": "Google (Image Generation)",
        "max_size": (2048, 2048),
        "supported_ratios": ["1:1", "4:3", "3:4", "16:9", "21:9"],
        "quality": "High (Google AI Studio models)",
        "requires_key": True,
        "description": "Google's image generation models with Nano Banana branding",
        "api_key_source": "GOOGLE_API_KEY"
    },
    "Nano Banana Pro": {
        "provider": "Google (Advanced Image Generation)",
        "max_size": (4096, 4096),
        "supported_ratios": ["1:1", "4:3", "3:4", "16:9", "21:9"],
        "quality": "Ultra (4K)",
        "requires_key": True,
        "description": "Google's Nano Banana Pro with advanced features: multi-image reference, search grounding, text rendering",
        "api_key_source": "GOOGLE_API_KEY",
        "features": ["14 reference images", "Search grounding", "Text rendering", "4K output", "Enterprise-grade"]
    },
    "Midjourney (Placeholder)": {
        "provider": "Midjourney",
        "max_size": (1024, 1024),
        "supported_ratios": ["1:1", "4:3", "3:4", "16:9"],
        "quality": "Ultra",
        "requires_key": True
    }
}

# Nano Banana Pro Advanced Features Implementation
class NanoBananaProFeatures:
    """Advanced features for Nano Banana Pro (Gemini 3 Pro Image)"""
    
    @staticmethod
    def generate_with_references(generator, prompt, size=(1024, 1024), reference_images=None, 
                               use_search_grounding=False, text_rendering_mode=False):
        """Generate with Nano Banana Pro advanced features"""
        try:
            if not hasattr(generator, 'google_api_key'):
                st.warning("⚠️ Google API not configured for Nano Banana Pro features")
                return None
            
            import google.generativeai as genai
            genai.configure(api_key=generator.google_api_key)
            
            # Use Nano Banana Pro model
            model_name = 'gemini-3-pro-image-preview'
            model = genai.GenerativeModel(model_name)
            
            # Enhanced prompt for Nano Banana Pro capabilities
            enhanced_prompt = NanoBananaProFeatures._build_enhanced_prompt(
                prompt, use_search_grounding, text_rendering_mode
            )
            
            st.info(f"🚀 Nano Banana Pro: Search={use_search_grounding}, Text={text_rendering_mode}")
            
            # Prepare input for multi-modal generation
            generation_input = [enhanced_prompt]
            
            # Add reference images (up to 14 for Nano Banana Pro)
            successful_references = 0
            if reference_images:
                for i, ref_img in enumerate(reference_images[:14]):
                    try:
                        # Add debug info
                        st.write(f"🔍 Processing reference image {i+1}: {type(ref_img)}")
                        
                        # Handle different image input types
                        if hasattr(ref_img, 'read') and hasattr(ref_img, 'seek'):
                            # Streamlit UploadedFile - convert to PIL Image
                            try:
                                ref_img.seek(0)
                                pil_image = Image.open(ref_img)
                                generation_input.append(pil_image)
                                successful_references += 1
                                st.info(f"📎 Reference image {i+1}/14 added (UploadedFile converted)")
                            except Exception as upload_error:
                                st.warning(f"⚠️ Failed to process UploadedFile {i+1}: {upload_error}")
                                continue
                        elif isinstance(ref_img, Image.Image):
                            # Already PIL Image
                            generation_input.append(ref_img)
                            successful_references += 1
                            st.info(f"📎 Reference image {i+1}/14 added (PIL Image)")
                        elif hasattr(ref_img, 'getvalue'):
                            # BytesIO object - get the bytes directly
                            try:
                                image_bytes = ref_img.getvalue()
                                if isinstance(image_bytes, bytes) and len(image_bytes) > 0:
                                    image_buffer = io.BytesIO(image_bytes)
                                    pil_image = Image.open(image_buffer)
                                    generation_input.append(pil_image)
                                    successful_references += 1
                                    st.info(f"📎 Reference image {i+1}/14 added (BytesIO converted)")
                                else:
                                    st.warning(f"⚠️ Reference image {i+1}: Empty or invalid BytesIO data")
                            except Exception as convert_error:
                                st.warning(f"⚠️ Failed to convert BytesIO reference image {i+1}: {convert_error}")
                        else:
                            # Try direct PIL Image.open with better error handling
                            try:
                                # Check if it's a file-like object or path
                                if hasattr(ref_img, '__fspath__') or isinstance(ref_img, (str, bytes)):
                                    pil_image = Image.open(ref_img)
                                    generation_input.append(pil_image)
                                    successful_references += 1
                                    st.info(f"📎 Reference image {i+1}/14 added (Direct conversion)")
                                else:
                                    st.warning(f"⚠️ Reference image {i+1}: Unsupported object type {type(ref_img)}")
                            except Exception as convert_error:
                                st.warning(f"⚠️ Failed to convert reference image {i+1}: {convert_error}")
                                st.error(f"🔍 Debug: Object type={type(ref_img)}, hasattr(read)={hasattr(ref_img, 'read')}")
                            except Exception as convert_error:
                                st.warning(f"⚠️ Failed to convert reference image {i+1}: {convert_error}")
                    except Exception as img_error:
                        st.warning(f"⚠️ Error processing reference image {i+1}: {img_error}")
                        continue
                
                if successful_references == 0 and reference_images:
                    st.warning("⚠️ No reference images could be processed. Continuing without references.")
            
            # Generate with advanced configuration
            generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                temperature=0.7,
            )
            
            # === CAPTURE ALL API PARAMETERS FOR NANO BANANA PRO ===
            api_call_details = {
                "api_provider": "Google Generative AI (Nano Banana Pro)",
                "model_name": model_name,
                "method": "generate_content",
                "generation_config": {
                    "candidate_count": 1,
                    "temperature": 0.7
                },
                "input_components": {
                    "text_prompt": enhanced_prompt,
                    "reference_images_count": successful_references,
                    "total_inputs": len(generation_input)
                },
                "advanced_features": {
                    "search_grounding": use_search_grounding,
                    "text_rendering_mode": text_rendering_mode
                },
                "prompt_details": {
                    "base_prompt": prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "prompt_length": len(enhanced_prompt),
                    "prompt_word_count": len(enhanced_prompt.split())
                },
                "target_size": {"width": size[0], "height": size[1]}
            }
            
            with st.expander("📡 Nano Banana Pro API Call Details", expanded=False):
                st.json(api_call_details)
                st.markdown("### Base Prompt (from app)")
                st.text_area("Original prompt:", prompt, height=200, key="nbp_base")
                st.markdown("### Enhanced Prompt (with Pro features)")
                st.text_area("Full prompt sent to API:", enhanced_prompt, height=400, key="nbp_enhanced")
                if reference_images:
                    st.markdown(f"### Reference Images: {successful_references} successfully processed")
            
            with st.status("🎨 Generating with Nano Banana Pro...", expanded=True) as status:
                st.write("🔍 Enhanced prompt prepared")
                if reference_images:
                    st.write(f"📎 Using {len(reference_images)} reference images")
                st.write(f"🔍 Search grounding: {'Enabled' if use_search_grounding else 'Disabled'}")
                st.write(f"✍️ Text rendering: {'Enabled' if text_rendering_mode else 'Disabled'}")
                
                try:
                    response = model.generate_content(
                        generation_input,
                        generation_config=generation_config
                    )
                    st.write("✅ Content generation completed")
                except Exception as gen_error:
                    st.error(f"❌ Generation failed: {gen_error}")
                    status.update(label="❌ Generation error", state="error")
                    return None
                
                # Process response
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                try:
                                    import base64
                                    # Get the image data properly
                                    if hasattr(part.inline_data, 'data'):
                                        image_data = part.inline_data.data
                                        
                                        # Handle different data formats
                                        if isinstance(image_data, str):
                                            # Base64 string - decode it
                                            decoded_data = base64.b64decode(image_data)
                                        elif isinstance(image_data, bytes):
                                            # Already bytes
                                            decoded_data = image_data
                                        else:
                                            # Try to get bytes from object
                                            decoded_data = bytes(image_data)
                                        
                                        # Create BytesIO and open image safely
                                        image_buffer = io.BytesIO(decoded_data)
                                        image = Image.open(image_buffer)
                                        
                                        # Resize if needed
                                        if image.size != size:
                                            image = image.resize(size, Image.Resampling.LANCZOS)
                                        
                                        status.update(label="✅ Nano Banana Pro complete!", state="complete")
                                        return image
                                except Exception as e:
                                    st.error(f"❌ Error processing image: {e}")
                                    st.error(f"🔍 Debug info - Data type: {type(part.inline_data.data)}")
                                    if hasattr(part.inline_data, 'data'):
                                        st.error(f"🔍 Debug info - Data length: {len(part.inline_data.data) if hasattr(part.inline_data.data, '__len__') else 'Unknown'}")
                
                status.update(label="❌ No image generated", state="error")
            
            return None
            
        except Exception as e:
            st.error(f"❌ Nano Banana Pro failed: {e}")
            return None
    
    @staticmethod
    def _build_enhanced_prompt(base_prompt, use_search_grounding=False, text_rendering_mode=False):
        """Build enhanced prompt with Nano Banana Pro capabilities"""
        return PromptBuilder.build_nano_banana_pro_prompt(
            base_prompt, use_search_grounding, text_rendering_mode
        )
    
    @staticmethod
    def detect_advanced_features(prompt):
        """Auto-detect if advanced features should be enabled"""
        return PromptBuilder.detect_advanced_features(prompt)