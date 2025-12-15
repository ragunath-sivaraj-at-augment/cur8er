# AI Image Editing with DALL-E - User Guide

## Overview

The AI Image Editor allows you to refine and modify your generated advertisements using natural language prompts. This feature is exclusively available when using DALL-E models (DALL-E 2 or DALL-E 3).

## How It Works

### Technical Implementation

1. **DALL-E 2 Edit API**: The feature uses OpenAI's `images.edit()` endpoint
2. **Intelligent Modifications**: DALL-E understands natural language and modifies only the parts you specify
3. **Quality Preservation**: Original image quality and style are maintained unless explicitly changed
4. **No Masking Required**: DALL-E intelligently determines what to modify based on your prompt

### When to Use AI Editing vs Manual Editing

| Feature | AI Edit (DALL-E) | Manual Edit (Filerobot) |
|---------|------------------|------------------------|
| **Availability** | DALL-E models only | All models |
| **Method** | Natural language prompts | Visual editing tools |
| **Best For** | Color changes, style adjustments, element repositioning | Precise manual adjustments, adding text/shapes |
| **Speed** | 10-20 seconds per edit | Immediate |
| **Examples** | "Change text to black" | Drawing, cropping, filters |

## Using the AI Image Editor

### Step 1: Generate an Image with DALL-E

First, generate your advertisement using DALL-E 3 or DALL-E 2:
1. Select DALL-E as your AI model
2. Configure your ad settings
3. Generate the image

### Step 2: Access AI Editor

In the Quick Actions section:
- Click **"✨ AI Edit (DALL-E)"** button
- This opens the full AI Image Editor interface

### Step 3: Choose or Create Your Modification

**Option A: Use Quick Enhancement Presets**

Click any preset button for instant modifications:
- 🎨 **Change Text Color** → "Change the text color to black with white outline for better readability"
- 🌈 **Enhance Colors** → "Make the colors more vibrant and eye-catching"
- ✨ **Professional Polish** → "Add professional polish with subtle shadows and lighting"
- 🔆 **Brighten Image** → "Brighten the overall image, increase exposure"
- 🎭 **Change Background** → "Change the background to a gradient from blue to purple"
- 📐 **Reposition Elements** → "Move the main text to the top center"

**Option B: Write Custom Modification**

Enter your own detailed prompt describing the changes:
```
Good examples:
✅ "Change the text color from white to black"
✅ "Replace the blue background with a sunset gradient"
✅ "Make the call-to-action button larger and green"
✅ "Move the company logo to the top right corner"
✅ "Add a subtle drop shadow to the main heading"

Avoid:
❌ "make it better" (too vague)
❌ "change everything" (too broad)
❌ "add a unicorn" (not present in original)
```

### Step 4: Configure Advanced Options (Optional)

Expand "⚙️ Advanced Options" to fine-tune:

- **Preserve Composition**: Keep the overall layout and structure
- **Preserve Art Style**: Maintain the same artistic style
- **Preserve Color Scheme**: Keep colors unless explicitly changing them
- **High Quality Output**: Use best quality settings

### Step 5: Apply the Edit

1. Click **"✨ Apply AI Edit"**
2. Wait 10-20 seconds for DALL-E to process
3. Review the Before & After comparison
4. Choose an action:
   - **✅ Keep Edited Version**: Save and use the edited image
   - **🔄 Try Another Edit**: Apply additional modifications
   - **❌ Discard Changes**: Revert to original

## Example Use Cases

### Use Case 1: Text Color Adjustment

**Scenario**: Generated ad has white text on light background (hard to read)

**Prompt**: 
```
Change the text color to black with a white outline for better readability
```

**Settings**:
- ✅ Preserve Composition
- ✅ Preserve Art Style
- ✅ High Quality Output

### Use Case 2: Background Modification

**Scenario**: Want to change background color while keeping everything else

**Prompt**:
```
Replace the blue background with a gradient from orange to pink, keep all other elements exactly the same
```

**Settings**:
- ✅ Preserve Composition
- ✅ Preserve Art Style
- ❌ Preserve Color Scheme (we're changing colors)

### Use Case 3: Layout Adjustment

**Scenario**: Need to reposition elements for better composition

**Prompt**:
```
Move the company logo to the top right corner and center the main headline at the top
```

**Settings**:
- ❌ Preserve Composition (we're changing layout)
- ✅ Preserve Art Style
- ✅ Preserve Color Scheme

### Use Case 4: Multiple Enhancements

**Scenario**: Want to improve overall quality

**Prompt**:
```
Make the colors more vibrant, add subtle shadows to text for depth, and increase contrast slightly
```

**Settings**:
- ✅ Preserve Composition
- ✅ Preserve Art Style
- ❌ Preserve Color Scheme (we're enhancing colors)
- ✅ High Quality Output

## Tips for Best Results

### Prompt Writing Tips

1. **Be Specific**: Instead of "better", say "brighter" or "higher contrast"
2. **Reference Elements**: Mention what's already in the image
3. **One Change at a Time**: Multiple edits work better than one complex edit
4. **Use Colors by Name**: "navy blue", "bright red", "golden yellow"
5. **Specify Positions**: "top left", "center", "bottom right"

### What Works Well

✅ Color changes (text, background, elements)
✅ Brightness and contrast adjustments
✅ Element repositioning
✅ Style enhancements (shadows, glows, effects)
✅ Size adjustments for existing elements
✅ Background modifications

### What Doesn't Work Well

❌ Adding completely new elements (use regeneration instead)
❌ Removing elements (DALL-E edit doesn't remove)
❌ Very complex multi-step edits (break into smaller edits)
❌ Changing fundamental image structure

## Troubleshooting

### "Failed to edit image"

**Causes**:
- API key issues
- Image format problems
- Too complex prompt

**Solutions**:
1. Check your OpenAI API key in `.env` or Streamlit secrets
2. Try a simpler, more specific prompt
3. Ensure the original image was generated successfully

### "Edit doesn't match expectations"

**Causes**:
- Vague prompt
- DALL-E interpreted differently

**Solutions**:
1. Be more specific in your description
2. Use color names, positions, and sizes explicitly
3. Try the "🔄 Try Another Edit" option with revised prompt

### "Image quality degraded"

**Causes**:
- Multiple sequential edits
- Low quality source image

**Solutions**:
1. Check "High Quality Output" in Advanced Options
2. Start from original generated image instead of edited version
3. Consider regenerating with better initial prompt

## Technical Details

### API Requirements

- **OpenAI API Key**: Required
- **Model**: DALL-E 2 (used for editing even if DALL-E 3 generated the image)
- **Image Format**: Automatically converted to PNG RGBA
- **Size Limits**: Images scaled to max 1024x1024 for processing

### Processing Steps

1. Image converted to RGBA PNG format
2. Resized and padded to square (if needed)
3. Sent to DALL-E 2 edit endpoint with prompt
4. Edited image downloaded
5. Cropped/resized back to original dimensions
6. Displayed for user review

### Cost Considerations

Each AI edit request costs the same as DALL-E 2 image generation:
- **1024×1024**: $0.020 per image
- Usage tracked on your OpenAI account

## Combining AI Edit with Manual Edit

For best results, you can combine both editing methods:

1. **Start with AI Edit**: Make broad changes (colors, layout, style)
2. **Fine-tune with Manual Edit**: Add text, precise adjustments, filters

Example workflow:
1. Generate ad with DALL-E
2. Use AI Edit: "Change background to gradient blue to purple"
3. Use Manual Edit: Add promotional text overlay, apply subtle filter
4. Download final result

## Keyboard Shortcuts

When in AI Editor:
- `Esc`: Close editor (same as clicking Close button)
- `Enter`: Submit edit (when in prompt text area)

## Limitations

- Only available for DALL-E models
- Cannot add entirely new objects
- Cannot remove objects completely
- Best for modifications, not radical changes
- Processing takes 10-20 seconds per edit

## FAQ

**Q: Can I use AI Edit with Google Imagen or Nano Banana Pro?**  
A: No, AI editing is exclusive to DALL-E models. Use Manual Edit (Filerobot) for other models.

**Q: How many edits can I make?**  
A: Unlimited, but each edit counts as a DALL-E 2 generation and costs accordingly.

**Q: Can I undo an edit?**  
A: Yes, click "❌ Discard Changes" before clicking "Keep Edited Version".

**Q: Can I edit an uploaded image?**  
A: No, only images generated by the app. For uploaded images, use Manual Edit.

**Q: Does editing work with templates?**  
A: Yes, you can edit template-based generated images.

**Q: Can I save multiple versions?**  
A: Each "Keep Edited Version" saves a new file with timestamp. Previous versions remain saved.

## Support

For issues or questions:
1. Check this guide
2. Review the error message for specific guidance
3. Try the Manual Edit option as alternative
4. Check OpenAI API key configuration

---

**Last Updated**: December 10, 2025  
**Feature Version**: 1.0  
**Compatible Models**: DALL-E 2, DALL-E 3
