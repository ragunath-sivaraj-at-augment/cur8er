import streamlit as st
from utils.config import Config, EnvironmentManager
from utils.ai_generator import APIKeyManager

def setup_api_keys():
    """Setup and display API key configuration status"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 API Configuration")
    
    # Get API keys using the new EnvironmentManager
    openai_key = EnvironmentManager.get_config_value("OPENAI_API_KEY")
    google_key = EnvironmentManager.get_config_value("GOOGLE_API_KEY")
    # nano_banana_key = EnvironmentManager.get_config_value("NANO_BANANA_API_KEY")
    
    # Display deployment context
    is_streamlit_deployment = EnvironmentManager.is_streamlit_deployment()
    config_source = "Streamlit Secrets" if is_streamlit_deployment else "Environment Variables"
    st.sidebar.info(f"📍 Config source: {config_source}")
    
    if openai_key:
        st.sidebar.success("✅ OpenAI API Key configured")
    else:
        st.sidebar.error("❌ OpenAI API Key missing")
        if is_streamlit_deployment:
            st.sidebar.info("🔐 Add OPENAI_API_KEY to Streamlit secrets")
        else:
            st.sidebar.info("📄 Add OPENAI_API_KEY to your .env file")
    
    if google_key:
        st.sidebar.success("✅ Google API Key configured")
    else:
        st.sidebar.warning("⚠️ Google API Key missing (for Gemini)")
        if is_streamlit_deployment:
            st.sidebar.info("🔐 Add GOOGLE_API_KEY to Streamlit secrets")
        else:
            st.sidebar.info("📄 Add GOOGLE_API_KEY to your .env file")
    
    # if nano_banana_key:
    #     st.sidebar.success("✅ Nano Banana API Key configured")
    # else:
    #     st.sidebar.info("ℹ️ Nano Banana API Key missing (placeholder)")
    
    # Display API status
    with st.sidebar.expander("API Status"):
        st.write("**OpenAI (DALL-E):**", "✅ Ready" if openai_key else "❌ Not configured")
        st.write("**Google (Gemini):**", "✅ Ready" if google_key else "❌ Not configured")
        # st.write("**Nano Banana:**", "✅ Ready" if nano_banana_key else "🔧 Coming Soon")
        st.write("**Stable Diffusion:**", "🔧 Coming Soon")
        st.write("**Midjourney:**", "🔧 Coming Soon")

def display_model_info(selected_model):
    """Display information about the selected AI model"""
    from utils.ai_generator import MODEL_CONFIGS
    
    if selected_model in MODEL_CONFIGS:
        config = MODEL_CONFIGS[selected_model]
        
        with st.sidebar.expander(f"ℹ️ {selected_model} Info"):
            st.write(f"**Provider:** {config['provider']}")
            st.write(f"**Max Size:** {config['max_size'][0]}x{config['max_size'][1]}")
            st.write(f"**Quality:** {config['quality']}")
            st.write(f"**API Key Required:** {'Yes' if config['requires_key'] else 'No'}")

def show_generation_tips():
    """Display tips for better ad generation"""
    with st.sidebar.expander("💡 Generation Tips"):
        st.markdown("""
        **For better results:**
        
        🎯 **Be Specific**
        - Include colors, style, and mood
        - Mention specific products/services
        - Describe the target audience
        
        🎨 **Visual Elements**
        - Specify typography style
        - Mention layout preferences  
        - Include lighting and composition details
        
        📱 **Platform Optimization**
        - Consider the selected medium
        - Think about viewing distance
        - Account for text readability
        
        **Example:** "A modern smartphone advertisement with sleek design, blue and white color scheme, minimalist layout, professional photography, clear product shot, elegant typography, for tech-savvy millennials"
        """)

def display_usage_stats():
    """Display usage statistics"""
    if 'usage_stats' not in st.session_state:
        st.session_state.usage_stats = {
            'total_generations': 0,
            'successful_generations': 0,
            'favorite_style': 'Modern & Minimalist',
            'most_used_size': 'Square (1080x1080)'
        }
    
    stats = st.session_state.usage_stats
    
    with st.sidebar.expander("📊 Usage Statistics"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", stats['total_generations'])
        with col2:
            st.metric("Success", stats['successful_generations'])
        
        if stats['total_generations'] > 0:
            success_rate = (stats['successful_generations'] / stats['total_generations']) * 100
            st.progress(success_rate / 100)
            st.caption(f"Success Rate: {success_rate:.1f}%")

def export_project_data():
    """Export generated ads and project data"""
    if st.sidebar.button("📦 Export Project Data"):
        try:
            import zipfile
            import io
            import json
            from datetime import datetime
            
            # Create zip buffer
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add project metadata
                metadata = {
                    'export_date': datetime.now().isoformat(),
                    'app_version': Config.APP_CONFIG['version'],
                    'total_ads_generated': st.session_state.get('ads_generated', 0),
                    'generation_params': st.session_state.get('generation_params', {})
                }
                
                zip_file.writestr('project_metadata.json', json.dumps(metadata, indent=2))
                
                # Add generated ad if available
                if st.session_state.get('generated_ad'):
                    img_buffer = io.BytesIO()
                    st.session_state.generated_ad.save(img_buffer, format='PNG')
                    zip_file.writestr('generated_ad.png', img_buffer.getvalue())
            
            zip_buffer.seek(0)
            
            st.sidebar.download_button(
                "💾 Download Project Export",
                data=zip_buffer.getvalue(),
                file_name=f"ad_creator_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
            
        except Exception as e:
            st.sidebar.error(f"Export failed: {str(e)}")

# Helper functions for the main app
def validate_inputs(client_name, prompt):
    """Validate user inputs"""
    errors = []
    
    if not client_name.strip():
        errors.append("Client name is required")
    
    if not prompt.strip():
        errors.append("Creative prompt is required")
    
    if len(prompt.strip()) < 10:
        errors.append("Prompt should be more descriptive (at least 10 characters)")
    
    return errors

def suggest_prompt_improvements(prompt, style, medium):
    """Suggest improvements for the user's prompt"""
    suggestions = []
    
    # Check for style keywords
    style_config = Config.get_style_config(style)
    style_keywords = style_config.get('keywords', '').split(', ')
    
    if not any(keyword in prompt.lower() for keyword in style_keywords):
        suggestions.append(f"Consider adding style keywords like: {', '.join(style_keywords[:3])}")
    
    # Check for medium-specific elements
    if "social media" in medium.lower() and "hashtag" not in prompt.lower():
        suggestions.append("For social media, consider mentioning hashtag placement")
    
    if "print" in medium.lower() and "high resolution" not in prompt.lower():
        suggestions.append("For print ads, specify high resolution and print-quality elements")
    
    # Check prompt length
    if len(prompt.split()) < 15:
        suggestions.append("Try adding more descriptive details for better results")
    
    return suggestions