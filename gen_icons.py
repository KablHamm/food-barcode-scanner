from PIL import Image, ImageDraw, ImageFilter
import os

SRC = 'assets/apple-source.png'

def make(size, path):
    bg = (11, 18, 32)
    badge = (240, 253, 244)

    img = Image.new('RGB', (size, size), bg)
    d = ImageDraw.Draw(img)
    pad = size // 10
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=size // 5, fill=badge)

    # Load the apple artwork and trim transparent margins
    apple = Image.open(SRC).convert('RGBA')
    apple = apple.crop(apple.getbbox())

    # Scale so the apple is ~62% of the tile height, keeping aspect ratio
    target_h = int(size * 0.62)
    target_w = max(1, round(apple.width * target_h / apple.height))
    apple = apple.resize((target_w, target_h), Image.LANCZOS)
    apple = apple.filter(ImageFilter.UnsharpMask(radius=size / 64, percent=60, threshold=2))

    # Center the apple inside the badge, nudged slightly down for optical balance
    x = (size - target_w) // 2
    y = (size - target_h) // 2 + int(size * 0.01)
    img.paste(apple, (x, y), apple)

    img.save(path)
    print('saved', path)

os.makedirs('icons', exist_ok=True)
make(192, 'icons/icon-192.png')
make(512, 'icons/icon-512.png')
make(180, 'icons/apple-touch-icon.png')
