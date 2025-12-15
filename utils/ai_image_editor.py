"""
AI-Powered Image Editor using DALL-E
Allows users to modify generated images using natural language prompts
"""

import streamlit as st
from PIL import Image, ImageDraw
import io
import os
from datetime import datetime
from typing import Optional
from .ai_generator import AIImageGenerator

def show_ai_image_editor():
    """Display AI-powered image editing interface for DALL-E models"""
    
    if 'generated_ad' not in st.session_state or st.session_state.generated_ad is None:
        st.error("❌ No image to edit. Please generate an advertisement first.")
        return
    
    if 'generation_params' not in st.session_state:
        st.error("❌ Generation parameters not found.")
        return
    
    # Check if using DALL-E model
    model_name = st.session_state.generation_params.get("model", "")
    if "DALL-E" not in model_name:
        st.warning(f"⚠️ AI image editing is only available for DALL-E models. Current model: {model_name}")
        st.info("💡 Use the Filerobot editor for manual editing, or regenerate with DALL-E to use AI editing.")
        return
    
    st.markdown("### ✨ AI-Powered Image Editor")
    st.markdown("""
    **Transform your image with AI using natural language!**
    
    Describe the changes you want to make, and DALL-E will intelligently modify your image.
    """)
    
    # Show current image
    st.image(st.session_state.generated_ad, caption="Current Image", use_column_width=True)
    
    st.markdown("---")
    
    # Enhancement presets
    st.markdown("#### 🎯 Quick Enhancements")
    st.markdown("Choose a preset or write your own custom modification:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎨 Change Text Color", width='stretch'):
            st.session_state.edit_preset = "Change the text color to black with white outline for better readability"
    
    with col2:
        if st.button("🌈 Enhance Colors", width='stretch'):
            st.session_state.edit_preset = "Make the colors more vibrant and eye-catching, increase saturation and contrast"
    
    with col3:
        if st.button("✨ Professional Polish", width='stretch'):
            st.session_state.edit_preset = "Add professional polish with subtle shadows, lighting effects, and refined typography"
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🔆 Brighten Image", width='stretch'):
            st.session_state.edit_preset = "Brighten the overall image, increase exposure and make it more vibrant"
    
    with col5:
        if st.button("🎭 Change Background", width='stretch'):
            st.session_state.edit_preset = "Change the background to a gradient from blue to purple, keep all other elements the same"
    
    with col6:
        if st.button("📐 Reposition Elements", width='stretch'):
            st.session_state.edit_preset = "Move the main text to the top center and the button to the bottom, keep everything else the same"
    
    st.markdown("---")
    
    # Custom modification prompt
    st.markdown("#### ✏️ Custom Modification")
    
    # Use preset if selected, otherwise use custom
    default_prompt = st.session_state.get('edit_preset', '')
    
    modification_prompt = st.text_area(
        "Describe the changes you want to make:",
        value=default_prompt,
        height=100,
        placeholder="Example: Change the text color to black, make the background white instead of blue, move the logo to the top right corner",
        help="Be specific about what you want to change. DALL-E will modify only the parts you mention."
    )
    
    # Clear preset after use
    if 'edit_preset' in st.session_state:
        del st.session_state.edit_preset
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        st.markdown("**Enhancement Settings:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            preserve_composition = st.checkbox(
                "Preserve Composition",
                value=True,
                help="Keep the overall layout and structure the same"
            )
            
            preserve_style = st.checkbox(
                "Preserve Art Style",
                value=True,
                help="Maintain the same artistic style and aesthetic"
            )
        
        with col2:
            preserve_colors = st.checkbox(
                "Preserve Color Scheme",
                value=False,
                help="Keep the same color palette (unless changing colors)"
            )
            
            high_quality = st.checkbox(
                "High Quality Output",
                value=True,
                help="Use best quality settings for the edited image"
            )
        
        # Build enhancement instructions
        enhancement_instructions = []
        if preserve_composition:
            enhancement_instructions.append("maintain the same composition and layout")
        if preserve_style:
            enhancement_instructions.append("keep the same artistic style")
        if preserve_colors:
            enhancement_instructions.append("preserve the color scheme where not explicitly changed")
        if high_quality:
            enhancement_instructions.append("high quality, professional finish")
        
        if enhancement_instructions:
            st.info(f"🎯 Active enhancements: {', '.join(enhancement_instructions)}")
    
    st.markdown("---")
    
    # Edit button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        edit_button = st.button("✨ Apply AI Edit", type="primary", width='stretch')
    
    if edit_button:
        if not modification_prompt.strip():
            st.error("❌ Please describe the changes you want to make.")
            return
        
        # Build final prompt
        final_prompt = modification_prompt.strip()
        
        # Add enhancement instructions
        if enhancement_instructions:
            final_prompt += f". Please {', and '.join(enhancement_instructions)}."
        
        st.info(f"🔄 AI Edit Prompt: {final_prompt}")
        
        # Show progress
        with st.spinner("✨ AI is editing your image... This may take 10-20 seconds..."):
            try:
                # Initialize AI generator with current model
                generator = AIImageGenerator(model_name)
                
                # Edit the image
                edited_image = generator.edit_dalle_image(
                    image=st.session_state.generated_ad,
                    prompt=final_prompt,
                    mask=None  # No mask = edit entire image intelligently
                )
                
                if edited_image:
                    # Show comparison
                    st.success("✅ Image edited successfully!")
                    
                    st.markdown("#### 🔄 Before & After Comparison")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Original:**")
                        st.image(st.session_state.generated_ad, use_column_width=True)
                    
                    with col2:
                        st.markdown("**AI Edited:**")
                        st.image(edited_image, use_column_width=True)
                    
                    # Store edited image temporarily
                    st.session_state.ai_edited_image = edited_image
                    
                    # Apply button
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        if st.button("✅ Keep Edited Version", type="primary", width='stretch'):
                            st.session_state.generated_ad = edited_image
                            
                            # Save to file
                            try:
                                output_dir = "assets/generated_ads"
                                os.makedirs(output_dir, exist_ok=True)
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                client_name = st.session_state.generation_params.get("client_name", "ad").replace(" ", "_")
                                filename = f"ai_edited_{client_name}_{timestamp}.png"
                                filepath = os.path.join(output_dir, filename)
                                edited_image.save(filepath, "PNG")
                                st.success(f"✅ Edited image saved to: {filepath}")
                            except Exception as save_error:
                                st.warning(f"Image updated but couldn't save to file: {str(save_error)}")
                            
                            st.info("💡 Close the editor to see your updated advertisement")
                            st.balloons()
                    
                    with col2:
                        if st.button("🔄 Try Another Edit", width='stretch'):
                            st.session_state.generated_ad = edited_image
                            st.rerun()
                    
                    with col3:
                        if st.button("❌ Discard Changes", width='stretch'):
                            if 'ai_edited_image' in st.session_state:
                                del st.session_state.ai_edited_image
                            st.info("Changes discarded. Original image preserved.")
                            st.rerun()
                else:
                    st.error("❌ Failed to edit image. Please try a different prompt or check your API key.")
                    
            except Exception as e:
                st.error(f"❌ Error during AI editing: {str(e)}")
                st.info("💡 Try simplifying your edit prompt or check your OpenAI API key configuration.")
    
    # Tips section
    st.markdown("---")
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        **Effective Edit Prompts:**
        - ✅ "Change the text color from white to black"
        - ✅ "Replace the blue background with a sunset gradient"
        - ✅ "Move the logo to the top right corner"
        - ✅ "Make the call-to-action button larger and green"
        - ✅ "Add a subtle drop shadow to the main text"
        
        **Avoid:**
        - ❌ Vague prompts like "make it better"
        - ❌ Too many changes at once (try one change at a time)
        - ❌ Requesting completely new elements not in the original
        
        **Best Practices:**
        - Be specific about colors, positions, and sizes
        - Reference existing elements in your image
        - Start with small changes and iterate
        - Use the presets as examples for prompt formatting
        """)
