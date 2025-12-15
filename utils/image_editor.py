"""
Filerobot Image Editor Integration for Streamlit
Provides professional image editing capabilities using Filerobot's Image Editor
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
from PIL import Image
import io
import os
from datetime import datetime

def show_image_editor():
    """Display Filerobot Image Editor for the generated advertisement"""
    
    if 'generated_ad' not in st.session_state or st.session_state.generated_ad is None:
        st.error("❌ No image to edit. Please generate an advertisement first.")
        return
    
    # Convert PIL Image to base64 for the editor
    img = st.session_state.generated_ad
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Get image dimensions
    width, height = img.size
    
    st.markdown("### 🎨 Professional Image Editor")
    st.markdown("""
    **How to use:**
    1. Edit your image using the tools in the editor below
    2. Click the **"Save"** button in the editor toolbar (top right)
    3. The image will download automatically to your Downloads folder
    4. **Upload the downloaded image** in the section below to replace your ad
    
    💡 You can also click the blue **"⬇️ Download"** button that appears after editing
    """)
    
    # Filerobot Image Editor HTML/JavaScript
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Filerobot Image Editor</title>
        <script src="https://cdn.scaleflex.it/plugins/filerobot-image-editor/4.0.0/filerobot-image-editor.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }}
            #editor-container {{
                width: 100%;
                height: 650px;
            }}
            #download-btn {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 10000;
                background: #4c6fff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(76, 111, 255, 0.4);
                display: none;
            }}
            #download-btn:hover {{
                background: #3d5ce6;
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(76, 111, 255, 0.5);
            }}
            #download-btn:active {{
                transform: translateY(0);
            }}
        </style>
    </head>
    <body>
        <div id="editor-container"></div>
        <button id="download-btn">⬇️ Download Edited Image</button>
        
        <script>
            let currentEditor = null;
            let hasEdits = false;
            
            const config = {{
                source: 'data:image/png;base64,{img_base64}',
                defaultSavedImageName: 'edited_advertisement',
                defaultSavedImageType: 'png',
                savingPixelRatio: 1,
                previewPixelRatio: 1,
                observePluginContainerSize: true,
                showCanvasOnly: false,
                useBackendTranslations: false,
                translations: {{
                    en: {{
                        'header.image_editor_title': 'Edit Advertisement',
                    }},
                }},
                theme: {{
                    palette: {{
                        'bg-primary': '#ffffff',
                        'bg-secondary': '#f5f8fa',
                        'accent-primary': '#4c6fff',
                    }},
                }},
                tabsIds: [
                    'Adjust',
                    'Annotate', 
                    'Watermark',
                    'Filters',
                    'Finetune',
                    'Resize',
                ],
                defaultTabId: 'Annotate',
                Annotate: {{
                    annotations: ['Text', 'Image', 'Rect', 'Ellipse', 'Polygon', 'Pen', 'Line', 'Arrow'],
                }},
                Text: {{
                    fonts: [
                        'Arial',
                        'Helvetica',
                        'Times New Roman',
                        'Courier',
                        'Verdana',
                        'Georgia',
                        'Comic Sans MS',
                        'Impact',
                    ],
                }},
                onModify: () => {{
                    // Show download button when user makes any edit
                    hasEdits = true;
                    document.getElementById('download-btn').style.display = 'block';
                }},
                onSave: (editedImageObject, designState) => {{
                    // This callback is triggered when user clicks Save in the editor
                    try {{
                        const imageBase64 = editedImageObject.imageBase64;
                        
                        // Convert base64 to blob
                        const base64Data = imageBase64.split(',')[1];
                        const byteCharacters = atob(base64Data);
                        const byteNumbers = new Array(byteCharacters.length);
                        for (let i = 0; i < byteCharacters.length; i++) {{
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }}
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], {{ type: 'image/png' }});
                        
                        // Create download link
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'edited_advertisement_' + new Date().getTime() + '.png';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                        
                        alert('✅ Image downloaded successfully! Upload it below to replace your ad.');
                    }} catch (error) {{
                        console.error('Save error:', error);
                        alert('Error saving image: ' + error.message);
                    }}
                }},
            }};
            
            // Initialize the editor
            currentEditor = new FilerobotImageEditor(
                document.querySelector('#editor-container'),
                config
            );
            
            // Render the editor
            currentEditor.render();
            
            // Download button handler
            document.getElementById('download-btn').addEventListener('click', async () => {{
                try {{
                    // Trigger the editor's built-in save functionality
                    const saveButton = document.querySelector('[data-testid="save-button"]');
                    if (saveButton) {{
                        saveButton.click();
                    }} else {{
                        // Try alternative selector
                        const buttons = document.querySelectorAll('button');
                        for (let btn of buttons) {{
                            if (btn.textContent.toLowerCase().includes('save')) {{
                                btn.click();
                                return;
                            }}
                        }}
                        alert('Please use the Save button in the editor toolbar at the top.');
                    }}
                }} catch (error) {{
                    console.error('Download error:', error);
                    alert('Please use the Save button in the editor toolbar at the top.');
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Display the editor
    components.html(html_code, height=750, scrolling=False)
    
    st.markdown("---")
    
    # File uploader for the edited image
    st.markdown("### 📤 Upload Your Edited Image")
    st.info("After editing and saving the image above, upload it here to replace your current advertisement.")
    
    uploaded_edited = st.file_uploader(
        "Upload the edited image (PNG/JPG)",
        type=["png", "jpg", "jpeg"],
        key="edited_image_upload",
        help="Upload the image you just saved from the editor above"
    )
    
    if uploaded_edited is not None:
        try:
            # Load the uploaded edited image
            edited_image = Image.open(uploaded_edited)
            
            # Show preview
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original:**")
                st.image(st.session_state.generated_ad, use_column_width=True)
            with col2:
                st.markdown("**Edited:**")
                st.image(edited_image, use_column_width=True)
            
            # Confirm button
            if st.button("✅ Replace with Edited Image", type="primary", width='stretch'):
                # Update session state
                st.session_state.generated_ad = edited_image
                
                # Save to file
                try:
                    output_dir = "assets/generated_ads"
                    os.makedirs(output_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    client_name = st.session_state.generation_params.get("client_name", "ad").replace(" ", "_")
                    filename = f"edited_{client_name}_{timestamp}.png"
                    filepath = os.path.join(output_dir, filename)
                    edited_image.save(filepath, "PNG")
                    st.success(f"✅ Image replaced and saved to: {filepath}")
                except Exception as save_error:
                    st.warning(f"Image replaced but couldn't save to file: {str(save_error)}")
                
                st.info("💡 Close the editor to see your updated advertisement")
                
        except Exception as e:
            st.error(f"❌ Error loading edited image: {str(e)}")
    
    st.markdown("---")
    st.markdown("""
    **Available Tools:**
    - ✏️ **Annotate**: Add text, shapes, drawings
    - 🎨 **Filters**: Apply artistic filters  
    - 🔧 **Adjust**: Brightness, contrast, saturation
    - 🔍 **Finetune**: Advanced color adjustments
    - 📏 **Resize**: Change image dimensions
    - 💧 **Watermark**: Add watermarks
    """)

def save_edited_image_to_file(image, filename):
    """Save the edited image to the generated_ads folder"""
    import os
    from datetime import datetime
    
    try:
        # Create directory if needed
        output_dir = "assets/generated_ads"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_dir, f"edited_{timestamp}_{filename}")
        
        # Save the image
        image.save(filepath, "PNG")
        
        return filepath
    except Exception as e:
        st.error(f"Error saving edited image: {str(e)}")
        return None
