# Cur8er

A powerful Streamlit application for creating professional advertisements using AI image generation.

## Features

- **Multiple Ad Sizes**: Support for various social media and print formats
- **AI Image Generation**: Integration with DALL-E 3, DALL-E 2, and Stable Diffusion
- **Client Logo Upload**: Upload and integrate client logos into advertisements  
- **Customizable Prompts**: Detailed prompt input for creative control
- **Style Presets**: Pre-defined styles like Modern, Vintage, Professional, etc.
- **Export Options**: Download in PNG, JPG, or PDF formats
- **Real-time Preview**: Instant preview of generated advertisements

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

4. **Download Results**:
   - Download as PNG, JPG, or PDF
   - Export with metadata for future reference

## Project Structure

```
ai-ad-creator/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/                 # Utility modules
│   ├── __init__.py       
│   ├── ai_generator.py    # AI image generation handlers
│   ├── image_processor.py # Image processing utilities
│   └── config.py         # Application configuration
└── assets/               # Generated content
    ├── generated_ads/    # Generated advertisement images
    └── uploaded_logos/   # Uploaded client logos
```

## API Keys Required

- **OpenAI API Key**: Required for DALL-E image generation
- **Hugging Face Token**: Optional, for Stable Diffusion (coming soon)

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

- Stable Diffusion integration
- Midjourney API integration  
- Advanced logo positioning
- Text overlay editor
- Batch generation
- Campaign management
- Analytics dashboard

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details.