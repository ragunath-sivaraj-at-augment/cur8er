# Cur8er

A powerful Streamlit application for creating professional advertisements using AI image generation.

## Features

- **Multiple Ad Sizes**: Support for various social media and print formats
- **AI Image Generation**: Integration with DALL-E 3, DALL-E 2, Google Imagen, and Nano Banana Pro
- **AI Image Editing**: Edit generated images using natural language prompts (DALL-E models)
- **Manual Image Editor**: Professional editing tools via Filerobot integration
- **Client Logo Upload**: Upload and integrate client logos into advertisements  
- **Customizable Prompts**: Detailed prompt input for creative control
- **Style Presets**: Pre-defined styles like Modern, Vintage, Professional, etc.
- **Template System**: Create and use custom templates for consistent branding
- **Export Options**: Download in PNG, JPG, or PDF formats
- **Real-time Preview**: Instant preview of generated advertisements
- **Dual Environment Support**: Works locally with .env and on Streamlit Cloud with secrets

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ai-ad-creator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit the `.env` file and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_openai_api_key_here
     ```

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Configure Ad Settings**:
   - Select ad size from predefined options or use custom dimensions
   - Choose advertising medium (Instagram, Facebook, Print, etc.)
   - Enter client name and upload client logo

2. **Create Your Prompt**:
   - Write a detailed description of your advertisement concept
   - Select AI model (DALL-E 3, DALL-E 2, etc.)
   - Choose style preset and color scheme

3. **Generate Advertisement**:
   - Click "Generate Ad" to create your advertisement
   - Use "Refresh" to regenerate with the same settings
   - Use "Edit Prompt" to modify and regenerate

4. **Edit Your Image** (Optional):
   - **AI Edit (DALL-E only)**: Use natural language to modify your image
     - Example: "Change the text color to black"
     - Example: "Make the background gradient from blue to purple"
     - Example: "Move the logo to the top right corner"
   - **Manual Edit**: Use visual editing tools (Filerobot)
     - Add text, shapes, filters, and effects
     - Resize, crop, and adjust colors
     - Apply watermarks and annotations

5. **Download Results**:
   - Download as PNG, JPG, or PDF
   - Export with metadata for future reference

## AI Image Editing (DALL-E)

When using DALL-E models, you can refine generated images using natural language prompts:

### Quick Enhancement Presets
- 🎨 **Change Text Color**: Modify text colors for better readability
- 🌈 **Enhance Colors**: Make colors more vibrant and eye-catching
- ✨ **Professional Polish**: Add shadows, lighting, and refined typography
- 🔆 **Brighten Image**: Increase exposure and vibrancy
- 🎭 **Change Background**: Modify background colors or patterns
- 📐 **Reposition Elements**: Move text, buttons, or logos

### Custom Modifications
Write custom prompts like:
- "Change the text color to black with white outline"
- "Replace the blue background with a gradient from orange to pink"
- "Make the call-to-action button larger and green"
- "Add a subtle drop shadow to the main heading"

### Advanced Options
- Preserve composition and layout
- Maintain artistic style
- Keep color scheme (unless explicitly changing)
- High quality output settings

## Project Structure

```
ai-ad-creator/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/                 # Utility modules
│   ├── __init__.py       
│   ├── ai_generator.py    # AI image generation and editing
│   ├── ai_image_editor.py # AI-powered image editing interface
│   ├── image_editor.py    # Manual image editing (Filerobot)
│   ├── image_processor.py # Image processing utilities
│   ├── template_manager.py # Template system
│   ├── template_editor.py  # Template editing interface
│   ├── prompts.py         # Prompt building utilities
│   ├── helpers.py         # Helper functions
│   └── config.py          # Environment configuration
├── templates/            # Template storage
│   └── custom/          # Custom user templates
└── assets/              # Generated content
    ├── generated_ads/   # Generated advertisement images
    └── uploaded_logos/  # Uploaded client logos
```

## API Keys Required

- **OpenAI API Key**: Required for DALL-E image generation and editing
  - Sign up at [OpenAI Platform](https://platform.openai.com/)
  - Add to `.env` file: `OPENAI_API_KEY=your_key_here`
  - Or add to Streamlit secrets for cloud deployment

- **Google API Key**: Required for Imagen and Nano Banana Pro models
  - Get API key from [Google AI Studio](https://aistudio.google.com/apikey)
  - Add to `.env` file: `GOOGLE_API_KEY=your_key_here`
  - Optionally add: `GOOGLE_PROJECT_ID=your_project_id`

## Supported Ad Formats

### Social Media
- Instagram Post (1080x1080)
- Instagram Story (1080x1920)  
- Facebook Post (1200x630)
- Facebook Cover (820x312)
- LinkedIn Post (1200x627)
- YouTube Thumbnail (1920x1080)

### Digital Display
- Web Banner (728x90)
- Leaderboard (970x250)
- Mobile Banner (320x50)

### Print
- A4 Format (2480x3508)
- Letter Format (2550x3300)
- Magazine Layout

## Style Presets

- Modern & Minimalist
- Bold & Vibrant  
- Elegant & Professional
- Retro & Vintage
- Futuristic & Tech
- Natural & Organic
- Luxury & Premium
- Playful & Fun

## Features in Development

- Advanced masking for selective AI editing
- Multi-image batch editing
- Version history and comparison
- A/B testing for ad variants
- Campaign management
- Analytics dashboard
- Video ad generation

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details.