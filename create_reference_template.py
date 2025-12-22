"""
Quick script to generate a reference image with placeholder positions
Run this to create a test reference template
"""
from PIL import Image, ImageDraw, ImageFont

# Create canvas
width, height = 1920, 1080
img = Image.new('RGB', (width, height), color='#2a2a2a')
draw = ImageDraw.Draw(img)

# Try to use a decent font, fallback to default
try:
    font_large = ImageFont.truetype("arial.ttf", 80)
    font_medium = ImageFont.truetype("arial.ttf", 60)
    font_small = ImageFont.truetype("arial.ttf", 40)
except:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Define placeholder zones with boxes
zones = [
    # (x, y, width, height, label, font)
    (100, 80, 200, 120, "[LOGO]", font_small),
    (width//2 - 200, 200, 400, 100, "[BRAND NAME]", font_large),
    (width//2 - 400, height//2 - 80, 800, 160, "[MAIN MESSAGE]", font_large),
    (width//2 - 150, height - 200, 300, 80, "[CTA]", font_small),
]

# Draw zones
for x, y, w, h, label, font in zones:
    # Draw rectangle
    draw.rectangle([x, y, x + w, y + h], outline='white', width=3)
    
    # Draw label centered in box
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = x + (w - text_width) // 2
    text_y = y + (h - text_height) // 2
    draw.text((text_x, text_y), label, fill='white', font=font)

# Add instruction text at bottom
instruction = "Reference Template - Use this layout for AI generation"
draw.text((width//2 - 300, height - 50), instruction, fill='#888888', font=font_small)

# Save
output_path = "reference_layout_test.png"
img.save(output_path)
print(f"✅ Reference image created: {output_path}")
print(f"📏 Size: {width}x{height}")
print(f"📍 Zones: LOGO (top-left), BRAND NAME (upper center), MAIN MESSAGE (center), CTA (bottom)")
print(f"\n🎯 Next: Upload this as a reference image in your app and test generation!")
