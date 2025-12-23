"""
Visual Layout Generator Interface
Streamlit UI for the visual layout method with drag-and-drop canvas
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import time
import json
import numpy as np
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
            # Reset canvas key
            st.session_state.canvas_key = 0
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
    
    # Initialize canvas key to prevent MediaFileStorageError
    if 'canvas_key' not in st.session_state:
        st.session_state.canvas_key = 0
    
    # Flag to control canvas rendering after state changes
    if 'update_canvas' not in st.session_state:
        st.session_state.update_canvas = False
    
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
        - � Draw rectangles, circles, lines, or polygons for custom elements
        - ↔️ Use transform mode to move/resize existing elements
        - 🗑️ Select and delete unwanted elements from the list below
        - 🔄 Click 'Sync Elements' to capture drawn shapes
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
        tool_options = {
            "rect": "📦 Rectangle",
            "circle": "⭕ Circle",
            "line": "📏 Line",
            "polygon": "🔶 Polygon",
            "transform": "↔️ Transform"
        }
        drawing_mode = st.radio(
            "Tool Mode",
            list(tool_options.keys()),
            format_func=lambda x: tool_options[x],
            horizontal=False
        )
        
        if drawing_mode == "polygon":
            st.caption("💡 Click to add points, double-click to complete")
        
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
                        "height": props["h"],
                        "shape": "rect"
                    }
                    st.session_state.canvas_elements.append(new_elem)
                    st.session_state.canvas_key += 1
                    st.session_state.update_canvas = True
                    st.rerun()
        
        # Clear all button
        if st.button("🗑️ Clear All Elements", width='stretch'):
            st.session_state.canvas_elements = []
            st.session_state.canvas_key += 1
            st.session_state.update_canvas = True
            st.rerun()
        
        # Element list and delete
        if st.session_state.canvas_elements:
            st.subheader("5. Current Elements")
            for idx, elem in enumerate(st.session_state.canvas_elements):
                with st.container():
                    col_label, col_pos, col_del = st.columns([2, 2, 1])
                    with col_label:
                        # Allow editing custom element labels
                        if elem.get('type') == 'custom':
                            new_label = st.text_input(
                                "Name",
                                value=elem['label'],
                                key=f"label_{idx}",
                                label_visibility="collapsed",
                                placeholder="Element name"
                            )
                            if new_label != elem['label']:
                                st.session_state.canvas_elements[idx]['label'] = new_label
                        else:
                            st.caption(elem['label'])
                    with col_pos:
                        st.caption(f"({elem['x']}, {elem['y']})")
                    with col_del:
                        if st.button("❌", key=f"del_{idx}_{elem['label']}"):
                            st.session_state.canvas_elements.pop(idx)
                            st.session_state.canvas_key += 1
                            st.session_state.update_canvas = True
                            st.rerun()
                    st.divider()
        
        # Dynamic Content Mapping based on canvas elements
        st.subheader("6. Content Mapping")
        
        if st.session_state.canvas_elements:
            st.caption("Map content to your canvas elements:")
            
            content_mapping = {}
            logo = None
            
            # Group elements by type for better organization
            for idx, elem in enumerate(st.session_state.canvas_elements):
                elem_label = elem['label']
                elem_type = elem.get('type', 'custom')
                
                # Logo upload for logo elements
                if elem_type == 'logo' or 'LOGO' in elem_label.upper():
                    logo_file = st.file_uploader(
                        f"📷 Upload for: {elem_label}",
                        type=['png', 'jpg', 'jpeg'],
                        key=f"logo_upload_{idx}"
                    )
                    if logo_file is not None:
                        try:
                            logo = Image.open(logo_file)
                            content_mapping[elem_label] = "logo_uploaded"
                        except Exception as e:
                            st.error(f"Error loading logo: {e}")
                            logo = None
                    else:
                        content_mapping[elem_label] = "logo_space"
                
                # Text input for text-based elements
                elif elem_type in ['brand', 'message', 'tagline', 'cta', 'custom']:
                    placeholder_text = {
                        'brand': 'e.g., Mosaic',
                        'message': 'e.g., Premium Living Spaces',
                        'tagline': 'e.g., Real life. Real possibilities',
                        'cta': 'e.g., Visit Us',
                        'custom': 'Enter text content...'
                    }
                    
                    text_value = st.text_input(
                        f"✏️ Content for: {elem_label}",
                        placeholder=placeholder_text.get(elem_type, 'Enter content...'),
                        key=f"content_{idx}"
                    )
                    
                    if text_value:
                        content_mapping[elem_label] = text_value
                    else:
                        content_mapping[elem_label] = elem_label  # Use label as placeholder
        else:
            st.info("Add elements to the canvas first")
            content_mapping = {}
            logo = None
        
        # Always show custom instructions
        st.subheader("7. Custom Instructions")
        custom_instructions = st.text_area(
            "Additional Prompt Instructions",
            placeholder="Add any specific instructions for the AI (e.g., 'Use warm sunset colors', 'Include mountains in background', etc.)",
            height=120,
            help="These instructions will be added to the AI prompt along with the layout information"
        )
        
        # Scene style (simplified)
        st.subheader("8. Style Settings")
        style = st.selectbox(
            "Visual Style",
            ["Modern & Minimalist", "Modern", "Luxury", "Professional", "Creative"]
        )
        
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Brand Colors", "Monochrome", "Warm Tones", "Cool Tones", "Vibrant"]
        )
    
    with canvas_col:
        st.header("🖼️ Interactive Canvas")
        
        # Scale canvas for display
        display_width = 800
        scale = display_width / dimensions[0]
        display_height = int(dimensions[1] * scale)
        
        # Use placeholder to avoid rendering canvas during state transitions
        canvas_placeholder = st.empty()
        
        # Only render canvas if not in the middle of an update
        if st.session_state.update_canvas:
            # Show loading message instead of canvas
            with canvas_placeholder.container():
                st.info("🔄 Updating canvas...")
                st.session_state.update_canvas = False
                st.rerun()
        
        # Create canvas with existing elements as initial data
        initial_drawing = {
            "version": "4.4.0",
            "objects": []
        }
        
        for elem in st.session_state.canvas_elements:
            shape = elem.get("shape", "rect")
            
            if shape in ["rect", "circle", "ellipse"]:
                initial_drawing["objects"].append({
                    "type": shape,
                    "version": "4.4.0",
                    "left": elem["x"] * scale,
                    "top": elem["y"] * scale,
                    "width": elem["width"] * scale,
                    "height": elem["height"] * scale,
                    "fill": "rgba(100, 100, 100, 0.3)",
                    "stroke": "#ffffff",
                    "strokeWidth": 2
                })
            elif shape == "line":
                initial_drawing["objects"].append({
                    "type": "line",
                    "version": "4.4.0",
                    "x1": elem["x"] * scale,
                    "y1": elem["y"] * scale,
                    "x2": (elem["x"] + elem["width"]) * scale,
                    "y2": (elem["y"] + elem["height"]) * scale,
                    "stroke": "#ffffff",
                    "strokeWidth": 2
                })
        
        # Drawable canvas with unique key to prevent MediaFileStorageError
        with canvas_placeholder.container():
            canvas_result = st_canvas(
                fill_color="rgba(100, 100, 100, 0.3)",
                stroke_width=2,
                stroke_color="#ffffff",
                background_color="#2a2a2a",
                height=display_height,
                width=display_width,
                drawing_mode=drawing_mode,
                initial_drawing=initial_drawing,
                key=f"canvas_{st.session_state.canvas_key}",
            )
        
        st.caption(f"Canvas: {dimensions[0]}x{dimensions[1]}px (scaled to {display_width}px for display)")
        st.caption("💡 Tip: Draw rectangles on canvas, then click 'Sync Elements' to capture them")
        
        # Manual sync button to capture canvas elements
        col_sync, col_refresh = st.columns(2)
        with col_sync:
            if st.button("🔄 Sync Elements", width='stretch', help="Capture all rectangles from canvas"):
                # Sync all elements from canvas
                if canvas_result.json_data is not None:
                    canvas_objects = canvas_result.json_data.get("objects", [])
                    updated_elements = []
                    
                    for i, obj in enumerate(canvas_objects):
                        obj_type = obj.get("type")
                        
                        if obj_type in ["rect", "circle", "ellipse"]:
                            # Handle transform scaling
                            scaleX = obj.get("scaleX", 1)
                            scaleY = obj.get("scaleY", 1)
                            
                            x = int(obj.get("left", 0) / scale)
                            y = int(obj.get("top", 0) / scale)
                            width = int(obj.get("width", 100) * scaleX / scale)
                            height = int(obj.get("height", 100) * scaleY / scale)
                            shape = obj_type
                        elif obj_type == "line":
                            x1 = int(obj.get("x1", 0) / scale)
                            y1 = int(obj.get("y1", 0) / scale)
                            x2 = int(obj.get("x2", 100) / scale)
                            y2 = int(obj.get("y2", 100) / scale)
                            x = min(x1, x2)
                            y = min(y1, y2)
                            width = abs(x2 - x1)
                            height = abs(y2 - y1)
                            shape = "line"
                        elif obj_type == "path":  # polygon
                            # Get bounding box of polygon
                            path = obj.get("path", [])
                            if path:
                                xs = [int(p[1] / scale) for p in path if len(p) > 1]
                                ys = [int(p[2] / scale) for p in path if len(p) > 2]
                                if xs and ys:
                                    x = min(xs)
                                    y = min(ys)
                                    width = max(xs) - x
                                    height = max(ys) - y
                                    shape = "polygon"
                                else:
                                    continue
                            else:
                                continue
                        else:
                            continue
                        
                        # Preserve label if element already exists
                        if i < len(st.session_state.canvas_elements):
                            original = st.session_state.canvas_elements[i]
                            label = original.get("label", "[CUSTOM]")
                            elem_type = original.get("type", "custom")
                        else:
                            # New custom element with shape indicator
                            shape_emoji = {"rect": "📦", "circle": "⭕", "ellipse": "⭕", "line": "📏", "polygon": "🔶"}
                            label = f"{shape_emoji.get(shape, '📐')} CUSTOM {i+1}"
                            elem_type = "custom"
                        
                        updated_elements.append({
                            "label": label,
                            "type": elem_type,
                            "shape": shape,
                            "x": x,
                            "y": y,
                            "width": width,
                            "height": height
                        })
                    
                    st.session_state.canvas_elements = updated_elements
                    st.session_state.canvas_key += 1
                    st.session_state.update_canvas = True
                st.rerun()
        
        with col_refresh:
            if st.button("🔄 Clear Canvas", width='stretch', help="Reset canvas view"):
                st.session_state.canvas_key += 1
                st.session_state.update_canvas = True
                st.rerun()
        
        # Create and display reference image (only when not updating)
        if not st.session_state.update_canvas:
            # Create reference image from canvas elements
            if st.session_state.canvas_elements:
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
            else:
                st.subheader("📸 Reference Preview")
                st.info("Add elements to see preview")
    
    # Generation section
    st.markdown("---")
    st.header("🚀 Generate Advertisement")
    
    if not st.session_state.canvas_elements:
        st.warning("⚠️ Add some elements to the canvas first!")
        return
    
    if st.button("🎨 Generate with This Layout", type="primary", width='stretch'):
        # Validation
        if not content_mapping:
            st.error("❌ Please add elements and provide content mapping")
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
                
                # Detect scene type from custom instructions or style
                scene_text = (custom_instructions or "").lower()
                is_nature_scene = any(keyword in scene_text for keyword in 
                    ['nature', 'outdoor', 'forest', 'safari', 'wildlife', 'landscape', 'beach', 'mountain', 'garden', 'park', 'tree', 'animal'])
                is_architectural_scene = any(keyword in scene_text for keyword in 
                    ['interior', 'room', 'building', 'architectural', 'office', 'lobby', 'wall', 'floor', 'concrete', 'glass'])
                
                # Build dynamic prompt based on canvas elements and custom instructions
                prompt_parts = []
                
                # Use custom instructions if provided, otherwise fall back to style descriptions
                if custom_instructions:
                    # User provided custom instructions - use those as the main creative direction
                    prompt_parts.append(custom_instructions)
                else:
                    # No custom instructions - use default style guidance as fallback
                    scene_guidance = get_scene_style_guidance(style, color_scheme)
                    prompt_parts.append(scene_guidance)
                
                # Add layout description in natural language
                prompt_parts.append(f"\nIMPORTANT: A reference image is provided showing exact text positions with placeholder labels in [BRACKETS]. Use this reference to determine the PRECISE location and scale of each text element.")
                prompt_parts.append(f"\nCreate a professional {dimensions[0]}x{dimensions[1]}px advertisement as a SINGLE UNIFIED SCENE (do not divide into sections or quadrants). Place text elements at the EXACT positions shown in the reference image:")
                
                # Build natural layout description
                layout_descriptions = []
                for idx, elem in enumerate(st.session_state.canvas_elements, 1):
                    elem_label = elem['label']
                    content = content_mapping.get(elem_label, elem_label)
                    x, y, w, h = elem['x'], elem['y'], elem['width'], elem['height']
                    
                    # Determine position description
                    h_pos = "left" if x < dimensions[0] / 3 else ("center" if x < 2 * dimensions[0] / 3 else "right")
                    v_pos = "top" if y < dimensions[1] / 3 else ("middle" if y < 2 * dimensions[1] / 3 else "bottom")
                    position_desc = f"in the {v_pos}-{h_pos} area"
                    
                    if 'LOGO' in elem_label.upper() or elem.get('type') == 'logo':
                        # Use positive "negative space" framing instead of NO/NO/NO
                        layout_descriptions.append(f"- {position_desc}: This area is clean, empty negative space where the natural background scene continues seamlessly - reserve this as an open area for logo overlay (the actual company logo will be added separately after generation)")
                    elif 'CTA' in elem_label.upper() or 'call' in elem_label.lower() or 'button' in elem_label.lower():
                        # CTA button with shadow for scene unity
                        if is_architectural_scene:
                            layout_descriptions.append(f"- Place a clean button with the text '{content}' {position_desc} - render as a dimensional UI element integrated into the scene with a soft shadow on the floor/surface beneath it")
                        else:
                            layout_descriptions.append(f"- Place a simple, clean button with the text '{content}' {position_desc} - use a soft-edged button that blends naturally with the scene, with a subtle shadow grounding it in the environment")
                    else:
                        # Regular text - scene-aware implementation
                        if is_architectural_scene:
                            # Physical text for architecture
                            layout_descriptions.append(f"- Render the text '{content}' {position_desc} as physical typography integrated into the architectural space (such as brushed-metal letters, glass-morphism lettering, or dimensional signage) with realistic shadows on the surface below, creating a unified scene where text exists as a real architectural element")
                        elif is_nature_scene:
                            # Clean overlay for nature
                            layout_descriptions.append(f"- Render the text '{content}' directly on the scene {position_desc} without any background box - use clean, elegant typography with a subtle drop shadow that grounds the text in the natural environment, ensuring it feels painted into the scene rather than floating on top")
                        else:
                            # Default: clean overlay
                            layout_descriptions.append(f"- Render the text '{content}' directly on the scene {position_desc} without any background box or container - use clean typography with natural contrast and a subtle shadow for depth")
                
                prompt_parts.extend(layout_descriptions)
                
                # Add style and quality requirements
                prompt_parts.append(f"\nStyle: {style}")
                prompt_parts.append(f"Color palette: {color_scheme}")
                prompt_parts.append(f"\nCRITICAL REQUIREMENTS:")
                prompt_parts.append(f"- Use the reference image to match EXACT text positions, sizes, and alignment shown by the placeholder labels")
                prompt_parts.append(f"- Each text element should appear in the same location as its corresponding [PLACEHOLDER] in the reference")
                prompt_parts.append(f"- Create ONE continuous, unified scene - DO NOT divide the image into sections, quadrants, or panels with lines")
                prompt_parts.append(f"- The entire image should be a seamless photographic scene with text overlaid at specified positions")
                prompt_parts.append(f"- NO horizontal or vertical dividing lines separating the image into blocks")
                prompt_parts.append(f"- Render all text directly on the unified scene without background boxes or containers")
                prompt_parts.append(f"- Only the CTA button should have a button shape")
                prompt_parts.append(f"- Use natural color contrast and subtle drop shadows for text readability")
                
                prompt = "\n".join(prompt_parts)
                
                # Store for later display
                generation_prompt = prompt
                generation_model = model
                
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
                    if logo:
                        st.write("🏷️ Applying logo...")
                        from utils.image_processor import ImageProcessor
                        logo_img = ImageProcessor.process_logo(logo)
                        if logo_img:
                            # Find logo element position
                            logo_elem = next((e for e in st.session_state.canvas_elements 
                                            if e.get("type") == "logo" or "LOGO" in e.get("label", "").upper()), None)
                            if logo_elem:
                                # Resize logo to fit the designated area
                                logo_img = logo_img.resize((logo_elem["width"], logo_elem["height"]), Image.Resampling.LANCZOS)
                                
                                # Ensure logo has alpha channel
                                if logo_img.mode != 'RGBA':
                                    logo_img = logo_img.convert('RGBA')
                                
                                # Remove white/light backgrounds from logo
                                logo_array = np.array(logo_img)
                                
                                # Create mask for white/near-white pixels (R>240, G>240, B>240)
                                white_mask = (logo_array[:, :, 0] > 240) & (logo_array[:, :, 1] > 240) & (logo_array[:, :, 2] > 240)
                                
                                # Set alpha to 0 for white pixels
                                logo_array[white_mask, 3] = 0
                                
                                # Convert back to PIL Image
                                logo_img = Image.fromarray(logo_array, 'RGBA')
                                
                                # Paste logo onto generated image using alpha as mask
                                if generated_image.mode != 'RGBA':
                                    generated_image = generated_image.convert('RGBA')
                                
                                generated_image.paste(logo_img, (logo_elem["x"], logo_elem["y"]), logo_img)
                                
                                # Convert back to RGB for final output
                                generated_image = generated_image.convert('RGB')
                    
                    status.update(label="✅ Complete!", state="complete")
                    st.success("✨ Generated successfully!")
                    
                    # Store in session state first
                    st.session_state.generated_ad = generated_image
                    
                    # Extract brand name from content mapping if available
                    brand_name = next((v for k, v in content_mapping.items() 
                                      if 'BRAND' in k.upper() and v != k), "advertisement")
                    
                    st.session_state.generation_params = {
                        "method": "visual_layout_interactive",
                        "model": generation_model,
                        "dimensions": dimensions,
                        "elements_count": len(st.session_state.canvas_elements),
                        "content_mapping": content_mapping,
                        "custom_instructions": custom_instructions,
                        "full_prompt": generation_prompt,
                        "style": style,
                        "color_scheme": color_scheme,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"❌ Error: {str(e)}")
    
    # Persistent generated advertisement section (outside the generation button)
    if 'generated_ad' in st.session_state and st.session_state.generated_ad:
        st.markdown("---")
        st.header("🎨 Generated Advertisement")
        
        st.image(st.session_state.generated_ad, caption="Generated Advertisement", width='stretch')
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download button
            buf = io.BytesIO()
            st.session_state.generated_ad.save(buf, format='PNG')
            params = st.session_state.generation_params
            brand_name = next((v for k, v in params.get("content_mapping", {}).items() 
                              if 'BRAND' in k.upper() and v != k), "advertisement")
            filename_base = brand_name.replace(' ', '_') if brand_name and brand_name != "advertisement" else 'ad'
            
            st.download_button(
                "💾 Download Image",
                data=buf.getvalue(),
                file_name=f"{filename_base}_layout.png",
                mime="image/png",
                width='stretch'
            )
        
        with col2:
            # Edit by prompt button
            if st.button("✏️ Edit by Prompt", width='stretch', help="Modify image using AI"):
                st.session_state.edit_by_prompt_mode = not st.session_state.get('edit_by_prompt_mode', False)
                st.rerun()
        
        with col3:
            # Clear/Reset button
            if st.button("🗑️ Clear Result", width='stretch'):
                del st.session_state.generated_ad
                if 'generation_params' in st.session_state:
                    del st.session_state.generation_params
                if 'edit_by_prompt_mode' in st.session_state:
                    st.session_state.edit_by_prompt_mode = False
                st.rerun()
        
        # Edit by prompt interface
        if st.session_state.get('edit_by_prompt_mode', False):
            st.markdown("---")
            st.subheader("✏️ Edit Image by Prompt")
            st.info("💡 Describe how you want to modify the current image. The AI will use your generated image as reference.")
            
            edit_prompt = st.text_area(
                "Modification Instructions:",
                height=100,
                placeholder="Example: Make the background warmer, Add more plants, Change lighting to sunset, etc.",
                help="Describe the specific changes you want to make",
                key="visual_layout_edit_prompt"
            )
            
            col_edit1, col_edit2 = st.columns([1, 1])
            with col_edit1:
                if st.button("🚀 Apply Changes", type="primary", width='stretch'):
                    if edit_prompt.strip():
                        with st.status("🎨 Applying modifications...", expanded=True) as edit_status:
                            try:
                                params = st.session_state.generation_params
                                
                                st.write("📝 Building edit prompt...")
                                full_edit_prompt = f"{params.get('full_prompt', '')}\n\nModifications: {edit_prompt}"
                                
                                st.write(f"🤖 Initializing {params['model']}...")
                                generator = AIImageGenerator(params['model'])
                                
                                st.write("🎨 Generating modified image...")
                                
                                if "Nano Banana Pro" in params['model']:
                                    from utils.ai_generator import NanoBananaProFeatures
                                    modified_image = NanoBananaProFeatures.generate_with_references(
                                        generator=generator,
                                        prompt=full_edit_prompt,
                                        size=params['dimensions'],
                                        reference_images=[st.session_state.generated_ad],
                                        use_search_grounding=False,
                                        text_rendering_mode=True
                                    )
                                else:
                                    modified_image = generator.generate_image(prompt=full_edit_prompt, size=params['dimensions'])
                                
                                if modified_image:
                                    # Apply logo if it was used originally
                                    if logo:
                                        st.write("🏷️ Applying logo...")
                                        from utils.image_processor import ImageProcessor
                                        logo_img = ImageProcessor.process_logo(logo)
                                        if logo_img:
                                            logo_elem = next((e for e in st.session_state.canvas_elements 
                                                            if e.get("type") == "logo" or "LOGO" in e.get("label", "").upper()), None)
                                            if logo_elem:
                                                logo_img = logo_img.resize((logo_elem["width"], logo_elem["height"]), Image.Resampling.LANCZOS)
                                                if logo_img.mode != 'RGBA':
                                                    logo_img = logo_img.convert('RGBA')
                                                logo_array = np.array(logo_img)
                                                white_mask = (logo_array[:, :, 0] > 240) & (logo_array[:, :, 1] > 240) & (logo_array[:, :, 2] > 240)
                                                logo_array[white_mask, 3] = 0
                                                logo_img = Image.fromarray(logo_array, 'RGBA')
                                                if modified_image.mode != 'RGBA':
                                                    modified_image = modified_image.convert('RGBA')
                                                modified_image.paste(logo_img, (logo_elem["x"], logo_elem["y"]), logo_img)
                                                modified_image = modified_image.convert('RGB')
                                    
                                    st.session_state.generated_ad = modified_image
                                    st.session_state.generation_params['full_prompt'] = full_edit_prompt
                                    st.session_state.edit_by_prompt_mode = False
                                    
                                    edit_status.update(label="✅ Modifications applied!", state="complete")
                                    st.success("✨ Image modified successfully!")
                                    st.rerun()
                                else:
                                    edit_status.update(label="❌ Failed", state="error")
                                    st.error("❌ Modification failed")
                                    
                            except Exception as e:
                                edit_status.update(label="❌ Error", state="error")
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.error("❌ Please enter modification instructions")
            
            with col_edit2:
                if st.button("❌ Cancel Edit", width='stretch'):
                    st.session_state.edit_by_prompt_mode = False
                    st.rerun()
        
        # Display generation details (always visible)
        st.markdown("---")
        with st.expander("📋 Generation Details", expanded=False):
            params = st.session_state.generation_params
            
            st.subheader("Model Configuration")
            st.write(f"**Model:** {params['model']}")
            st.write(f"**Dimensions:** {params['dimensions'][0]}x{params['dimensions'][1]}px")
            st.write(f"**Style:** {params['style']}")
            st.write(f"**Color Scheme:** {params['color_scheme']}")
            
            st.subheader("Canvas Elements")
            for idx, elem in enumerate(st.session_state.canvas_elements, 1):
                elem_label = elem['label']
                content = params.get("content_mapping", {}).get(elem_label, elem_label)
                st.write(f"{idx}. **{elem_label}** → '{content}' (Position: {elem['x']},{elem['y']} | Size: {elem['width']}x{elem['height']}px)")
            
            if params.get('custom_instructions'):
                st.subheader("Custom Instructions")
                st.write(params['custom_instructions'])
            
            st.subheader("Full Prompt Sent to AI")
            st.code(params['full_prompt'], language="text")
            
            if "Nano Banana Pro" in params['model']:
                st.info("🍌⭐ Used Nano Banana Pro with reference image guidance and text rendering mode")
                st.write("**Additional Features:**")
                st.write("- Reference image guidance enabled")
                st.write("- Text rendering mode: ON")
                st.write("- Search grounding: OFF")


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
        shape = elem.get("shape", "rect")
        
        # Draw shape based on type
        if shape == "circle" or shape == "ellipse":
            draw.ellipse([x, y, x + w, y + h], outline='white', width=3)
        elif shape == "line":
            draw.line([x, y, x + w, y + h], fill='white', width=3)
        elif shape == "polygon":
            # Draw as rectangle for now (polygon points not stored)
            draw.rectangle([x, y, x + w, y + h], outline='white', width=3)
        else:  # rect
            draw.rectangle([x, y, x + w, y + h], outline='white', width=3)
        
        # Select font
        if elem.get("type") == "message":
            font = font_large
        elif elem.get("type") in ["brand", "tagline"]:
            font = font_medium
        else:
            font = font_small
        
        # Draw label (skip for lines as they're too thin)
        if shape != "line":
            bbox = draw.textbbox((0, 0), label, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_x = x + (w - text_w) // 2
            text_y = y + (h - text_h) // 2
            draw.text((text_x, text_y), label, fill='white', font=font)
    
    return img
