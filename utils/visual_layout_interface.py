"""
Visual Layout Generator Interface
Streamlit UI for the visual layout method with drag-and-drop canvas
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import time
import json
from datetime import datetime
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.warning("⚠️ Install streamlit-drawable-canvas for drag-and-drop: pip install streamlit-drawable-canvas")

from utils.visual_layout_builder import VisualLayoutCanvas, SimpleLayoutBuilder, LayoutElement
from utils.visual_layout_prompts import (
    get_visual_layout_prompt, 
    get_placeholder_replacement_map,
    get_scene_style_guidance
)
from utils.ai_generator import AIImageGenerator


def show_visual_layout_generator():
    """Main interface for visual layout generator with drag-and-drop canvas"""
    
    # Header
    st.title("🎨 Visual Layout Generator")
    st.markdown("Create ads by designing the layout visually - AI follows your composition exactly")
    
    # Close button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("❌ Close", key="close_visual_layout"):
            st.session_state.show_visual_layout = False
            # Clear canvas elements to prevent stale image references
            if 'canvas_elements' in st.session_state:
                st.session_state.canvas_elements = []
            st.rerun()
    
    st.markdown("---")
    
    # Check for canvas availability
    if not CANVAS_AVAILABLE:
        st.error("🚨 Drag-and-drop requires streamlit-drawable-canvas")
        st.info("📦 Install it: `pip install streamlit-drawable-canvas`")
        st.info("💡 Restart Streamlit after installing")
        return
    
    # Initialize session state for canvas elements
    if 'canvas_elements' not in st.session_state:
        st.session_state.canvas_elements = []
    
    # Info box
    with st.expander("ℹ️ How to Use", expanded=False):
        st.markdown("""
        **Interactive Canvas Controls:**
        1. **Add Elements**: Click buttons below to add logo, brand name, message, etc.
        2. **Move Elements**: Drag rectangles to reposition
        3. **Resize**: Use transform mode to resize elements
        4. **Delete**: Select element and click delete button
        5. **Generate**: Click generate when layout is ready
        
        **Tips:**
        - 🖱️ Draw rectangles to create custom elements
        - ✏️ Use transform mode to resize existing elements
        - 🗑️ Select and delete unwanted elements
        - 💾 Download your layout as reference image
        """)
    
    # Two column layout: Controls | Canvas
    controls_col, canvas_col = st.columns([1, 2])
    
    with controls_col:
        st.header("⚙️ Configuration")
        
        # Model selection
        st.subheader("1. Model")
        model = st.selectbox(
            "AI Model",
            ["🍌⭐ Nano Banana Pro", "🍌 Nano Banana", "🎨 DALL-E 3"],
            help="Nano Banana Pro recommended"
        )
        
        # Dimensions
        st.subheader("2. Canvas Size")
        dimension_presets = {
            "Instagram Post (1080x1080)": (1080, 1080),
            "Facebook Post (1200x630)": (1200, 630),
            "Instagram Story (1080x1920)": (1080, 1920),
            "Twitter Post (1200x675)": (1200, 675),
            "Custom": None
        }
        
        dim_choice = st.selectbox("Size Preset", list(dimension_presets.keys()))
        
        if dim_choice == "Custom":
            col_w, col_h = st.columns(2)
            with col_w:
                width = st.number_input("Width", 800, 3840, 1920, 10)
            with col_h:
                height = st.number_input("Height", 600, 2160, 1080, 10)
            dimensions = (width, height)
        else:
            dimensions = dimension_presets[dim_choice]
        
        st.markdown(f"**Canvas:** {dimensions[0]}x{dimensions[1]}px")
        
        # Drawing tool selection
        st.subheader("3. Canvas Tools")
        drawing_mode = st.radio(
            "Tool Mode",
            ["rect", "transform"],
            format_func=lambda x: "✏️ Draw" if x == "rect" else "↔️ Transform",
            horizontal=True
        )
        
        # Quick add buttons
        st.subheader("4. Quick Add Elements")
        
        element_types = {
            "[LOGO]": {"w": 200, "h": 120, "type": "logo"},
            "[BRAND NAME]": {"w": 400, "h": 100, "type": "brand"},
            "[MAIN MESSAGE]": {"w": 800, "h": 160, "type": "message"},
            "[TAGLINE]": {"w": 500, "h": 60, "type": "tagline"},
            "[CTA]": {"w": 300, "h": 80, "type": "cta"}
        }
        
        col1, col2 = st.columns(2)
        for i, (label, props) in enumerate(element_types.items()):
            with col1 if i % 2 == 0 else col2:
                if st.button(f"➕ {label}", key=f"add_{props['type']}", width='stretch'):
                    # Add element to canvas
                    new_elem = {
                        "label": label,
                        "type": props["type"],
                        "x": 100 + (i * 50),
                        "y": 100 + (i * 80),
                        "width": props["w"],
                        "height": props["h"]
                    }
                    st.session_state.canvas_elements.append(new_elem)
                    st.rerun()
        
        # Clear all button
        if st.button("🗑️ Clear All Elements", width='stretch'):
            st.session_state.canvas_elements = []
            st.rerun()
        
        # Element list and delete
        if st.session_state.canvas_elements:
            st.subheader("5. Current Elements")
            for idx, elem in enumerate(st.session_state.canvas_elements):
                col_info, col_del = st.columns([3, 1])
                with col_info:
                    st.caption(f"{elem['label']} ({elem['x']}, {elem['y']})")
                with col_del:
                    if st.button("❌", key=f"del_{idx}_{elem['label']}"):
                        st.session_state.canvas_elements.pop(idx)
                        # Force clean rerun
                        st.rerun()
        
        # Content inputs
        st.subheader("6. Content Mapping")
        
        content_mapping = {}
        
        include_logo = st.checkbox("Logo Space", value=True)
        logo = None
        if include_logo:
            logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
            if logo_file is not None:
                try:
                    logo = Image.open(logo_file)
                except Exception as e:
                    st.error(f"Error loading logo: {e}")
                    logo = None
            content_mapping["[LOGO]"] = "logo_space"
        else:
            logo = None
        
        brand_name = st.text_input("Brand Name", placeholder="e.g., Mosaic")
        if brand_name:
            content_mapping["[BRAND NAME]"] = brand_name
        
        main_message = st.text_input("Main Message", placeholder="e.g., Premium Living Spaces")
        if main_message:
            content_mapping["[MAIN MESSAGE]"] = main_message
        
        tagline = st.text_input("Tagline (optional)", placeholder="e.g., Real life. Real possibilities")
        if tagline:
            content_mapping["[TAGLINE]"] = tagline
        
        cta_text = st.text_input("CTA Text (optional)", placeholder="e.g., Visit Us")
        if cta_text:
            content_mapping["[CTA]"] = cta_text
        
        # Scene style
        st.subheader("7. Scene Style")
        style = st.selectbox(
            "Visual Style",
            ["Modern & Minimalist", "Modern", "Luxury", "Professional", "Creative"]
        )
        
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Brand Colors", "Monochrome", "Warm Tones", "Cool Tones", "Vibrant"]
        )
        
        scene_description = st.text_area(
            "Scene Description (optional)",
            placeholder="Describe the environment...",
            height=80
        )
    
    with canvas_col:
        st.header("🖼️ Interactive Canvas")
        
        # Scale canvas for display
        display_width = 800
        scale = display_width / dimensions[0]
        display_height = int(dimensions[1] * scale)
        
        # Create canvas with existing elements as initial data
        initial_drawing = {
            "version": "4.4.0",
            "objects": []
        }
        
        for elem in st.session_state.canvas_elements:
            initial_drawing["objects"].append({
                "type": "rect",
                "version": "4.4.0",
                "left": elem["x"] * scale,
                "top": elem["y"] * scale,
                "width": elem["width"] * scale,
                "height": elem["height"] * scale,
                "fill": "rgba(100, 100, 100, 0.3)",
                "stroke": "#ffffff",
                "strokeWidth": 2
            })
        
        # Drawable canvas
        canvas_result = st_canvas(
            fill_color="rgba(100, 100, 100, 0.3)",
            stroke_width=2,
            stroke_color="#ffffff",
            background_color="#2a2a2a",
            height=display_height,
            width=display_width,
            drawing_mode=drawing_mode,
            initial_drawing=initial_drawing,
            key="canvas",
        )
        
        st.caption(f"Canvas: {dimensions[0]}x{dimensions[1]}px (scaled to {display_width}px for display)")
        
        # Update elements from canvas - only on count change to avoid MediaFileStorageError
        if canvas_result.json_data is not None:
            canvas_objects = canvas_result.json_data.get("objects", [])
            
            # Only auto-update when element count changes (new element added/removed)
            # For position updates, user must click "Update Elements" button
            if len(canvas_objects) != len(st.session_state.canvas_elements):
                updated_elements = []
                
                for i, obj in enumerate(canvas_objects):
                    if obj["type"] == "rect":
                        x = int(obj["left"] / scale)
                        y = int(obj["top"] / scale)
                        width = int(obj["width"] / scale)
                        height = int(obj["height"] / scale)
                        
                        if i < len(st.session_state.canvas_elements):
                            original = st.session_state.canvas_elements[i]
                            updated_elements.append({
                                "label": original.get("label", "[CUSTOM]"),
                                "type": original.get("type", "custom"),
                                "x": x,
                                "y": y,
                                "width": width,
                                "height": height
                            })
                        else:
                            updated_elements.append({
                                "label": "[CUSTOM]",
                                "type": "custom",
                                "x": x,
                                "y": y,
                                "width": width,
                                "height": height
                            })
                
                st.session_state.canvas_elements = updated_elements
        
        # Manual update button for position changes
        col_refresh1, col_refresh2 = st.columns(2)
        with col_refresh1:
            if st.button("🔄 Update Positions", width='stretch'):
                # Update positions from canvas
                if canvas_result.json_data is not None:
                    canvas_objects = canvas_result.json_data.get("objects", [])
                    updated_elements = []
                    
                    for i, obj in enumerate(canvas_objects):
                        if obj["type"] == "rect":
                            x = int(obj["left"] / scale)
                            y = int(obj["top"] / scale)
                            width = int(obj["width"] / scale)
                            height = int(obj["height"] / scale)
                            
                            if i < len(st.session_state.canvas_elements):
                                original = st.session_state.canvas_elements[i]
                                updated_elements.append({
                                    "label": original.get("label", "[CUSTOM]"),
                                    "type": original.get("type", "custom"),
                                    "x": x,
                                    "y": y,
                                    "width": width,
                                    "height": height
                                })
                    
                    st.session_state.canvas_elements = updated_elements
                st.rerun()
        
        with col_refresh2:
            if st.button("🔄 Refresh Preview", width='stretch'):
                st.rerun()
        
        # Create reference image from canvas elements
        reference_img = create_reference_from_elements(
            st.session_state.canvas_elements,
            dimensions
        )
        
        st.subheader("📸 Reference Preview")
        st.image(reference_img, caption="AI will use this layout", width='stretch')
        
        # Download reference
        buf = io.BytesIO()
        reference_img.save(buf, format='PNG')
        st.download_button(
            "💾 Download Reference",
            data=buf.getvalue(),
            file_name="layout_reference.png",
            mime="image/png",
            width='stretch'
        )
    
    # Generation section
    st.markdown("---")
    st.header("🚀 Generate Advertisement")
    
    if not st.session_state.canvas_elements:
        st.warning("⚠️ Add some elements to the canvas first!")
        return
    
    if st.button("🎨 Generate with This Layout", type="primary", width='stretch'):
        # Validation
        if not any(content_mapping.values()):
            st.error("❌ Please fill in at least one content field")
            return
        
        # Start generation
        with st.status("🎨 Generating...", expanded=True) as status:
            try:
                st.write("📐 Creating reference image...")
                reference_img = create_reference_from_elements(
                    st.session_state.canvas_elements,
                    dimensions
                )
                
                st.write("📝 Building prompt...")
                mapping = get_placeholder_replacement_map(
                    logo_space=include_logo,
                    brand_name=brand_name,
                    main_message=main_message,
                    tagline=tagline,
                    cta_text=cta_text
                )
                
                if not scene_description:
                    scene_description = get_scene_style_guidance(style, color_scheme)
                
                prompt = get_visual_layout_prompt(
                    elements_mapping=mapping,
                    scene_description=scene_description,
                    style=style,
                    color_scheme=color_scheme,
                    dimensions=dimensions
                )
                
                st.write(f"🤖 Initializing {model}...")
                generator = AIImageGenerator(model)
                
                st.write("🎨 Generating image...")
                
                if "Nano Banana Pro" in model:
                    from utils.ai_generator import NanoBananaProFeatures
                    generated_image = NanoBananaProFeatures.generate_with_references(
                        generator=generator,
                        prompt=prompt,
                        size=dimensions,
                        reference_images=[reference_img],
                        use_search_grounding=False,
                        text_rendering_mode=True
                    )
                else:
                    generated_image = generator.generate_image(prompt=prompt, size=dimensions)
                
                if generated_image:
                    if logo and include_logo:
                        st.write("🏷️ Applying logo...")
                        from utils.image_processor import ImageProcessor
                        logo_img = ImageProcessor.process_logo(logo)
                        if logo_img:
                            # Find logo element position
                            logo_elem = next((e for e in st.session_state.canvas_elements if e["type"] == "logo"), None)
                            if logo_elem:
                                logo_img = logo_img.resize((logo_elem["width"], logo_elem["height"]), Image.Resampling.LANCZOS)
                                generated_image.paste(logo_img, (logo_elem["x"], logo_elem["y"]), logo_img if logo_img.mode == 'RGBA' else None)
                    
                    status.update(label="✅ Complete!", state="complete")
                    st.success("✨ Generated successfully!")
                    
                    st.image(generated_image, caption="Generated Advertisement", width='stretch')
                    
                    st.session_state.generated_ad = generated_image
                    st.session_state.generation_params = {
                        "method": "visual_layout_interactive",
                        "model": model,
                        "dimensions": dimensions,
                        "elements_count": len(st.session_state.canvas_elements),
                        "brand_name": brand_name,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    buf = io.BytesIO()
                    generated_image.save(buf, format='PNG')
                    st.download_button(
                        "💾 Download Image",
                        data=buf.getvalue(),
                        file_name=f"{brand_name.replace(' ', '_') if brand_name else 'ad'}_layout.png",
                        mime="image/png",
                        width='stretch'
                    )
                else:
                    status.update(label="❌ Failed", state="error")
                    st.error("❌ Generation failed")
                    
            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"❌ Error: {str(e)}")


def create_reference_from_elements(elements, dimensions):
    """Create reference image from canvas elements"""
    img = Image.new('RGB', dimensions, color='#2a2a2a')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 80)
        font_medium = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        font_large = font_medium = font_small = ImageFont.load_default()
    
    for elem in elements:
        x, y, w, h = elem["x"], elem["y"], elem["width"], elem["height"]
        label = elem.get("label", "[ELEMENT]")
        
        # Draw box
        draw.rectangle([x, y, x + w, y + h], outline='white', width=3)
        
        # Select font
        if elem.get("type") == "message":
            font = font_large
        elif elem.get("type") in ["brand", "tagline"]:
            font = font_medium
        else:
            font = font_small
        
        # Draw label
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = x + (w - text_w) // 2
        text_y = y + (h - text_h) // 2
        draw.text((text_x, text_y), label, fill='white', font=font)
    
    return img
    
    # Header
    st.title("🎨 Visual Layout Generator")
    st.markdown("Create ads by designing the layout visually - AI follows your composition exactly")
    
    # Close button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("❌ Close", key="close_visual_layout"):
            st.session_state.show_visual_layout = False
            # Clear canvas elements to prevent stale image references
            if 'canvas_elements' in st.session_state:
                st.session_state.canvas_elements = []
            st.rerun()
    
    st.markdown("---")
    
    # Info box
    with st.expander("ℹ️ How This Works", expanded=False):
        st.markdown("""
        **Visual Layout Method:**
        1. Choose which elements to include (logo, brand name, message, etc.)
        2. Select a layout style or customize positions
        3. System generates a reference image with placeholders
        4. AI uses this reference to create your ad with exact positioning
        
        **Benefits:**
        - ✅ Precise control over element positions
        - ✅ No abstract JSON templates
        - ✅ Visual feedback before generation
        - ✅ Better positioning accuracy
        
        **Note:** This method works best with Nano Banana Pro model (Google Gemini)
        """)
    
    # Two column layout: Controls | Preview
    controls_col, preview_col = st.columns([1, 2])
    
    with controls_col:
        st.header("⚙️ Layout Configuration")
        
        # Model selection (Nano Banana Pro recommended)
        st.subheader("1. Model")
        model = st.selectbox(
            "AI Model",
            ["🍌⭐ Nano Banana Pro", "🍌 Nano Banana", "🎨 DALL-E 3"],
            help="Nano Banana Pro recommended for best results"
        )
        
        if "Nano Banana" not in model:
            st.warning("⚠️ Visual Layout method works best with Nano Banana Pro")
        
        # Dimensions
        st.subheader("2. Dimensions")
        dimension_presets = {
            "Instagram Post (1080x1080)": (1080, 1080),
            "Facebook Post (1200x630)": (1200, 630),
            "Instagram Story (1080x1920)": (1080, 1920),
            "Twitter Post (1200x675)": (1200, 675),
            "LinkedIn Post (1200x627)": (1200, 627),
            "Custom": None
        }
        
        dim_choice = st.selectbox("Size Preset", list(dimension_presets.keys()))
        
        if dim_choice == "Custom":
            col_w, col_h = st.columns(2)
            with col_w:
                width = st.number_input("Width", 800, 3840, 1920, 10)
            with col_h:
                height = st.number_input("Height", 600, 2160, 1080, 10)
            dimensions = (width, height)
        else:
            dimensions = dimension_presets[dim_choice]
        
        # Content inputs
        st.subheader("3. Content")
        
        include_logo = st.checkbox("Include Logo Space", value=True)
        logo = None
        if include_logo:
            logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
            if logo_file is not None:
                try:
                    logo = Image.open(logo_file)
                except Exception as e:
                    st.error(f"Error loading logo: {e}")
                    logo = None
        else:
            logo = None
        
        include_brand = st.checkbox("Include Brand Name", value=True)
        brand_name = ""
        if include_brand:
            brand_name = st.text_input("Brand Name", placeholder="e.g., Mosaic")
        
        include_message = st.checkbox("Include Main Message", value=True)
        main_message = ""
        if include_message:
            main_message = st.text_input("Main Message", placeholder="e.g., Premium Living Spaces")
        
        include_tagline = st.checkbox("Include Tagline", value=False)
        tagline = ""
        if include_tagline:
            tagline = st.text_input("Tagline", placeholder="e.g., Real life. Real possibilities")
        
        include_cta = st.checkbox("Include Call-to-Action", value=True)
        cta_text = ""
        if include_cta:
            cta_text = st.text_input("CTA Text", placeholder="e.g., Visit Us")
        
        # Layout style
        st.subheader("4. Layout Style")
        layout_style = st.selectbox(
            "Composition",
            ["centered", "left-aligned", "asymmetric"],
            format_func=lambda x: x.replace("-", " ").title()
        )
        
        # Scene style
        st.subheader("5. Scene Style")
        style = st.selectbox(
            "Visual Style",
            ["Modern & Minimalist", "Modern", "Luxury", "Professional", "Creative"]
        )
        
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Brand Colors", "Monochrome", "Warm Tones", "Cool Tones", "Vibrant"]
        )
        
        scene_description = st.text_area(
            "Scene Description (optional)",
            placeholder="Describe the environment you want...",
            help="Leave empty for default modern interior"
        )
    
    with preview_col:
        st.header("👁️ Layout Preview")
        
        # Generate reference image preview
        reference_img = SimpleLayoutBuilder.create_layout(
            dimensions=dimensions,
            include_logo=include_logo,
            include_brand=include_brand,
            include_message=include_message,
            include_tagline=include_tagline,
            include_cta=include_cta,
            layout_style=layout_style
        )
        
        # Use unique key to prevent MediaFileStorageError on rerun
        st.image(reference_img, caption="Reference Layout - AI will use this composition", width='stretch', key=f"ref_quick_{int(time.time() * 1000)}")
        
        # Download reference button
        buf = io.BytesIO()
        reference_img.save(buf, format='PNG')
        st.download_button(
            "💾 Download Reference Image",
            data=buf.getvalue(),
            file_name="reference_layout.png",
            mime="image/png"
        )
        
        st.info("ℹ️ This reference shows where elements will appear in the final generated image")
    
    # Generation section
    st.markdown("---")
    st.header("🚀 Generate Advertisement")
    
    # Show what will be generated
    with st.expander("📋 Generation Summary", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Elements:**")
            if include_logo:
                st.markdown("- ✅ Logo space")
            if include_brand and brand_name:
                st.markdown(f"- ✅ Brand: {brand_name}")
            if include_message and main_message:
                st.markdown(f"- ✅ Message: {main_message}")
            if include_tagline and tagline:
                st.markdown(f"- ✅ Tagline: {tagline}")
            if include_cta and cta_text:
                st.markdown(f"- ✅ CTA: {cta_text}")
        
        with col2:
            st.markdown("**Settings:**")
            st.markdown(f"- Model: {model}")
            st.markdown(f"- Size: {dimensions[0]}x{dimensions[1]}")
            st.markdown(f"- Style: {style}")
            st.markdown(f"- Layout: {layout_style.replace('-', ' ').title()}")
    
    # Generate button
    if st.button("🎨 Generate with Visual Layout", type="primary", width='stretch'):
        # Validation
        if include_brand and not brand_name:
            st.error("❌ Please enter a brand name")
            return
        if include_message and not main_message:
            st.error("❌ Please enter a main message")
            return
        
        # Start generation
        with st.status("🎨 Generating with Visual Layout Method...", expanded=True) as status:
            try:
                # Step 1: Create reference image
                st.write("📐 Creating reference image...")
                reference_img = SimpleLayoutBuilder.create_layout(
                    dimensions=dimensions,
                    include_logo=include_logo,
                    include_brand=include_brand,
                    include_message=include_message,
                    include_tagline=include_tagline,
                    include_cta=include_cta,
                    layout_style=layout_style
                )
                
                # Step 2: Build prompt
                st.write("📝 Building AI prompt...")
                
                # Get placeholder mapping
                mapping = get_placeholder_replacement_map(
                    logo_space=include_logo,
                    brand_name=brand_name,
                    main_message=main_message,
                    tagline=tagline,
                    cta_text=cta_text
                )
                
                # Get scene description
                if not scene_description:
                    scene_description = get_scene_style_guidance(style, color_scheme)
                
                # Generate full prompt
                prompt = get_visual_layout_prompt(
                    elements_mapping=mapping,
                    scene_description=scene_description,
                    style=style,
                    color_scheme=color_scheme,
                    dimensions=dimensions
                )
                
                # Show prompt in expander
                with st.expander("🔍 Generated Prompt", expanded=False):
                    st.text_area("Full prompt:", prompt, height=300)
                
                # Step 3: Initialize AI generator
                st.write(f"🤖 Initializing {model}...")
                generator = AIImageGenerator(model)
                
                # Step 4: Generate image
                st.write("🎨 Generating image...")
                
                # Check if Nano Banana Pro for multi-modal
                if "Nano Banana Pro" in model:
                    from utils.ai_generator import NanoBananaProFeatures
                    
                    # Use reference image as input
                    reference_images = [reference_img]
                    
                    generated_image = NanoBananaProFeatures.generate_with_references(
                        generator=generator,
                        prompt=prompt,
                        size=dimensions,
                        reference_images=reference_images,
                        use_search_grounding=False,
                        text_rendering_mode=True
                    )
                else:
                    # For other models, just use prompt (no reference support)
                    generated_image = generator.generate_image(
                        prompt=prompt,
                        size=dimensions
                    )
                
                if generated_image:
                    # Apply logo if provided
                    if logo and include_logo:
                        st.write("🏷️ Applying logo...")
                        from utils.image_processor import ImageProcessor
                        logo_img = ImageProcessor.process_logo(logo)
                        if logo_img:
                            # Simple logo overlay in top-left
                            logo_img = logo_img.resize((200, 120), Image.Resampling.LANCZOS)
                            generated_image.paste(logo_img, (100, 80), logo_img if logo_img.mode == 'RGBA' else None)
                    
                    # Success!
                    status.update(label="✅ Generation Complete!", state="complete")
                    
                    st.success("✨ Advertisement generated successfully!")
                    
                    st.image(generated_image, caption="Generated Advertisement", width='stretch')
                    
                    # Save to session state
                    st.session_state.generated_ad = generated_image
                    st.session_state.generation_params = {
                        "method": "visual_layout",
                        "model": model,
                        "dimensions": dimensions,
                        "layout_style": layout_style,
                        "brand_name": brand_name,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Download button
                    buf = io.BytesIO()
                    generated_image.save(buf, format='PNG')
                    st.download_button(
                        "💾 Download Image",
                        data=buf.getvalue(),
                        file_name=f"{brand_name.replace(' ', '_') if brand_name else 'ad'}_visual_layout.png",
                        mime="image/png",
                        width='stretch'
                    )
                else:
                    status.update(label="❌ Generation Failed", state="error")
                    st.error("❌ Image generation failed. Please check your API configuration.")
                    
            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"❌ Error during generation: {str(e)}")
