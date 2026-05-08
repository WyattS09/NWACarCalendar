from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

FONTS_DIR = "static/fonts"
OUTPUT_DIR = "static/images/cards"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)
    except:
        return ImageFont.load_default()

def generate_minimal_card(event, output_filename):
    W, H = 1080, 1080

    # Base image
    if event.image_filename:
        img_path = os.path.join("static/images", event.image_filename)
        try:
            bg = Image.open(img_path).convert("RGB")
            bg = bg.resize((W, H), Image.LANCZOS)
        except:
            bg = Image.new("RGB", (W, H), (15, 15, 15))
    else:
        bg = Image.new("RGB", (W, H), (15, 15, 15))

    # Dark gradient overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    for i in range(H):
        alpha = int(120 + (i / H) * 160)
        draw_overlay.line([(0, i), (W, i)], fill=(0, 0, 0, alpha))

    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(bg)

    # Fonts
    font_title = load_font("BebasNeue.ttf", 160)
    font_sub = load_font("Inter-Bold.ttf", 42)
    font_type = load_font("Inter-Bold.ttf", 32)
    font_credit = load_font("Inter-Regular.ttf", 28)

    # Accent bar
    draw.rectangle([(80, 620), (160, 628)], fill=(74, 158, 255))

    # Event type
    draw.text((80, 640), event.event_type.upper(), font=font_type, fill=(74, 158, 255))

    # Event title — wrap if long
    title = event.title.upper()
    draw.text((80, 690), title, font=font_title, fill=(255, 255, 255))

    # Date and time
    date_str = f"{event.date}  ·  {event.time}"
    draw.text((80, 880), date_str, font=font_sub, fill=(220, 220, 220))

    # Location
    draw.text((80, 940), event.location.upper(), font=font_sub, fill=(220, 220, 220))

    # Instagram handle
    if event.instagram:
        draw.text((80, 1010), f"@{event.instagram}", font=font_credit, fill=(74, 158, 255))

    # NWA Car Events credit
    draw.text((W - 80, 1010), "NWACAREVENTS.COM", font=font_credit, fill=(150, 150, 150),
              anchor="ra")

    # Save
    out_path = os.path.join(OUTPUT_DIR, output_filename)
    bg.convert("RGB").save(out_path, "JPEG", quality=95)
    return out_path


def generate_detailed_card(event, output_filename):
    W, H = 1080, 1080

    # Top photo section (60% of card)
    PHOTO_H = 620

    if event.image_filename:
        img_path = os.path.join("static/images", event.image_filename)
        try:
            photo = Image.open(img_path).convert("RGB")
            photo = photo.resize((W, PHOTO_H), Image.LANCZOS)
        except:
            photo = Image.new("RGB", (W, PHOTO_H), (20, 20, 20))
    else:
        photo = Image.new("RGB", (W, PHOTO_H), (20, 20, 20))

    # Gradient on bottom of photo
    photo_rgba = photo.convert("RGBA")
    grad = Image.new("RGBA", (W, PHOTO_H), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(grad)
    for i in range(PHOTO_H):
        alpha = int((i / PHOTO_H) ** 2 * 200)
        grad_draw.line([(0, i), (W, i)], fill=(0, 0, 0, alpha))
    photo_rgba = Image.alpha_composite(photo_rgba, grad)

    # Info panel (bottom 40%)
    panel = Image.new("RGB", (W, H - PHOTO_H), (22, 22, 22))
    panel_draw = ImageDraw.Draw(panel)

    # Accent line at top of panel
    panel_draw.rectangle([(0, 0), (W, 5)], fill=(74, 158, 255))

    # Fonts
    font_title = load_font("BebasNeue.ttf", 100)
    font_label = load_font("Inter-Bold.ttf", 26)
    font_value = load_font("Inter-Bold.ttf", 34)
    font_type = load_font("Inter-Bold.ttf", 28)
    font_credit = load_font("Inter-Regular.ttf", 24)

    # Event type badge
    panel_draw.rectangle([(60, 30), (60 + 260, 72)], fill=(74, 158, 255))
    panel_draw.text((80, 34), event.event_type.upper(), font=font_type, fill=(255, 255, 255))

    # Event title
    panel_draw.text((60, 80), event.title.upper(), font=font_title, fill=(255, 255, 255))

    # Divider
    panel_draw.rectangle([(60, 195), (W - 60, 198)], fill=(50, 50, 50))

    # Info grid
    info_y = 215
    col1_x = 60
    col2_x = 560

    # Date
    panel_draw.text((col1_x, info_y), "DATE", font=font_label, fill=(74, 158, 255))
    panel_draw.text((col1_x, info_y + 32), event.date, font=font_value, fill=(240, 240, 240))

    # Time
    panel_draw.text((col2_x, info_y), "TIME", font=font_label, fill=(74, 158, 255))
    panel_draw.text((col2_x, info_y + 32), event.time, font=font_value, fill=(240, 240, 240))

    # Location
    panel_draw.text((col1_x, info_y + 100), "LOCATION", font=font_label, fill=(74, 158, 255))
    panel_draw.text((col1_x, info_y + 132), event.location, font=font_value, fill=(240, 240, 240))

    # Instagram
    if event.instagram:
        panel_draw.text((col2_x, info_y + 100), "INSTAGRAM", font=font_label, fill=(74, 158, 255))
        panel_draw.text((col2_x, info_y + 132), f"@{event.instagram}", font=font_value, fill=(240, 240, 240))

    # Credit
    panel_draw.text((W - 60, H - PHOTO_H - 30), "NWACAREVENTS.COM",
                    font=font_credit, fill=(100, 100, 100), anchor="ra")

    # Combine
    final = Image.new("RGB", (W, H))
    final.paste(photo_rgba.convert("RGB"), (0, 0))
    final.paste(panel, (0, PHOTO_H))

    out_path = os.path.join(OUTPUT_DIR, output_filename)
    final.save(out_path, "JPEG", quality=95)
    return out_path