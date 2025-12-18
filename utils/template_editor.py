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
    position: Dict[str, int]  # {'x': 50, 'y': 100}
    size: Dict[str, int]     # {'width': 200, 'height': 100}
    content: str = ""        # Text content or placeholder
    style: Dict = None       # Font, color, etc.
    
    def __post_init__(self):
        if self.style is None:
            self.style = {}

@dataclass
class TemplateLayout:
    """Complete template layout definition"""
    name: str
    dimensions: List[int]
    elements: List[TemplateElement]
    background_style: Dict = None
    
    def __post_init__(self):
        if self.background_style is None:
            self.background_style = {}

class EditableTemplateManager:
    """Manager for editable custom templates"""
    
    def __init__(self):
        self.custom_templates_dir = "templates/custom"
        os.makedirs(self.custom_templates_dir, exist_ok=True)
        self.current_template = None
        
    def get_default_elements(self, dimensions):
        """Get default template elements for given dimensions"""
        width, height = dimensions
        
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
    
    def create_template(self, name: str, dimensions: List[int]) -> TemplateLayout:
        """Create a new editable template"""
        elements = self.get_default_elements(dimensions)
        template = TemplateLayout(
            name=name,
            dimensions=dimensions,
            elements=elements,
            background_style={"style": "modern", "color_scheme": "brand"}
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
                "background_style": template.background_style
            }
            
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
                background_style=data.get("background_style", {})
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
                if submitted and template_name:
                    template = manager.create_template(template_name, dimensions)
                    st.session_state.editing_template = template
                    st.success(f"✅ Created template: {template_name}")
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
            - `{{client_website}}` - Website URL
            
            **Special Elements:**
            - `{{logo}}` - Company logo placement
            - Custom text and shapes
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
    
    # Template editor interface (full width when editing)
    if st.session_state.editing_template:
        st.markdown("---")
        show_visual_editor(st.session_state.editing_template, manager)

def show_visual_editor(template: TemplateLayout, manager: EditableTemplateManager):
    """Visual template editor interface"""
    st.markdown(f"### ✏️ Editing: **{template.name}**")
    st.markdown(f"📐 Canvas Size: **{template.dimensions[0]} × {template.dimensions[1]}** pixels")
    
    # Main editing area - three columns
    preview_col, elements_col, properties_col = st.columns([2, 1.5, 1.5])
    
    with preview_col:
        st.markdown("#### 🎨 Template Preview")
        
        # Create visual preview image
        preview_img = Image.new('RGB', tuple(template.dimensions), color='#f0f0f0')
        draw = ImageDraw.Draw(preview_img)
        
        # Draw elements on preview
        if template.elements:
            for i, element in enumerate(template.elements):
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
            bg_color = st.selectbox(
                "Color Scheme:",
                ["brand", "warm", "cool", "monochrome", "vibrant"],
                index=["brand", "warm", "cool", "monochrome", "vibrant"].index(
                    template.background_style.get("color_scheme", "brand")
                )
            )
        
        template.background_style = {"style": bg_style, "color_scheme": bg_color}
    
    with elements_col:
        st.markdown("#### 📋 Elements List")
        
        if template.elements:
            for i, element in enumerate(template.elements):
                with st.expander(f"{i+1}. {element.type.title()}: {element.content[:20]}...", expanded=False):
                    st.write(f"**Type:** {element.type}")
                    st.write(f"**Content:** {element.content}")
                    st.write(f"**Position:** ({element.position['x']}, {element.position['y']})")
                    st.write(f"**Size:** {element.size['width']} × {element.size['height']}")
                    
                    if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                        template.elements.pop(i)
                        st.rerun()
        else:
            st.info("No elements added")
        
        # Add new element with full control
        st.markdown("#### ➕ Add New Element")
        
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
            
            # Position and size inputs
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
                new_element = TemplateElement(
                    type=element_type,
                    content=content,
                    position={'x': x_pos, 'y': y_pos},
                    size={'width': width, 'height': height},
                    style={
                        'color': '#FFFFFF' if element_type == 'text' else '#FF6600',
                        'font_size': 30 if element_type == 'text' else None,
                        'bg_color': '#FF6600' if element_type == 'button' else None
                    }
                )
                template.elements.append(new_element)
                st.success(f"Added {element_type} element!")
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
                
                # Position
                st.markdown("**Position:**")
                pos_col1, pos_col2 = st.columns(2)
                with pos_col1:
                    new_x = st.number_input("X:", value=selected_element.position['x'], min_value=0)
                with pos_col2:
                    new_y = st.number_input("Y:", value=selected_element.position['y'], min_value=0)
                
                # Size
                st.markdown("**Size:**")
                size_col1, size_col2 = st.columns(2)
                with size_col1:
                    new_w = st.number_input("Width:", value=selected_element.size['width'], min_value=10)
                with size_col2:
                    new_h = st.number_input("Height:", value=selected_element.size['height'], min_value=10)
                
                # Style properties
                st.markdown("**Styling:**")
                if selected_element.type == "text":
                    font_size = st.number_input("Font Size:", value=selected_element.style.get('font_size', 30), min_value=8, max_value=200)
                    text_color = st.color_picker("Text Color:", value=selected_element.style.get('color', '#FFFFFF'))
                elif selected_element.type == "button":
                    bg_color = st.color_picker("Button Color:", value=selected_element.style.get('bg_color', '#FF6600'))
                    text_color = st.color_picker("Text Color:", value=selected_element.style.get('text_color', '#FFFFFF'))
                
                update_submitted = st.form_submit_button("💾 Update Element")
                if update_submitted:
                    # Update element properties
                    selected_element.content = new_content
                    selected_element.position = {'x': new_x, 'y': new_y}
                    selected_element.size = {'width': new_w, 'height': new_h}
                    
                    if selected_element.type == "text":
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