"""Generate CipherV4 icon"""
from PIL import Image, ImageDraw, ImageFont

# Create a 256x256 image with transparent background
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw background circle (dark blue/purple gradient effect)
draw.ellipse([10, 10, size-10, size-10], fill='#1a1a2e', outline='#0066cc', width=8)

# Draw inner circle
draw.ellipse([40, 40, size-40, size-40], fill='#16213e', outline='#0066cc', width=4)

# Draw "C4" text for CipherV4
try:
    # Try to use a bold font
    font = ImageFont.truetype("arial.ttf", 100)
    font_bold = ImageFont.truetype("arialbd.ttf", 110)
except:
    font = ImageFont.load_default()
    font_bold = font

# Draw "C4" in the center
text = "C4"
# Get text bounding box
bbox = draw.textbbox((0, 0), text, font=font_bold)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text
x = (size - text_width) // 2
y = (size - text_height) // 2 - 10

# Draw text with glow effect
for offset in range(3, 0, -1):
    alpha = 100 - (offset * 20)
    glow_color = (0, 102, 204, alpha)
    for dx in [-offset, 0, offset]:
        for dy in [-offset, 0, offset]:
            draw.text((x + dx, y + dy), text, font=font_bold, fill=glow_color)

# Draw main text
draw.text((x, y), text, font=font_bold, fill='#00ffff')

# Add small detail - corner accents
corner_size = 30
# Top-left
draw.line([(20, 20), (20, 20+corner_size)], fill='#0066cc', width=6)
draw.line([(20, 20), (20+corner_size, 20)], fill='#0066cc', width=6)
# Top-right
draw.line([(size-20, 20), (size-20, 20+corner_size)], fill='#0066cc', width=6)
draw.line([(size-20, 20), (size-20-corner_size, 20)], fill='#0066cc', width=6)
# Bottom-left
draw.line([(20, size-20), (20, size-20-corner_size)], fill='#0066cc', width=6)
draw.line([(20, size-20), (20+corner_size, size-20)], fill='#0066cc', width=6)
# Bottom-right
draw.line([(size-20, size-20), (size-20, size-20-corner_size)], fill='#0066cc', width=6)
draw.line([(size-20, size-20), (size-20-corner_size, size-20)], fill='#0066cc', width=6)

# Save as ICO file with multiple sizes
img.save('cipher_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("Icon created successfully: cipher_icon.ico")

# Also save as PNG for reference
img.save('cipher_icon.png', format='PNG')
print("PNG preview created: cipher_icon.png")
