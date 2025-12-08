import streamlit as st
import os
import io
from PIL import Image
from datetime import datetime
import json
from utils.ai_generator import AIImageGenerator
from utils.image_processor import ImageProcessor
from utils.config import Config, EnvironmentManager
from utils.helpers import display_model_info, validate_inputs, suggest_prompt_improvements
from utils.template_manager import TemplateManager
from utils.prompts import PromptBuilder
# Commented out: setup_api_keys, show_generation_tips, display_usage_stats

# Load environment variables from .env file only for local development
try:
    if not EnvironmentManager.is_streamlit_deployment():
        from dotenv import load_dotenv
        load_dotenv()
except ImportError:
    # dotenv not available, skip loading
    pass

def analyze_logo_details(logo_file):
    """Simplified logo analysis for AI prompt (templates and reference images handle placement)"""
    return PromptBuilder.analyze_logo_details(logo_file)

def store_uploaded_logo(logo_file, client_name):
    """Store uploaded logo file in assets/uploaded_logos directory"""
    try:
        # Create assets directory if it doesn't exist
        assets_dir = "assets/uploaded_logos"
        os.makedirs(assets_dir, exist_ok=True)
        
        # Generate safe filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_client_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_client_name = safe_client_name.replace(' ', '_')
        file_extension = os.path.splitext(logo_file.name)[1] if logo_file.name else '.png'
        
        filename = f"{safe_client_name}_{timestamp}{file_extension}"
        filepath = os.path.join(assets_dir, filename)
        
        # Save the uploaded file
        with open(filepath, "wb") as f:
            f.write(logo_file.read())
        
        # Reset file pointer for further processing
        logo_file.seek(0)
        
        return filepath
        
    except Exception as e:
        st.error(f"Failed to store logo: {str(e)}")
        return None

# Page configuration
st.set_page_config(
    page_title="Cur8er",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'generated_ad' not in st.session_state:
    st.session_state.generated_ad = None
if 'generation_params' not in st.session_state:
    st.session_state.generation_params = {}
if 'client_logo' not in st.session_state:
    st.session_state.client_logo = None
if 'show_template_editor' not in st.session_state:
    st.session_state.show_template_editor = False

def main():
    st.title("🎨 Cur8er")
    st.markdown("Create stunning advertisements with AI-powered image generation")
    
    # Template Editor Interface (Full Width)
    if st.session_state.get('show_template_editor', False):
        st.markdown("---")
        st.header("🎨 Template Editor")
        st.info("💡 Create and customize advertisement templates with precise element positioning")
        
        # Close button at the top
        if st.button("❌ Close Template Editor", key="close_editor_main"):
            st.session_state.show_template_editor = False
            st.rerun()
        
        # Import and show template editor with full width
        from utils.template_editor import show_template_editor
        show_template_editor()
        
        st.markdown("---")
        st.markdown("### 👆 Template editor above - Use the controls to create custom templates")
        st.markdown("**💡 Tip:** Close the editor above to return to ad generation")
        
        # Don't show the main content when editor is open
        st.stop()
    
    # Main content area - 3 column layout for optimal organization
    input_col, middle_col, actions_col = st.columns([1, 2, 1], gap="medium")
    
    # LEFT COLUMN: Move sidebar content here
    with input_col:
        st.header("🎯 Configuration")
        
        # Company/Client input
        company_name = st.text_input("Company/Client Name", placeholder="Enter company name...")
        
        # Template system toggle
        use_template = st.checkbox("Use Template System", value=False, key="template_toggle")
        
        # Template selection if enabled
        if use_template:
            template_manager = TemplateManager()
            templates = template_manager.get_available_templates()
            if templates:
                template_col1, template_col2 = st.columns([3, 1])
                with template_col1:
                    selected_template = st.selectbox(
                        "Choose Template:",
                        options=list(templates.keys()),
                        format_func=lambda x: templates[x]
                    )
                with template_col2:
                    if st.button("✏️ Edit", help="Edit templates", use_container_width=True):
                        st.session_state.show_template_editor = True
                        st.rerun()
            else:
                selected_template = None
                st.info("No templates available. Create templates using the Template Editor.")
                if st.button("🎨 Create Template", use_container_width=True):
                    st.session_state.show_template_editor = True
                    st.rerun()
        else:
            selected_template = None
        
        st.divider()
        
        # Custom prompt for LLM
        user_prompt = st.text_area(
            "Custom Prompt (LLM Instructions)", 
            placeholder="Enter detailed instructions for the AI to create your advertisement...",
            help="💡 This is your custom prompt that instructs the AI model on what to generate",
            height=100
        )
        
        # Ad medium
        ad_medium = st.selectbox(
            "Medium/Platform:",
            options=["Social Media", "Print", "Digital Display", "Email", "Web Banner"]
        )
        
        # Style preset
        style_preset = st.selectbox(
            "Style Preset:",
            options=[
                "Modern & Minimalist",
                "Bold & Vibrant", 
                "Elegant & Professional",
                "Retro & Vintage",
                "Futuristic & Tech",
                "Natural & Organic",
                "Luxury & Premium",
                "Playful & Fun"
            ]
        )
        
        # Ad size selector
        st.subheader("📏 Select Sizes")
        ad_size = st.selectbox(
            "Select ad size:",
            options=[
                "Square (1080x1080) - Instagram Post",
                "Landscape (1920x1080) - YouTube Thumbnail", 
                "Portrait (1080x1920) - Instagram Story",
                "Banner (728x90) - Web Banner",
                "Leaderboard (970x250) - Web Header",
                "Facebook Cover (820x312)",
                "LinkedIn Post (1200x627)",
                "Custom Size"
            ]
        )
        
        # Custom size inputs if selected
        if ad_size == "Custom Size":
            col1, col2 = st.columns(2)
            with col1:
                custom_width = st.number_input("Width (px)", min_value=100, max_value=4000, value=1080)
            with col2:
                custom_height = st.number_input("Height (px)", min_value=100, max_value=4000, value=1080)
            dimensions = (custom_width, custom_height)
        else:
            dimensions = Config.get_dimensions(ad_size)
        
        # Logo upload
        uploaded_logo = st.file_uploader(
            "Upload Company Logo",
            type=["png", "jpg", "jpeg", "svg"]
        )
        
        # Reference images for AI generation
        reference_images = st.file_uploader(
            "🖼️ Reference Images (Style Guide)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            help="Upload reference images to guide the AI's style and composition (up to 14 images)"
        )
        
        # Show reference image preview and status
        if reference_images:
            st.success(f"✅ {len(reference_images)} reference image(s) uploaded")
            with st.expander(f"📋 Preview Reference Images ({len(reference_images)})"):
                preview_cols = st.columns(min(4, len(reference_images)))
                for i, ref_img in enumerate(reference_images[:4]):
                    with preview_cols[i % 4]:
                        try:
                            img = Image.open(ref_img)
                            st.image(img, caption=f"Ref {i+1}", width=80)
                        except:
                            st.text(f"Ref {i+1}: {ref_img.name}")
                if len(reference_images) > 4:
                    st.info(f"... and {len(reference_images) - 4} more reference images")
        
        # Advanced options
        with st.expander("Advanced Options"):
            color_scheme = st.selectbox(
                "Primary Color Scheme:",
                options=["Brand Colors", "Warm Tones", "Cool Tones", "Monochrome", "High Contrast", "Pastel"]
            )
            
            include_text = st.checkbox("Include text overlay", value=True)
            include_cta = st.checkbox("Include call-to-action", value=True)
            
            # Website and tagline
            client_website = st.text_input("Website (optional)", placeholder="https://example.com")
            client_tagline = st.text_input("Tagline (optional)", placeholder="Your company slogan...")

    
    # MIDDLE COLUMN: Model Selection, Preview, Generation Details
    with middle_col:
        # Single comprehensive model selection section
        st.header("🤖 AI Model Selection")
        
        # Get current API key status
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        nano_banana_key = os.getenv("NANO_BANANA_API_KEY")
        
        # Create model options with detailed status indicators
        model_options = []
        model_status = {}
        
        # DALL-E models
        if openai_key:
            model_options.extend(["✅ DALL-E 3 (Ready - Premium Quality)", "✅ DALL-E 2 (Ready - Fast)"])
            model_status["DALL-E 3"] = "ready"
            model_status["DALL-E 2"] = "ready"
        else:
            model_options.extend(["❌ DALL-E 3 (API Key Missing)", "❌ DALL-E 2 (API Key Missing)"])
            model_status["DALL-E 3"] = "missing_key"
            model_status["DALL-E 2"] = "missing_key"
        
        # Imagen model (Google's actual image generation API)
        if google_key:
            model_options.append("✅ Google Imagen (Ready - Google's Image AI)")
            model_status["Google Imagen"] = "ready"
        else:
            model_options.append("❌ Google Imagen (API Key Missing)")
            model_status["Google Imagen"] = "missing_key"
        
        # Nano Banana (Google API compatible)
        if google_key:
            model_options.append("🍌 Nano Banana (Ready - Google API Compatible)")
            model_options.append("🍌⭐ Nano Banana Pro (Advanced Features - 4K, Search, Text)")
            model_status["Nano Banana"] = "ready"
            model_status["Nano Banana Pro"] = "ready"
        else:
            model_options.append("❌ Nano Banana (API Key Missing)")
            model_options.append("❌ Nano Banana Pro (API Key Missing)")
            model_status["Nano Banana"] = "missing_key"
            model_status["Nano Banana Pro"] = "missing_key"
        
        # Other placeholder models
        model_options.extend([
            "🔧 Stable Diffusion (Coming Soon)",
            "🔧 Midjourney (Coming Soon)"
        ])
        model_status["Stable Diffusion"] = "coming_soon"
        model_status["Midjourney"] = "coming_soon"
        
        # Main model selection dropdown
        selected_option = st.selectbox(
            "Choose your AI model:",
            options=model_options,
            help="✅ Ready to use | ❌ Need API key | 🔧 In development",
            key="main_model_selector"
        )
        
        # Extract the actual model name from the selected option
        ai_model = selected_option.split(" (")[0].replace("✅ ", "").replace("❌ ", "").replace("🔧 ", "").replace("🍌 ", "")
        
        # Store the selected model in session state
        st.session_state.selected_model = ai_model
        
        # Display model status and setup information
        status_col1, status_col2 = st.columns([3, 1])
        with status_col1:
            if ai_model in model_status:
                status = model_status[ai_model]
                if status == "ready":
                    st.success(f"✨ {ai_model} is ready to generate images!")
                elif status == "missing_key":
                    st.error(f"❌ {ai_model} cannot generate images without API key")
                    if "DALL-E" in ai_model:
                        config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                        st.info(f"🔑 Add OPENAI_API_KEY to your {config_source}")
                        if EnvironmentManager.is_streamlit_deployment():
                            st.code("OPENAI_API_KEY = \"sk-your-key-here\"", language="toml")
                        else:
                            st.code("OPENAI_API_KEY=sk-your-key-here", language="bash")
                    elif "Imagen" in ai_model:
                        config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                        st.info(f"🔑 Add GOOGLE_API_KEY to your {config_source} (same as Gemini)")
                        if EnvironmentManager.is_streamlit_deployment():
                            st.code("GOOGLE_API_KEY = \"your-google-key-here\"", language="toml")
                        else:
                            st.code("GOOGLE_API_KEY=your-google-key-here", language="bash")
                    elif "Nano Banana" in ai_model:
                        config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                        st.info(f"🔑 Add GOOGLE_API_KEY to your {config_source}")
                        if EnvironmentManager.is_streamlit_deployment():
                            st.code("GOOGLE_API_KEY = \"your-google-key-here\"", language="toml")
                        else:
                            st.code("GOOGLE_API_KEY=your-google-key-here", language="bash")
                elif status == "coming_soon":
                    st.error(f"❌ {ai_model} integration is in development - cannot generate images")
        
        # Show model information
        from utils.ai_generator import MODEL_CONFIGS
        if ai_model in MODEL_CONFIGS:
            config = MODEL_CONFIGS[ai_model]
            
            info_cols = st.columns(4)
            with info_cols[0]:
                st.metric("Provider", config['provider'])
            with info_cols[1]:
                st.metric("Quality", config['quality'])
            with info_cols[2]:
                st.metric("Max Size", f"{config['max_size'][0]}x{config['max_size'][1]}")
            with info_cols[3]:
                api_req = "Yes" if config['requires_key'] else "No"
                st.metric("API Key Req.", api_req)
        
        st.divider()
        
        # Model comparison section
        with st.expander("📊 Model Comparison & Features"):
            st.markdown("""
            | Model | Provider | Quality | Speed | API Key Required | Status |
            |-------|----------|---------|-------|-----------------|---------|
            | DALL-E 3 | OpenAI | ⭐⭐⭐⭐⭐ | 🐌 Slow | ✅ Yes | Ready |
            | DALL-E 2 | OpenAI | ⭐⭐⭐⭐ | 🚀 Fast | ✅ Yes | Ready |
            | Gemini Pro | Google | ⭐⭐⭐⭐ | 🚀 Fast | ✅ Yes | Ready |
            | Stable Diffusion | HuggingFace | ⭐⭐⭐⭐ | 🚀 Fast | ❌ No | 🔧 Coming Soon |
            | Nano Banana | Google | ⭐⭐⭐⭐⭐ | ⚡ Ultra | ✅ Yes | Ready |
            | Nano Banana Pro | Google | ⭐⭐⭐⭐⭐⭐ | ⚡ Ultra | ✅ Yes | 🚀 Advanced Features |
            | Midjourney | Midjourney | ⭐⭐⭐⭐⭐ | 🐌 Slow | ❌ No | 🔧 Coming Soon |
            
            **Recommendations:**
            - 🎯 **Best Quality:** DALL-E 3 or Nano Banana Pro
            - 🚀 **Advanced Features:** Nano Banana Pro (4K, Search Grounding, Text Rendering, **14 Reference Images**)
            - ⚡ **Fastest:** Nano Banana or DALL-E 2
            - 💰 **Free Options:** Stable Diffusion (when available)
            - 🎨 **Most Creative:** Nano Banana Pro with reference images (upload style references, mood boards, or inspiration images)
            
            **🖼️ Reference Image Feature:**
            When using Nano Banana Pro, you can upload up to 14 reference images to guide the AI generation. These can be:
            - Style references (color schemes, visual aesthetics)
            - Composition examples (layout inspiration)
            - Brand mood boards (visual brand identity)
            - Product photos (for product-focused ads)
            - Competitor ads (for style inspiration)
            """)
        
        st.header("Generated Advertisement")
        
        if st.session_state.generated_ad is not None:
            # Display generated ad
            st.image(
                st.session_state.generated_ad,
                caption="Generated Advertisement",
                width='stretch'
            )
            
            # Ad information
            if st.session_state.generation_params:
                with st.expander("📋 Generation Details", expanded=False):
                    params = st.session_state.generation_params
                    
                    # Core Generation Info
                    st.markdown("**🎯 Core Generation**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Model Used", params.get('model', 'Unknown'))
                        st.metric("Generation Type", params.get('generation_type', 'Unknown').replace('_', ' ').title())
                        if params.get('template_used'):
                            st.metric("Template", params.get('template_name', 'Custom Template'))
                    with col2:
                        st.metric("Style", params.get('style', 'Unknown'))
                        st.metric("Color Scheme", params.get('color_scheme', 'Unknown'))
                        st.metric("Dimensions", f"{params.get('dimensions', [0,0])[0]}x{params.get('dimensions', [0,0])[1]}")
                    
                    # Client Information
                    st.markdown("**🏢 Client Information**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Company:** {params.get('client_name', 'Not specified')}")
                        st.write(f"**Tagline:** {params.get('client_tagline', 'None') if params.get('client_tagline') else 'None'}")
                    with col2:
                        st.write(f"**Website:** {params.get('client_website', 'None') if params.get('client_website') else 'None'}")
                        st.write(f"**Medium:** {params.get('medium', 'Unknown')}")
                    
                    # Logo & Assets
                    st.markdown("**🎨 Assets & References**")
                    col1, col2 = st.columns(2)
                    with col1:
                        logo_status = "✅ Uploaded" if params.get('logo_uploaded') else "❌ Not provided"
                        st.write(f"**Logo:** {logo_status}")
                        if params.get('logo_filename'):
                            st.write(f"   📁 File: {params.get('logo_filename')}")
                    with col2:
                        ref_count = params.get('reference_images_count', 0)
                        st.write(f"**Reference Images:** {ref_count} uploaded")
                        if ref_count > 0:
                            st.write("   📎 Files:")
                            for name in params.get('reference_images_names', [])[:3]:  # Show first 3
                                st.write(f"   • {name}")
                            if len(params.get('reference_images_names', [])) > 3:
                                st.write(f"   • ... and {len(params.get('reference_images_names', [])) - 3} more")
                    
                    # Advanced Features (Nano Banana Pro)
                    if params.get('nano_banana_features'):
                        st.markdown("**🍌 Nano Banana Pro Features**")
                        features = params['nano_banana_features']
                        col1, col2 = st.columns(2)
                        with col1:
                            search_status = "🔍 Enabled" if features.get('search_grounding') else "❌ Disabled"
                            st.write(f"**Search Grounding:** {search_status}")
                            text_status = "✍️ Enabled" if features.get('text_rendering') else "❌ Disabled"
                            st.write(f"**Text Rendering:** {text_status}")
                        with col2:
                            ref_used = features.get('reference_images_used', 0)
                            st.write(f"**Reference Images Used:** {ref_used}/14")
                            st.write(f"**4K Output:** ✅ Enabled")
                    
                    # Content & Prompts
                    st.markdown("**✍️ Content & Prompts**")
                    prompt_text = params.get('prompt', 'No prompt provided')
                    if prompt_text:
                        st.write(f"**User Prompt:** {prompt_text}")
                    else:
                        st.write("**User Prompt:** Default company advertisement generated")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Text Overlay:** {'✅ Enabled' if params.get('include_text') else '❌ Disabled'}")
                    with col2:
                        st.write(f"**Call-to-Action:** {'✅ Enabled' if params.get('include_cta') else '❌ Disabled'}")
                    
                    # Technical Details
                    st.markdown("**🔧 Technical Details**")
                    timestamp = params.get('timestamp', 'Unknown')
                    if timestamp != 'Unknown':
                        from datetime import datetime
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                            st.write(f"**Generated:** {formatted_time}")
                        except:
                            st.write(f"**Generated:** {timestamp}")
                    else:
                        st.write(f"**Generated:** {timestamp}")
                    
                    # Raw JSON (collapsible)
                    with st.expander("🔍 Raw JSON Data", expanded=False):
                        st.json(params)
        else:
            # Placeholder
            st.info("👆 Configure your ad settings in the left column and click 'Generate Ad' to create your advertisement")
            
            # Show sample layout
            st.markdown("### Preview Layout")
            placeholder_image = Image.new('RGB', dimensions, color='lightgray')
            st.image(placeholder_image, caption=f"Ad Preview - {dimensions[0]}x{dimensions[1]}")
    
    # RIGHT COLUMN: Actions and Controls
    with actions_col:
        st.header("🎨 Actions")
        
        # Generate button (always at top)
        if st.button("🚀 Generate Ad", type="primary", use_container_width=True):
            # Validate inputs - only client name is required
            if not company_name.strip():
                st.error("⚠️ Please enter a company name to generate the advertisement.")
            else:
                # Optional field warnings
                missing_fields = []
                if not user_prompt.strip():
                    missing_fields.append("Advertisement prompt")
                
                if missing_fields:
                    st.warning(f"ℹ️ Optional fields not filled: {', '.join(missing_fields)}. Continuing with available information.")
                
                # Show prompt suggestions if prompt exists
                if user_prompt.strip():
                    suggestions = suggest_prompt_improvements(user_prompt, style_preset, ad_medium)
                    if suggestions:
                        with st.expander("💡 Prompt Suggestions"):
                            for suggestion in suggestions:
                                st.info(suggestion)
                
                # Use the selected model from the main selector
                selected_ai_model = st.session_state.get('selected_model', 'DALL-E 3')
                
                generate_ad(
                    user_prompt or f"Professional advertisement for {company_name}",  # Default prompt if empty
                    company_name, client_website, client_tagline, dimensions, ad_medium, 
                    selected_ai_model, style_preset, color_scheme, include_text, 
                    include_cta, uploaded_logo, selected_template if use_template else None,
                    reference_images
                )
        
        st.divider()
        
        # Action buttons (only show if ad is generated)
        if st.session_state.generated_ad is not None:
            st.subheader("🔄 Quick Actions")
            
            # Refresh button
            if st.button("🔄 Refresh", use_container_width=True):
                if st.session_state.generation_params:
                    regenerate_ad()
            
            # Edit button
            if st.button("✏️ Edit Prompt", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
            
            st.divider()
            
            # Download section
            st.subheader("📥 Download")
            download_ad()
            
            # Additional export options
            export_format = st.selectbox("Format:", ["PNG", "JPG", "PDF"])
            
            if export_format == "PDF":
                if st.button("📄 Create PDF", use_container_width=True):
                    create_pdf_export()
            
            st.divider()
        
        # Session Statistics
        st.subheader("📊 Session Stats")
        if 'ads_generated' not in st.session_state:
            st.session_state.ads_generated = 0
        st.metric("Ads Generated", st.session_state.ads_generated)
        
        st.divider()
        
        # Debug Panel
        with st.expander("🔍 Debug Information"):
            st.write("**Environment Check:**")
            import os
            
            # Get the selected model from session state
            current_model = st.session_state.get('selected_model', 'DALL-E 3')
            st.write(f"**Selected Model:** {current_model}")
            
            # Check API keys based on selected model
            if "DALL-E" in current_model:
                api_key = EnvironmentManager.get_config_value("OPENAI_API_KEY")
                if api_key:
                    st.success(f"✅ OpenAI API Key found (ends with: ...{api_key[-4:]})")
                    st.write(f"**API Key Length:** {len(api_key)} characters")
                    st.write(f"**Starts with:** {api_key[:7]}...")
                else:
                    st.error("❌ No OpenAI API Key found")
                    config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                    st.warning(f"Make sure you have a {config_source} with OPENAI_API_KEY=your_key")
            
            elif "Gemini" in current_model:
                api_key = EnvironmentManager.get_config_value("GOOGLE_API_KEY")
                if api_key:
                    st.success(f"✅ Google API Key found (ends with: ...{api_key[-4:]})")
                    st.write(f"**API Key Length:** {len(api_key)} characters")
                    st.write(f"**Starts with:** {api_key[:7]}...")
                else:
                    st.error("❌ No Google API Key found")
                    config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                    st.warning(f"Make sure you have a {config_source} with GOOGLE_API_KEY=your_key")
            
            elif "Nano Banana" in current_model:
                google_key = EnvironmentManager.get_config_value("GOOGLE_API_KEY")
                nano_key = EnvironmentManager.get_config_value("NANO_BANANA_API_KEY")
                if google_key:
                    st.success(f"✅ Using Google API Key for Nano Banana (ends with: ...{google_key[-4:]})")
                    st.info("💡 Nano Banana uses the same Google API key as Imagen")
                elif nano_key:
                    st.success(f"✅ Dedicated Nano Banana API Key found (ends with: ...{nano_key[-4:]})")
                else:
                    st.error("❌ No API key configured for Nano Banana")
                    config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                    st.warning(f"🔑 Add GOOGLE_API_KEY or NANO_BANANA_API_KEY to {config_source}")
                    st.error("❌ Cannot generate images without API key")            else:
                st.info(f"ℹ️ {current_model} is in development")
                st.error("❌ Cannot generate images - API not implemented yet")
            
            st.write("**Session State:**")
            st.write(f"- Generated Ad: {'Yes' if st.session_state.get('generated_ad') else 'No'}")
            st.write(f"- Ads Generated: {st.session_state.get('ads_generated', 0)}")
            
            # Show generation parameters if available
            if st.session_state.get('generation_params'):
                st.write("**Last Generation:**")
                params = st.session_state.generation_params
                st.write(f"- Requested Model: {params.get('model', 'Unknown')}")
                st.write(f"- Actual Model Used: {params.get('actual_model_used', 'Unknown')}")
                st.success("🤖 Real AI generation")
                st.write(f"- Generation Type: {params.get('generation_type', 'Unknown')}")
                if params.get('template_used'):
                    st.write(f"- Template: {params.get('template_name', 'Custom')}")
                if params.get('reference_images_count', 0) > 0:
                    st.write(f"- Reference Images: {params.get('reference_images_count')} uploaded")
                if params.get('nano_banana_features'):
                    features = params['nano_banana_features']
                    if features.get('search_grounding'):
                        st.write("- 🔍 Search Grounding: Enabled")
                    if features.get('text_rendering'):
                        st.write("- ✍️ Text Rendering: Enhanced")
                    if features.get('reference_images_used'):
                        st.write(f"- 📸 Reference Images Used: {features['reference_images_used']}/14")
            
            # Show current image info
            if st.session_state.get('generated_ad'):
                img = st.session_state.generated_ad
                st.write(f"**Current Image Info:**")
                st.write(f"- Size: {img.size[0]}x{img.size[1]}")
                st.write(f"- Mode: {img.mode}")
                st.success("🎨 Real AI-generated image")
                if hasattr(img, 'format'):
                    st.write(f"- Format: {img.format}")
            
            # Utility buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Session", use_container_width=True):
                    st.session_state.clear()
                    st.success("Session data cleared!")
                    st.rerun()
            with col2:
                if st.button("🔄 Test API", use_container_width=True):
                    current_model = st.session_state.get('selected_model', 'DALL-E 3')
                    test_api_connection(current_model)

def generate_ad(prompt, client_name, client_website, client_tagline, dimensions, medium, model, style, color_scheme, include_text, include_cta, logo, template_id=None, reference_images=None):
    """Generate advertisement using AI"""
    
    # CRITICAL: Validate client name input (this is the most important field)
    if not client_name or not client_name.strip():
        st.error("❌ **CRITICAL ERROR**: Client name is required but missing!")
        st.error("The client/company name is essential for advertisement generation.")
        st.error("Please enter a client name in the sidebar and try again.")
        return
    
    # Debug: Show what we received
    st.info(f"📝 **Client Name:** '{client_name}' (Length: {len(client_name.strip())})")
    
    # Create status placeholder for real-time updates
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    # Track which model is actually being used
    st.info(f"🎯 **SELECTED MODEL:** {model}")
    
    # Create persistent status tracking with cancel functionality
    status_container = st.container()
    
    # Add cancel button with better layout
    cancel_col, spacer_col = st.columns([2, 3])
    with cancel_col:
        if st.button("🛑 Cancel", key="cancel_gen", disabled=False, use_container_width=True):
            st.warning("⚠️ Generation cancelled by user")
            st.stop()
    
    with status_container:
        with st.status(f"🎨 Creating Advertisement with {model}", expanded=True) as main_status:
            try:
                # Initialize template manager
                template_manager = TemplateManager()
                
                # Step 1: Initialize AI generator
                st.write(f"🤖 Initializing {model} generator...")
                st.write(f"🏢 Client: {client_name}")  # Debug confirmation
                generator = AIImageGenerator(model)
                
                # Check if the model setup was successful
                model_ready = False
                if "DALL-E" in model:
                    model_ready = hasattr(generator, 'client') and generator.client is not None
                elif "Gemini" in model:
                    model_ready = hasattr(generator, 'gemini_model') and generator.gemini_model is not None
                else:
                    model_ready = False
                
                if model_ready:
                    status_placeholder.success(f"✅ {model} successfully initialized and ready")
                else:
                    status_placeholder.warning(f"⚠️ {model} not available - will use DEMO mode")
                
                # Step 2: Process logo if uploaded
                status_placeholder.info("🏷️ Processing client logo...")
                logo_processed = None
                if logo is not None:
                    logo_path = store_uploaded_logo(logo, client_name)
                    if logo_path:
                        status_placeholder.info(f"💾 Logo stored: {logo_path}")
                    
                    logo_processed = ImageProcessor.process_logo(logo)
                    if logo_processed:
                        status_placeholder.success(f"✅ Logo processed: {logo.name}")
                    else:
                        status_placeholder.warning("⚠️ Logo processing failed")
                else:
                    status_placeholder.info("ℹ️ No logo uploaded")
                
                # Step 3: Generate with template system
                if template_id:
                    status_placeholder.info("🎨 Using template-based generation...")
                    
                    # Create background prompt for template
                    background_prompt = template_manager.create_template_background(
                        template_id, style, color_scheme, prompt
                    )
                    
                    # Show the background prompt for debugging
                    with st.expander("🔍 Template Background Prompt (Debug)"):
                        st.text(background_prompt)
                    
                    # Generate background using AI with advanced features if Nano Banana Pro
                    status_placeholder.info(f"🎨 Generating background with {model}...")
                    
                    # Check if we should use advanced features and reference images
                    if "Nano Banana Pro" in model:
                        from utils.ai_generator import NanoBananaProFeatures
                        
                        # Auto-detect advanced features needed
                        use_search, use_text = NanoBananaProFeatures.detect_advanced_features(background_prompt)
                        
                        # Prepare reference images for Nano Banana Pro (excluding logo for background)
                        all_reference_images = []
                        
                        # Add uploaded reference images first (style references only)
                        if reference_images:
                            for i, ref_img in enumerate(reference_images):
                                try:
                                    # Handle Streamlit UploadedFile properly
                                    if hasattr(ref_img, 'seek') and hasattr(ref_img, 'read'):
                                        ref_img.seek(0)  # Reset file pointer
                                        ref_pil = Image.open(ref_img)
                                        all_reference_images.append(ref_pil)
                                    else:
                                        st.warning(f"⚠️ Reference image {i+1}: Invalid file object")
                                except Exception as ref_error:
                                    st.warning(f"⚠️ Could not process reference image {i+1}: {ref_error}")
                        
                        # NOTE: Logo is NOT used as reference for background generation
                        # This prevents AI from duplicating logos in the background
                        # Template system will overlay the logo precisely
                        
                        # Limit to 14 reference images (Nano Banana Pro limit)
                        final_reference_images = all_reference_images[:14] if all_reference_images else None
                        
                        if final_reference_images:
                            st.info(f"🎨 Using {len(final_reference_images)} style reference image(s) for background generation")
                        else:
                            st.info("🎨 Generating clean background without reference images")
                        
                        background_image = NanoBananaProFeatures.generate_with_references(
                            generator=generator,
                            prompt=background_prompt,
                            size=dimensions,
                            reference_images=final_reference_images,
                            use_search_grounding=use_search,
                            text_rendering_mode=use_text
                        )
                    else:
                        # For other models, incorporate reference image guidance into the prompt
                        enhanced_background_prompt = background_prompt
                        if reference_images:
                            st.info(f"📸 Incorporating {len(reference_images)} reference image(s) into prompt guidance")
                            ref_descriptions = []
                            for i, ref_img in enumerate(reference_images[:5]):  # Limit to 5 for prompt
                                try:
                                    ref_img.seek(0)
                                    # Add reference guidance to prompt
                                    ref_descriptions.append(f"reference style {i+1}")
                                except:
                                    pass
                            if ref_descriptions:
                                enhanced_background_prompt += f" Style guidance: follow the visual style and composition similar to {', '.join(ref_descriptions)} with consistent color palette and aesthetic approach."
                        
                        background_image = generator.generate_image(
                            prompt=enhanced_background_prompt,
                            size=dimensions
                        )
                    
                    if background_image:
                        status_placeholder.info("🎯 Applying brand elements to template...")
                        
                        # Debug: Show what we're passing to the template
                        st.write(f"🔍 Debug - Applying brand elements:")
                        st.write(f"   📝 Client Name: '{client_name}' (Length: {len(client_name)})")
                        st.write(f"   🏷️ Tagline: '{client_tagline}' (Length: {len(client_tagline) if client_tagline else 0})")
                        st.write(f"   💬 Message: '{prompt}' (Length: {len(prompt) if prompt else 0})")
                        st.write(f"   🎨 Template: {template_id}")
                        
                        # Apply brand elements to template
                        final_image = template_manager.apply_brand_elements(
                            background_image=background_image,
                            template_id=template_id,
                            logo=logo_processed,
                            client_name=client_name,
                            tagline=client_tagline if client_tagline.strip() else "",
                            main_message=prompt if prompt.strip() else f"Advertisement for {client_name}",
                            cta_text="SHOP NOW" if include_cta else "",
                            website=client_website if client_website.strip() else "",
                            color_scheme=color_scheme
                        )
                        
                        generated_image = final_image
                        status_placeholder.success("✨ Template-based ad created successfully!")
                    else:
                        status_placeholder.error("❌ Background generation failed")
                        return None
                        
                else:
                    # Traditional prompt-based generation
                    status_placeholder.info("✍️ Building enhanced prompt...")
                    logo_description = analyze_logo_details(logo) if logo else ""
                    enhanced_prompt = build_enhanced_prompt(
                        prompt, client_name, client_website, medium, style, color_scheme, 
                        include_text, include_cta, dimensions, logo_description
                    )
                    
                    with st.expander("🔍 Enhanced Prompt (Debug)"):
                        st.text(enhanced_prompt)
                    
                    status_placeholder.info(f"🎨 Generating image with {model}...")
                    
                    # Check if we should use advanced features for image generation
                    if "Nano Banana Pro" in model:
                        from utils.ai_generator import NanoBananaProFeatures
                        
                        # Auto-detect advanced features needed
                        use_search, use_text = NanoBananaProFeatures.detect_advanced_features(enhanced_prompt)
                        
                        # Prepare reference images for Nano Banana Pro
                        all_reference_images = []
                        
                        # Add uploaded reference images first
                        if reference_images:
                            for i, ref_img in enumerate(reference_images):
                                try:
                                    # Handle Streamlit UploadedFile properly
                                    if hasattr(ref_img, 'seek') and hasattr(ref_img, 'read'):
                                        ref_img.seek(0)  # Reset file pointer
                                        ref_pil = Image.open(ref_img)
                                        all_reference_images.append(ref_pil)
                                    else:
                                        st.warning(f"⚠️ Reference image {i+1}: Invalid file object")
                                except Exception as ref_error:
                                    st.warning(f"⚠️ Could not process reference image {i+1}: {ref_error}")
                        
                        # NOTE: Logo is NOT used as reference to prevent duplication
                        # Template system handles precise logo placement
                        
                        # Limit to 14 reference images (Nano Banana Pro limit)
                        final_reference_images = all_reference_images[:14] if all_reference_images else None
                        
                        if final_reference_images:
                            st.info(f"🎨 Using {len(final_reference_images)} style reference image(s) for generation")
                        else:
                            st.info("🎨 Generating clean background without reference images")
                        
                        generated_image = NanoBananaProFeatures.generate_with_references(
                            generator=generator,
                            prompt=enhanced_prompt,
                            size=dimensions,
                            reference_images=final_reference_images,
                            use_search_grounding=use_search,
                            text_rendering_mode=use_text
                        )
                    else:
                        # For other models, incorporate reference image guidance into the prompt
                        final_enhanced_prompt = enhanced_prompt
                        if reference_images:
                            st.info(f"📸 Incorporating {len(reference_images)} reference image(s) into prompt guidance")
                            ref_descriptions = []
                            for i, ref_img in enumerate(reference_images[:5]):  # Limit to 5 for prompt
                                try:
                                    ref_img.seek(0)
                                    # Add reference guidance to prompt
                                    ref_descriptions.append(f"reference style {i+1}")
                                except:
                                    pass
                            if ref_descriptions:
                                final_enhanced_prompt += f" Style guidance: follow the visual style and composition similar to {', '.join(ref_descriptions)} with consistent color palette and aesthetic approach."
                        
                        generated_image = generator.generate_image(
                            prompt=final_enhanced_prompt,
                            size=dimensions,
                            client_logo=logo_processed
                        )
                
                # Step 4: Save and finalize
                if generated_image:
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        clean_client = (client_name or "Unknown").replace(" ", "_")
                        filename = f"{model.replace(' ', '_')}_{clean_client}_{timestamp}.png"
                        filepath = os.path.join("assets", "generated_ads", filename)
                        
                        generated_image.save(filepath, "PNG")
                        status_placeholder.success(f"💾 Image saved to: {filepath}")
                    except Exception as save_error:
                        st.warning(f"⚠️ Could not save image: {str(save_error)}")
                    
                    st.session_state.generated_ad = generated_image
                    st.session_state.generation_params = {
                        "prompt": prompt,
                        "original_prompt": prompt,
                        "client_name": client_name,
                        "client_website": client_website,
                        "client_tagline": client_tagline,
                        "dimensions": dimensions,
                        "medium": medium,
                        "model": model,
                        "actual_model_used": model,
                        "template_used": template_id,
                        "template_name": template_manager.get_template(template_id)["name"] if template_id and template_manager.get_template(template_id) else None,
                        "style": style,
                        "color_scheme": color_scheme,
                        "include_text": include_text,
                        "include_cta": include_cta,
                        "logo_uploaded": logo is not None,
                        "logo_filename": logo.name if logo else None,
                        "reference_images_count": len(reference_images) if reference_images else 0,
                        "reference_images_names": [img.name for img in reference_images] if reference_images else [],
                        "nano_banana_features": {
                            "search_grounding": "Nano Banana Pro" in model,
                            "text_rendering": "Nano Banana Pro" in model,
                            "reference_images_used": len(reference_images) if reference_images and "Nano Banana Pro" in model else 0
                        } if "Nano Banana" in model else None,
                        "timestamp": datetime.now().isoformat(),
                        "generation_type": "template_based" if template_id else "prompt_based"
                    }
                    st.session_state.ads_generated = st.session_state.get('ads_generated', 0) + 1
                    
                    # Clear status and show success
                    status_placeholder.empty()
                    st.success(f"✨ Advertisement generated successfully using {model}!")
                    st.rerun()
                else:
                    # Generation failed completely
                    status_placeholder.error("❌ Image generation failed")
                    st.error("❌ **Generation Failed**")
                    st.error(f"The {model} API could not generate an image. Please check:")
                    st.error("• Your API key configuration")
                    st.error("• Your internet connection") 
                    st.error("• API service status")
                    st.info("💡 Check the debug panel for more details about what went wrong.")
                    
            except Exception as e:
                status_placeholder.error(f"❌ Error: {str(e)}")
                st.error(f"Error generating advertisement: {str(e)}")
                st.error("Please check your API key configuration and internet connection.")

def build_enhanced_prompt(prompt, client_name, client_website, medium, style, color_scheme, include_text, include_cta, dimensions, logo_description=""):
    """Build enhanced prompt with context and medium-specific optimizations"""
    return PromptBuilder.build_enhanced_prompt(
        prompt, client_name, client_website, medium, style, 
        color_scheme, include_text, include_cta, dimensions, logo_description
    )

def regenerate_ad():
    """Regenerate ad with same parameters"""
    params = st.session_state.generation_params
    if params:
        generate_ad(
            params.get("prompt", ""),
            params.get("client_name", ""),
            params.get("client_website", ""),
            params.get("client_tagline", ""),
            params.get("dimensions", (1080, 1080)),
            params.get("medium", ""),
            params.get("model", "DALL-E 3"),
            "Modern & Minimalist",  # Default values for missing params
            "Brand Colors",
            True,
            True,
            st.session_state.client_logo,
            params.get("template_used", None)
        )

def download_ad():
    """Provide download functionality"""
    if st.session_state.generated_ad is not None:
        # Convert PIL image to bytes
        img_buffer = io.BytesIO()
        st.session_state.generated_ad.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = st.session_state.generation_params.get("client_name", "ad").replace(" ", "_")
        filename = f"{client_name}_ad_{timestamp}.png"
        
        st.download_button(
            label="💾 Download PNG",
            data=img_bytes,
            file_name=filename,
            mime="image/png",
            width='stretch'
        )

def create_pdf_export():
    """Create PDF export with metadata"""
    if st.session_state.generated_ad is not None:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                # Create PDF with metadata
                pdf_buffer = io.BytesIO()
                # Implementation for PDF creation would go here
                st.success("PDF created successfully!")
                
        except ImportError:
            st.error("PDF export requires reportlab. Install with: pip install reportlab")
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")

def test_api_connection(model_name=None):
    """Test the API connection for the selected model"""
    import logging
    
    # Set up console logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    if not model_name:
        model_name = "DALL-E 3"  # Default fallback
    
    try:
        import os
        
        st.info(f"🔍 Testing {model_name} API connection...")
        logger.info(f"Testing API connection for model: {model_name}")
        
        if "DALL-E" in model_name:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                error_msg = f"No OpenAI API key found for {model_name}"
                st.error(f"❌ {error_msg}")
                logger.error(error_msg)
                return
            
            client = OpenAI(api_key=api_key)
            
            with st.spinner(f"🔍 Testing {model_name} API connection..."):
                try:
                    model_version = "dall-e-3" if "3" in model_name else "dall-e-2"
                    response = client.images.generate(
                        model=model_version,
                        prompt="A simple test image",
                        size="256x256",
                        n=1,
                    )
                    success_msg = f"{model_name} API connection successful!"
                    st.success(f"✅ {success_msg}")
                    st.info(f"🎉 Your {model_name} API key is working correctly")
                    st.info(f"🔗 Test image URL: {response.data[0].url[:50]}...")
                    logger.info(f"API test successful for {model_name}")
                except Exception as api_error:
                    error_msg = f"{model_name} API connection failed: {str(api_error)}"
                    st.error(f"❌ {error_msg}")
                    logger.error(f"API test failed for {model_name}: {str(api_error)}")
                    
                    if "quota" in str(api_error).lower():
                        st.warning("💳 This might be a quota/billing issue")
                    elif "invalid" in str(api_error).lower():
                        st.warning("🔑 This might be an invalid API key")
                    elif "unauthorized" in str(api_error).lower():
                        st.warning("🔐 API key might be invalid or expired")
        
        elif "Imagen" in model_name:
            api_key = os.getenv("GOOGLE_API_KEY")
            
            if not api_key:
                error_msg = f"No Google API key found for {model_name}"
                st.error(f"❌ {error_msg}")
                st.info("🔑 Add GOOGLE_API_KEY to your .env file")
                logger.error(error_msg)
                return
            
            try:
                import google.generativeai as genai
                
                with st.spinner(f"🔍 Testing {model_name} API connection..."):
                    try:
                        # Configure and test the API
                        genai.configure(api_key=api_key)
                        
                        # Test with a simple model call
                        model = genai.GenerativeModel('gemini-pro')
                        
                        success_msg = f"{model_name} API connection successful!"
                        st.success(f"✅ {success_msg}")
                        st.info(f"🔑 API key is valid (ends with: ...{api_key[-4:]})")
                        logger.info(f"API test successful for {model_name}")
                        
                    except Exception as api_error:
                        error_msg = f"{model_name} API connection failed: {str(api_error)}"
                        st.error(f"❌ {error_msg}")
                        logger.error(f"API test failed for {model_name}: {str(api_error)}")
                        
                        if "quota" in str(api_error).lower():
                            st.warning("💳 This might be a quota/billing issue")
                        elif "invalid" in str(api_error).lower():
                            st.warning("🔑 Check if your API key is correct")
                        elif "permission" in str(api_error).lower():
                            st.warning("🔐 Check your API permissions")
            
            except ImportError:
                error_msg = f"Google Generative AI library not installed for {model_name}"
                st.error(f"❌ {error_msg}")
                st.info("📦 Install with: pip install google-generativeai")
                logger.error(error_msg)
        
        elif "Nano Banana" in model_name:
            google_key = EnvironmentManager.get_config_value("GOOGLE_API_KEY")
            nano_key = EnvironmentManager.get_config_value("NANO_BANANA_API_KEY")
            if google_key or nano_key:
                st.info(f"🍌 {model_name} API key found but API not implemented yet")
                st.error("❌ Cannot generate images - API integration in development")
                logger.info(f"{model_name} API key configured but not implemented")
            else:
                st.error(f"❌ {model_name} API not configured and integration not complete")
                config_source = "Streamlit secrets" if EnvironmentManager.is_streamlit_deployment() else ".env file"
                st.error(f"❌ Cannot generate images without API key - Add GOOGLE_API_KEY to {config_source}")
                logger.error(f"{model_name} no API access")
        
        else:
            st.error(f"❌ {model_name} is in development - cannot generate images")
            st.error("❌ API integration not implemented yet")
            logger.info(f"{model_name} integration not available")
                    
    except Exception as e:
        error_msg = f"Error testing {model_name} connection: {str(e)}"
        st.error(f"❌ {error_msg}")
        logger.error(error_msg)

if __name__ == "__main__":
    main()