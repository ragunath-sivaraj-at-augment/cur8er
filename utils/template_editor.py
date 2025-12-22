"""
Editable Template System for Custom Advertisement Layouts
Provides visual template editor with drag-and-drop functionality
"""

import streamlit as st
import json
import os
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, asdict
from copy import deepcopy

@dataclass
class TemplateElement:
    """Represents a single element in a template"""
    type: str  # 'logo', 'text', 'button', 'shape'
    id: str
    content: str = ""        # Text content or placeholder
    style: Dict = None       # Font, color, style_hint, etc.
    size: Dict = None        # {'width': 200, 'height': 100}
    
    # NEW STRUCTURE (for AI-native semantic positioning)
    placement_hint: str = None  # "architectural surface", "upper area", etc.
    priority: str = None        # "highest", "high", "medium", "low"
    integration: str = None     # "engraved", "illuminated", etc.
    
    # OLD STRUCTURE (for overlay/pixel positioning - backward compatibility)
    position: Dict = None       # {'x': 50, 'y': 100} or {'zone': 'top-left'}
    
    def __post_init__(self):
        if self.style is None:
            self.style = {}
        if self.size is None:
            self.size = {"width": 200, "height": 100}

@dataclass
class TemplateLayout:
    """Complete template layout definition"""
    name: str
    dimensions: List[int]
    elements: List[TemplateElement]
    background_style: Dict = None
    positioning_mode: str = "pixel"  # 'pixel', 'zone', or 'semantic'
    design_rules: List[str] = None  # For AI-native mode
    
    def __post_init__(self):
        if self.background_style is None:
            self.background_style = {}
        if self.positioning_mode not in ["pixel", "zone", "semantic"]:
            self.positioning_mode = "pixel"
        if self.design_rules is None:
            self.design_rules = []

class EditableTemplateManager:
    """Manager for editable custom templates"""
    
    def __init__(self):
        self.custom_templates_dir = "templates/custom"
        os.makedirs(self.custom_templates_dir, exist_ok=True)
        self.current_template = None
        
    def get_default_elements(self, dimensions, positioning_mode="pixel", is_ai_native=False):
        """Get default template elements for given dimensions and positioning mode"""
        width, height = dimensions
        
        if positioning_mode == "zone" or positioning_mode == "semantic":
            # Zone-based or semantic positioning
            if is_ai_native:
                # AI-Native mode: NEW SIMPLIFIED STRUCTURE (placement_hint at element level)
                elements = [
                    TemplateElement(
                        type="logo",
                        id="logo_1",
                        placement_hint="upper architectural area with clean negative space",
                        priority="low",
                        integration="logo will be added post-generation; reserve subtle space only",
                        size={"width": min(300, width//6), "height": min(150, height//7)},
                        content="{{logo}}",
                        style={}
                    ),
                    TemplateElement(
                        type="text",
                        id="company_name", 
                        placement_hint="architectural branding surface near the upper area of the scene",
                        priority="high",
                        integration="engraved, mounted, or illuminated branding element",
                        size={"width": width//2, "height": height//8},
                        content="{{client_name}}",
                        style={"style_hint": "premium brand signage, subtle illumination, physically embedded"}
                    ),
                    TemplateElement(
                        type="text",
                        id="tagline_1",
                        placement_hint="secondary nearby surface, visually subordinate to the brand name",
                        priority="low",
                        integration="small supporting text on a wall or panel",
                        size={"width": width//3, "height": height//15},
                        content="{{client_tagline}}",
                        style={"style_hint": "minimal, elegant, unobtrusive"}
                    ),
                    TemplateElement(
                        type="text",
                        id="main_message_1",
                        placement_hint="dominant architectural surface clearly visible from the main viewpoint",
                        priority="highest",
                        integration="large-scale physical signage or illuminated wall feature",
                        size={"width": int(width*0.8), "height": height//4},
                        content="{{main_message}}",
                        style={"style_hint": "large cinematic typography, dominant, scene-integrated"}
                    ),
                    TemplateElement(
                        type="text",
                        id="cta_text_1",
                        placement_hint="small nearby signage element, not separated from the scene",
                        priority="medium",
                        integration="environmental call-to-action text, not a button",
                        size={"width": 300, "height": 100},
                        content="{{cta_text}}",
                        style={"style_hint": "short, clear, understated"}
                    )
                ]
            else:
                # Overlay mode: use traditional font specs with position dict
                elements = [
                    TemplateElement(
                        type="logo",
                        id="logo_1",
                        position={"zone": "top-left", "priority": "low", "integration": "subtle, blended into environment"},
                        size={"width": min(300, width//6), "height": min(150, height//7)},
                        content="{{logo}}",
                        style={"opacity": 1.0}
                    ),
                    TemplateElement(
                        type="text",
                        id="title_1", 
                        position={"zone": "top-center", "priority": "high", "integration": "naturally embedded, cinematic"},
                        size={"width": width//2, "height": height//8},
                        content="{{client_name}}",
                        style={"font_family": "Arial", "font_size": 60, "color": "#FFFFFF", "weight": "bold"}
                    ),
                    TemplateElement(
                        type="text",
                        id="tagline_1",
                        position={"zone": "top-right", "priority": "low", "integration": "subtle, secondary text"},
                        size={"width": width//3, "height": height//15},
                        content="{{client_tagline}}",
                        style={"font_family": "Arial", "font_size": 30, "color": "#CCCCCC"}
                    ),
                    TemplateElement(
                        type="text",
                        id="main_message_1",
                        position={"zone": "center-left", "priority": "highest", "integration": "part of the scene, readable but not flat"},
                        size={"width": int(width*0.8), "height": height//4},
                        content="{{main_message}}",
                        style={"font_family": "Arial", "font_size": 48, "color": "#FFFFFF", "weight": "normal"}
                    ),
                    TemplateElement(
                        type="button",
                        id="cta_button_1",
                        position={"zone": "bottom-center", "priority": "medium", "integration": "naturally integrated"},
                        size={"width": 300, "height": 100},
                        content="{{cta_text}}",
                        style={"bg_color": "#FF6600", "text_color": "#FFFFFF", "font_size": 32, "border_radius": 10}
                    )
                ]
            
            return elements
        else:
            # Pixel-based default positions
            return [
                TemplateElement(
                    type="logo",
                    id="logo_1",
                    position={"x": 50, "y": 50},
                    size={"width": min(300, width//6), "height": min(150, height//7)},
                    content="{{logo}}",
                    style={"opacity": 1.0}
                ),
                TemplateElement(
                    type="text",
                    id="title_1", 
                    position={"x": width//4, "y": 50},
                    size={"width": width//2, "height": height//8},
                    content="{{client_name}}",
                    style={"font_family": "Arial", "font_size": 60, "color": "#FFFFFF", "weight": "bold"}
                ),
                TemplateElement(
                    type="text",
                    id="tagline_1",
                    position={"x": width//4, "y": height//5},
                    size={"width": width//2, "height": height//15},
                    content="{{client_tagline}}",
                    style={"font_family": "Arial", "font_size": 30, "color": "#CCCCCC"}
                ),
                TemplateElement(
                    type="text",
                    id="main_message_1",
                    position={"x": 50, "y": height//2},
                    size={"width": int(width*0.8), "height": height//4},
                    content="{{main_message}}",
                    style={"font_family": "Arial", "font_size": 48, "color": "#FFFFFF", "weight": "normal"}
                ),
                TemplateElement(
                    type="button",
                    id="cta_button_1",
                    position={"x": width-350, "y": height-150},
                    size={"width": 300, "height": 100},
                    content="{{cta_text}}",
                    style={"bg_color": "#FF6600", "text_color": "#FFFFFF", "font_size": 32, "border_radius": 10}
                )
            ]
    
    def create_template(self, name: str, dimensions: List[int], positioning_mode: str = "pixel", is_ai_native: bool = False) -> TemplateLayout:
        """Create a new editable template"""
        elements = self.get_default_elements(dimensions, positioning_mode, is_ai_native)
        
        # Define design rules for AI-native mode
        design_rules = []
        if is_ai_native:
            design_rules = [
                "Generate a single continuous real-world scene",
                "No panels, no split views, no segmented layouts",
                "No UI elements, labels, badges, or black rounded rectangles",
                "All text must exist on real physical surfaces",
                "One dominant message, others must support it",
                "Cinematic lighting, realistic materials, premium brand feel"
            ]
        
        template = TemplateLayout(
            name=name,
            dimensions=dimensions,
            elements=elements,
            background_style={"style": "modern", "color_scheme": "brand"},
            positioning_mode="semantic" if is_ai_native else positioning_mode,
            design_rules=design_rules
        )
        return template
    
    def save_template(self, template: TemplateLayout) -> bool:
        """Save template to custom templates directory"""
        try:
            filename = f"{template.name.replace(' ', '_').lower()}.json"
            filepath = os.path.join(self.custom_templates_dir, filename)
            
            # Convert to serializable format
            template_dict = {
                "name": template.name,
                "dimensions": template.dimensions,
                "elements": [asdict(element) for element in template.elements],
                "background_style": template.background_style,
                "positioning_mode": template.positioning_mode
            }
            
            # Add design_rules if AI-native
            if template.design_rules:
                template_dict["design_rules"] = template.design_rules
            
            with open(filepath, 'w') as f:
                json.dump(template_dict, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Failed to save template: {e}")
            return False
    
    def load_template(self, template_name: str) -> Optional[TemplateLayout]:
        """Load template from file"""
        try:
            filename = f"{template_name.replace(' ', '_').lower()}.json"
            filepath = os.path.join(self.custom_templates_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            elements = [TemplateElement(**elem) for elem in data["elements"]]
            template = TemplateLayout(
                name=data["name"],
                dimensions=data["dimensions"],
                elements=elements,
                background_style=data.get("background_style", {}),
                positioning_mode=data.get("positioning_mode", "pixel"),  # Default to pixel for backward compatibility
                design_rules=data.get("design_rules", [])  # Load design_rules if present
            )
            
            return template
        except Exception as e:
            st.error(f"Failed to load template: {e}")
            return None
    
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

def show_template_editor():
    """Main template editor interface"""
    # Initialize session state for template editing
    if 'editing_template' not in st.session_state:
        st.session_state.editing_template = None
    if 'template_manager' not in st.session_state:
        st.session_state.template_manager = EditableTemplateManager()
    
    manager = st.session_state.template_manager
    
    # Header with overview
    st.markdown("""
    ### 🎯 Template Editor Overview
    Create custom advertisement templates with precise element positioning. Use template variables like `{{logo}}`, `{{client_name}}`, etc.
    """)
    
    # Two main sections side by side
    editor_col1, editor_col2 = st.columns([1, 1])
    
    with editor_col1:
        st.markdown("#### 📋 Template Management")
        
        # Option to create new or edit existing
        action = st.radio(
            "Choose action:",
            ["Create New Template", "Edit Existing Template"],
            horizontal=True
        )
        
        if action == "Create New Template":
            with st.form("create_template_form"):
                template_name = st.text_input("Template Name", placeholder="e.g., Holiday Sale Banner")
                
                # Rendering mode selector
                st.markdown("**Template Rendering Mode:**")
                rendering_mode = st.radio(
                    "How should text be rendered?",
                    ["🎨 AI-Native (Cinematic - AI generates all text as part of scene)", 
                     "🖼️ Overlay (Traditional - Text added on top of background)"],
                    index=1,
                    help="AI-Native for cinematic integration, Overlay for precise control"
                )
                is_ai_native = "AI-Native" in rendering_mode
                
                # Positioning mode selector (only for overlay mode)
                if not is_ai_native:
                    st.markdown("**Positioning Mode:**")
                    positioning_mode = st.radio(
                        "Choose how elements will be positioned:",
                        ["📍 Pixel Mode (Precise X,Y coordinates)", "🎯 Zone Mode (Semantic placement)"],
                        index=0,
                        help="Pixel mode for exact control, Zone mode for semantic placement"
                    )
                    selected_mode = "zone" if "Zone" in positioning_mode else "pixel"
                else:
                    # AI-Native always uses zone mode
                    selected_mode = "zone"
                    st.info("🎯 AI-Native mode uses zone-based positioning with style hints")
                
                dimensions_preset = st.selectbox(
                    "Template Dimensions:",
                    ["Billboard (1920x1080)", "Social Square (1080x1080)", "Web Banner (728x300)", "Instagram Story (1080x1920)", "Custom"]
                )
                
                if dimensions_preset == "Custom":
                    dim_col1, dim_col2 = st.columns(2)
                    with dim_col1:
                        custom_width = st.number_input("Width", min_value=100, max_value=4000, value=1080)
                    with dim_col2:
                        custom_height = st.number_input("Height", min_value=100, max_value=4000, value=1080)
                    dimensions = [custom_width, custom_height]
                else:
                    dim_map = {
                        "Billboard (1920x1080)": [1920, 1080],
                        "Social Square (1080x1080)": [1080, 1080],
                        "Web Banner (728x300)": [728, 300],
                        "Instagram Story (1080x1920)": [1080, 1920]
                    }
                    dimensions = dim_map[dimensions_preset]
                
                submitted = st.form_submit_button("🎨 Create Template", width='stretch')
                if submitted:
                    if not template_name or not template_name.strip():
                        st.error("❌ Please enter a template name")
                    else:
                        template = manager.create_template(template_name, dimensions, selected_mode, is_ai_native)
                        st.session_state.editing_template = template
                        mode_desc = "AI-Native Zone-based" if is_ai_native else ("Zone-based" if selected_mode == "zone" else "Pixel-based")
                        st.success(f"✅ Created {mode_desc} template: {template_name}")
                        st.rerun()
        
        else:  # Edit existing
            custom_templates = manager.get_custom_templates()
            if custom_templates:
                selected_template = st.selectbox("Select Template to Edit:", custom_templates)
                
                if st.button("✏️ Load Template", width='stretch'):
                    template = manager.load_template(selected_template)
                    if template:
                        st.session_state.editing_template = template
                        st.success(f"✅ Loaded template: {selected_template}")
                        st.rerun()
            else:
                st.info("📝 No custom templates found. Create your first template!")
    
    with editor_col2:
        st.markdown("#### 💡 Template Variables & Tips")
        
        with st.expander("🏷️ Available Template Variables", expanded=True):
            st.markdown("""
            **Text Placeholders:**
            - `{{client_name}}` - Company name
            - `{{client_tagline}}` - Company slogan  
            - `{{main_message}}` - Advertisement main message/description
            - `{{cta_text}}` - Call-to-action button text
            - `{{client_website}}` - Website URL (can be used as text element or with button)
            
            **Special Elements:**
            - `{{logo}}` - Company logo placement
            - Custom text and shapes
            
            **💡 Note:** All variables are optional. Elements with empty values won't be displayed.
            You can use `{{client_website}}` as a standalone text element anywhere in your template!
            """)
        
        with st.expander("📐 Positioning Modes", expanded=False):
            st.markdown("""
            **🎯 Choose When Creating Template:**
            
            **📍 Pixel Mode (Precise):**
            - Exact X,Y coordinates for pixel-perfect designs
            - Full visual control in the preview
            - Best for: Final production templates, specific brand requirements
            - All elements use exact coordinates
            
            **🎯 Zone Mode (Semantic + AI-Aware):**
            - Use semantic zones (top-left, center, etc.)
            - Add style hints (blended, bold, subtle)
            - AI generates backgrounds aware of your text placement
            - Best for: Quick layouts, AI-integrated designs, dynamic content
            - All elements use zone-based positioning
            
            **💡 Select mode when creating template - all elements will use that mode!**
            """)
        
        with st.expander("📐 Layout Tips", expanded=False):
            st.markdown("""
            **Best Practices:**
            - Logo: Top-left or center, 150-300px wide
            - Headline: Upper portion, large font (60-80px)
            - Body text: Center area, readable size (24-36px)
            - CTA button: Bottom-right, 200-300px wide
            - Maintain consistent margins (50-100px)
            """)
        
        if st.session_state.editing_template:
            st.markdown("#### 🎯 Current Template")
            template = st.session_state.editing_template
            st.metric("Template Name", template.name)
            st.metric("Dimensions", f"{template.dimensions[0]}×{template.dimensions[1]}px")
            st.metric("Elements", len(template.elements))
            
            # Show rendering mode
            is_ai_native = bool(template.design_rules)
            render_icon = "🎨" if is_ai_native else "🖼️"
            render_name = "AI-Native (Cinematic)" if is_ai_native else "Overlay (Traditional)"
            st.metric("Rendering", f"{render_icon} {render_name}")
            
            # Show positioning mode
            if not is_ai_native:
                mode_icon = "🎯" if template.positioning_mode == "zone" else "📍"
                mode_name = "Zone-based" if template.positioning_mode == "zone" else "Pixel-based"
                st.metric("Positioning", f"{mode_icon} {mode_name}")
    
    # Template editor interface (full width when editing)
    if st.session_state.editing_template:
        st.markdown("---")
        show_visual_editor(st.session_state.editing_template, manager)

def show_visual_editor(template: TemplateLayout, manager: EditableTemplateManager):
    """Visual template editor interface"""
    mode_icon = "🎯" if template.positioning_mode == "zone" else "📍"
    mode_name = "Zone-based" if template.positioning_mode == "zone" else "Pixel-based"
    st.markdown(f"### ✏️ Editing: **{template.name}** {mode_icon} ({mode_name})")
    st.markdown(f"📐 Canvas Size: **{template.dimensions[0]} × {template.dimensions[1]}** pixels")
    
    # Main editing area - three columns
    preview_col, elements_col, properties_col = st.columns([2, 1.5, 1.5])
    
    with preview_col:
        st.markdown("#### 🎨 Template Preview")
        
        # Check template's positioning mode
        is_zone_template = (template.positioning_mode == "zone")
        
        # Create visual preview image
        preview_img = Image.new('RGB', tuple(template.dimensions), color='#f0f0f0')
        draw = ImageDraw.Draw(preview_img)
        
        # Draw zone grid overlay if this is a zone-based template
        if is_zone_template:
            width, height = template.dimensions
            # Draw light grid lines to show zones
            grid_color = '#d0d0d0'
            # Vertical lines (3 columns)
            draw.line([(width//3, 0), (width//3, height)], fill=grid_color, width=1)
            draw.line([(2*width//3, 0), (2*width//3, height)], fill=grid_color, width=1)
            # Horizontal lines (3 rows)
            draw.line([(0, height//3), (width, height//3)], fill=grid_color, width=1)
            draw.line([(0, 2*height//3), (width, 2*height//3)], fill=grid_color, width=1)
            
            # Add zone labels
            try:
                zone_font = ImageFont.truetype("arial.ttf", 14)
            except:
                zone_font = ImageFont.load_default()
            
            zone_labels = [
                ("top-left", width//6, height//6),
                ("top-center", width//2, height//6),
                ("top-right", 5*width//6, height//6),
                ("center-left", width//6, height//2),
                ("center", width//2, height//2),
                ("center-right", 5*width//6, height//2),
                ("bottom-left", width//6, 5*height//6),
                ("bottom-center", width//2, 5*height//6),
                ("bottom-right", 5*width//6, 5*height//6)
            ]
            for label, x, y in zone_labels:
                draw.text((x, y), label, fill='#999999', anchor="mm", font=zone_font)
        
        # Draw elements on preview
        if template.elements:
            for i, element in enumerate(template.elements):
                # Resolve position (zone or pixel)
                if 'zone' in element.position:
                    # For zone-based, calculate approximate center position for preview
                    from utils.template_manager import TemplateManager
                    tm = TemplateManager()
                    pos = tm._resolve_position(element.position, template.dimensions)
                    x, y = pos['x'], pos['y']
                else:
                    x = element.position['x']
                    y = element.position['y']
                
                w = element.size['width']
                h = element.size['height']
                
                # Draw element box based on type
                if element.type == "logo":
                    # Logo area - purple/blue
                    draw.rectangle([x, y, x+w, y+h], fill='#9B59B6', outline='#8E44AD', width=3)
                    # Add text label
                    try:
                        font = ImageFont.truetype("arial.ttf", min(30, h//3))
                    except:
                        font = ImageFont.load_default()
                    draw.text((x+w//2, y+h//2), "LOGO", fill='white', anchor="mm", font=font)
                    
                elif element.type == "text":
                    # Text area - light blue
                    draw.rectangle([x, y, x+w, y+h], fill='#3498DB', outline='#2980B9', width=2)
                    # Add text label
                    try:
                        font_size = min(element.style.get('font_size', 30), h//2)
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    text_preview = element.content[:20] if element.content else "Text"
                    draw.text((x+10, y+h//2), text_preview, fill='white', anchor="lm", font=font)
                    
                elif element.type == "button":
                    # Button - orange
                    bg_color = element.style.get('bg_color', '#FF6600')
                    draw.rectangle([x, y, x+w, y+h], fill=bg_color, outline='#E55D00', width=3)
                    # Add button text
                    try:
                        font = ImageFont.truetype("arial.ttf", min(24, h//2))
                    except:
                        font = ImageFont.load_default()
                    btn_text = element.content[:15] if element.content else "Button"
                    draw.text((x+w//2, y+h//2), btn_text, fill='white', anchor="mm", font=font)
                    
                elif element.type == "shape":
                    # Shape - gray
                    fill_color = element.style.get('fill_color', '#95A5A6')
                    draw.rectangle([x, y, x+w, y+h], fill=fill_color, outline='#7F8C8D', width=2)
        
        # Display the preview image
        st.image(preview_img, caption=f"Template Layout Preview - {template.dimensions[0]}×{template.dimensions[1]}px", width='stretch')
        
        # Show elements list below preview
        if template.elements:
            with st.expander("📋 Elements Summary", expanded=False):
                elements_info = ""
                for i, element in enumerate(template.elements):
                    elements_info += f"**{i+1}. {element.type.title()}:** `{element.content[:25]}{'...' if len(element.content) > 25 else ''}`\n"
                    # Show position based on format
                    if 'zone' in element.position:
                        zone = element.position['zone']
                        style = element.position.get('style', '')
                        elements_info += f"  🎯 Zone: **{zone}**"
                        if style:
                            elements_info += f" | Style: *{style}*"
                        elements_info += f" | Size: {element.size['width']}×{element.size['height']}\n\n"
                    else:
                        elements_info += f"  📍 Position: ({element.position['x']}, {element.position['y']}) | Size: {element.size['width']}×{element.size['height']}\n\n"
                st.markdown(elements_info)
        else:
            st.info("No elements added yet. Use the 'Add Element' section to start building your template.")
        
        # Background settings
        st.markdown("#### 🌈 Background Style")
        bg_col1, bg_col2 = st.columns(2)
        with bg_col1:
            bg_style = st.selectbox(
                "Style:",
                ["modern", "classic", "minimal", "bold", "elegant"],
                index=["modern", "classic", "minimal", "bold", "elegant"].index(
                    template.background_style.get("style", "modern")
                )
            )
        with bg_col2:
            color_schemes = ["brand", "warm", "cool", "monochrome", "vibrant"]
            current_scheme = template.background_style.get("color_scheme", "brand")
            scheme_index = color_schemes.index(current_scheme) if current_scheme in color_schemes else 0
            bg_color = st.selectbox(
                "Color Scheme:",
                color_schemes,
                index=scheme_index
            )
        
        template.background_style = {"style": bg_style, "color_scheme": bg_color}
    
    with elements_col:
        st.markdown("#### 📋 Elements List")
        
        if template.elements:
            for i, element in enumerate(template.elements):
                # Create title with position mode indicator
                pos_icon = "🎯" if 'zone' in element.position else "📍"
                with st.expander(f"{pos_icon} {i+1}. {element.type.title()}: {element.content[:20]}...", expanded=False):
                    st.write(f"**Type:** {element.type}")
                    st.write(f"**Content:** {element.content}")
                    
                    # Display position based on format
                    if 'zone' in element.position:
                        st.write(f"**Position Mode:** Zone-based")
                        st.write(f"**Zone:** {element.position['zone']}")
                        if element.position.get('style'):
                            st.write(f"**Style:** {element.position['style']}")
                        if element.position.get('integration'):
                            st.write(f"**Integration:** {element.position['integration']}")
                    else:
                        st.write(f"**Position Mode:** Pixel-based")
                        st.write(f"**Position:** ({element.position['x']}, {element.position['y']})")
                    
                    st.write(f"**Size:** {element.size['width']} × {element.size['height']}")
                    
                    if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                        template.elements.pop(i)
                        st.rerun()
        else:
            st.info("No elements added")
        
        # Add new element with full control
        st.markdown("#### ➕ Add New Element")
        
        # Display template's positioning mode
        template_mode = template.positioning_mode
        mode_icon = "🎯" if template_mode == "zone" else "📍"
        mode_name = "Zone-based" if template_mode == "zone" else "Pixel-based"
        st.info(f"{mode_icon} **Template Mode: {mode_name}** (All elements use this mode)")
        
        is_zone_mode = (template_mode == "zone")
        
        with st.form("add_element_form", clear_on_submit=True):
            element_type = st.selectbox("Element Type:", ["text", "logo", "button", "shape"])
            
            if element_type == "text":
                content = st.text_input("Text Content:", placeholder="{{client_name}} or custom text")
            elif element_type == "logo":
                content = "{{logo}}"
                st.info("Logo placeholder automatically set")
            elif element_type == "button":
                content = st.text_input("Button Text:", placeholder="{{cta_text}} or SHOP NOW")
            else:  # shape
                content = st.text_input("Shape Label:", placeholder="Decorative shape")
            
            # Position inputs - different for pixel vs zone mode
            if is_zone_mode:
                # Zone-based positioning
                is_ai_native = bool(template.design_rules)
                
                zone_col1, zone_col2 = st.columns(2)
                with zone_col1:
                    zone = st.selectbox(
                        "Zone:",
                        ["top-left", "top-center", "top-right",
                         "center-left", "center", "center-right",
                         "bottom-left", "bottom-center", "bottom-right"],
                        index=0
                    )
                with zone_col2:
                    if is_ai_native:
                        priority = st.selectbox(
                            "Priority:",
                            ["highest", "high", "medium", "low"],
                            index=2,
                            help="Visual priority for AI rendering"
                        )
                    else:
                        style_hint = st.text_input(
                            "Style:",
                            placeholder="e.g., blended, bold, subtle",
                            help="Visual style hints for AI background generation"
                        )
                
                if is_ai_native:
                    integration = st.text_input(
                        "Integration:",
                        placeholder="e.g., part of the scene, readable but not flat",
                        value="naturally integrated",
                        help="How element integrates with scene"
                    )
                    
                    if element_type != "logo":
                        visual_style = st.text_input(
                            "Visual Style Hint:",
                            placeholder="e.g., clear, large, modern typography with subtle glow",
                            help="Describe how AI should render this text"
                        )
                else:
                    integration = st.text_input(
                        "Integration:",
                        placeholder="e.g., naturally part of environment",
                        value="naturally integrated",
                        help="How element should integrate with AI-generated background"
                    )
            else:
                # Pixel-based positioning (existing)
                pos_col1, pos_col2 = st.columns(2)
                with pos_col1:
                    x_pos = st.number_input("X Position", min_value=0, max_value=template.dimensions[0], value=50)
                with pos_col2:
                    y_pos = st.number_input("Y Position", min_value=0, max_value=template.dimensions[1], value=50)
            
            size_col1, size_col2 = st.columns(2)
            with size_col1:
                width = st.number_input("Width", min_value=10, max_value=template.dimensions[0], value=200)
            with size_col2:
                height = st.number_input("Height", min_value=10, max_value=template.dimensions[1], value=60)
            
            submitted = st.form_submit_button("➕ Add Element")
            if submitted and content:
                # Build position dict based on mode
                is_ai_native = bool(template.design_rules)
                
                if is_zone_mode:
                    if is_ai_native:
                        position = {
                            'zone': zone,
                            'priority': priority,
                            'integration': integration if integration.strip() else 'naturally integrated'
                        }
                    else:
                        position = {
                            'zone': zone,
                            'style': style_hint if style_hint.strip() else '',
                            'integration': integration if integration.strip() else 'naturally integrated'
                        }
                else:
                    position = {'x': x_pos, 'y': y_pos}
                
                # Generate unique ID for the element
                element_id = f"{element_type}_{len(template.elements) + 1}"
                
                # Build style dict based on mode
                if is_ai_native:
                    # AI-native: only style_hint, no font specs
                    element_style = {}
                    if element_type != 'logo' and 'visual_style' in locals() and visual_style.strip():
                        element_style['style_hint'] = visual_style
                    elif element_type == 'logo':
                        element_style['opacity'] = 1.0
                else:
                    # Overlay mode: traditional font specs
                    element_style = {
                        'color': '#FFFFFF' if element_type == 'text' else '#FF6600',
                        'font_size': 30 if element_type == 'text' else None,
                        'bg_color': '#FF6600' if element_type == 'button' else None
                    }
                
                new_element = TemplateElement(
                    type=element_type,
                    id=element_id,
                    content=content,
                    position=position,
                    size={'width': width, 'height': height},
                    style=element_style
                )
                template.elements.append(new_element)
                mode_name = "AI-native zone-based" if is_ai_native else ("zone-based" if is_zone_mode else "pixel-based")
                st.success(f"Added {element_type} element ({mode_name})!")
                st.rerun()
    
    with properties_col:
        st.markdown("#### ⚙️ Element Properties")
        
        if template.elements:
            # Element selection
            element_names = [f"{i+1}. {elem.type}: {elem.content[:15]}..." for i, elem in enumerate(template.elements)]
            if 'selected_element_idx' not in st.session_state:
                st.session_state.selected_element_idx = 0
            
            selected_idx = st.selectbox(
                "Select Element:", 
                range(len(element_names)), 
                format_func=lambda x: element_names[x],
                key="element_selector"
            )
            
            selected_element = template.elements[selected_idx]
            
            st.markdown(f"**Editing: {selected_element.type.title()}**")
            
            with st.form(f"edit_element_form_{selected_idx}"):
                # Content
                new_content = st.text_input("Content:", value=selected_element.content)
                
                # Position - different for pixel vs zone mode
                st.markdown("**Position:**")
                if template.positioning_mode == "zone":
                    # Zone-based editing
                    zone_col1, zone_col2 = st.columns(2)
                    with zone_col1:
                        current_zone = selected_element.position.get('zone', 'center')
                        new_zone = st.selectbox(
                            "Zone:",
                            ["top-left", "top-center", "top-right",
                             "center-left", "center", "center-right",
                             "bottom-left", "bottom-center", "bottom-right"],
                            index=["top-left", "top-center", "top-right",
                                   "center-left", "center", "center-right",
                                   "bottom-left", "bottom-center", "bottom-right"].index(current_zone)
                        )
                    with zone_col2:
                        current_style = selected_element.position.get('style', '')
                        new_style = st.text_input("Style:", value=current_style, placeholder="e.g., blended, bold")
                    
                    current_integration = selected_element.position.get('integration', 'naturally integrated')
                    new_integration = st.text_input("Integration:", value=current_integration)
                else:
                    # Pixel-based editing
                    pos_col1, pos_col2 = st.columns(2)
                    with pos_col1:
                        new_x = st.number_input("X:", value=selected_element.position.get('x', 0), min_value=0)
                    with pos_col2:
                        new_y = st.number_input("Y:", value=selected_element.position.get('y', 0), min_value=0)
                
                # Size
                st.markdown("**Size:**")
                size_col1, size_col2 = st.columns(2)
                with size_col1:
                    new_w = st.number_input("Width:", value=selected_element.size['width'], min_value=10)
                with size_col2:
                    new_h = st.number_input("Height:", value=selected_element.size['height'], min_value=10)
                
                # Style properties
                st.markdown("**Styling:**")
                
                is_ai_native = bool(template.design_rules)
                
                if is_ai_native and selected_element.type != "logo":
                    # AI-native mode: only style_hint
                    current_style_hint = selected_element.style.get('style_hint', '')
                    new_style_hint = st.text_area(
                        "Visual Style Hint:", 
                        value=current_style_hint,
                        placeholder="e.g., glowing neon sign, illuminated billboard text",
                        help="Describe how the AI should render this text in the scene"
                    )
                elif selected_element.type == "text":
                    # Overlay mode: traditional font properties
                    font_size = st.number_input("Font Size:", value=selected_element.style.get('font_size', 30), min_value=8, max_value=200)
                    text_color = st.color_picker("Text Color:", value=selected_element.style.get('color', '#FFFFFF'))
                elif selected_element.type == "button":
                    bg_color = st.color_picker("Button Color:", value=selected_element.style.get('bg_color', '#FF6600'))
                    text_color = st.color_picker("Text Color:", value=selected_element.style.get('text_color', '#FFFFFF'))
                
                update_submitted = st.form_submit_button("💾 Update Element")
                if update_submitted:
                    # Update element properties
                    selected_element.content = new_content
                    
                    # Update position based on mode
                    if template.positioning_mode == "zone":
                        if is_ai_native:
                            # AI-native: position has priority
                            selected_element.position = {
                                'zone': new_zone,
                                'priority': selected_element.position.get('priority', 'medium'),
                                'integration': new_integration
                            }
                        else:
                            # Overlay: position has style
                            selected_element.position = {
                                'zone': new_zone,
                                'style': new_style,
                                'integration': new_integration
                            }
                    else:
                        selected_element.position = {'x': new_x, 'y': new_y}
                    
                    selected_element.size = {'width': new_w, 'height': new_h}
                    
                    # Update style based on mode
                    if is_ai_native and selected_element.type != "logo":
                        selected_element.style = {'style_hint': new_style_hint}
                    elif selected_element.type == "text":
                        selected_element.style.update({
                            'font_size': font_size,
                            'color': text_color
                        })
                    elif selected_element.type == "button":
                        selected_element.style.update({
                            'bg_color': bg_color,
                            'text_color': text_color
                        })
                    
                    st.success("Element updated!")
                    st.rerun()
        else:
            st.info("Add elements to edit their properties")
        
        # Save template section
        st.markdown("---")
        st.markdown("#### 💾 Template Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("💾 Save Template", width='stretch', type="primary"):
                if manager.save_template(template):
                    st.success(f"✅ Template '{template.name}' saved successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save template")
        
        with action_col2:
            if st.button("🔄 Reset Layout", width='stretch'):
                template.elements = manager.get_default_elements(template.dimensions)
                st.success("Template reset to default layout")
                st.rerun()
        
        with action_col3:
            if st.button("❌ Close Editor", width='stretch'):
                # Close both the editing template and the template editor itself
                st.session_state.editing_template = None
                st.session_state.show_template_editor = False
                st.rerun()