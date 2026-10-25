from PIL import Image, ImageDraw, ImageFont

def make(size, path):
    img = Image.new('RGB', (size, size), (11, 18, 32))
    d = ImageDraw.Draw(img)
    # rounded green badge
    pad = size // 8
    d.rounded_rectangle([pad, pad, size-pad, size-pad], radius=size//6, fill=(34, 197, 94))
    # barcode lines
    cx, cy = size//2, size//2
    bw = size // 3
    x0 = cx - bw//2
    y0 = cy - bw//3
    y1 = cy + bw//3
    widths = [4,2,6,2,4,3,5,2,4]
    x = x0
    for w in widths:
        d.rectangle([x, y0, x+w, y1], fill=(5, 46, 22))
        x += w + 3
    img.save(path)
    print('saved', path)

make(192, 'icons/icon-192.png')
make(512, 'icons/icon-512.png')
make(180, 'icons/apple-touch-icon.png')
