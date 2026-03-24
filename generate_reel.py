#!/usr/bin/env python3
"""
禅園心斎橋 - 接待フォーカス Instagram リール動画生成スクリプト
9:16 (1080x1920) / 30fps / ~34秒
"""

import subprocess
import os
import math
import struct
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Config ──
W, H = 1080, 1920
FPS = 30
BASE_DIR = '/home/user/0324Zenen-shinsaibashi'
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')
FRAMES_DIR = os.path.join(BASE_DIR, 'frames')
OUTPUT = os.path.join(BASE_DIR, 'reel_settai.mp4')

# Font paths
FONT_MINCHO = os.path.join(FONTS_DIR, 'ZenOldMincho-Bold.ttf')
FONT_MINCHO_REG = os.path.join(FONTS_DIR, 'ZenOldMincho-Regular.ttf')
FONT_SANS = os.path.join(FONTS_DIR, 'NotoSansJP-Variable.ttf')
FONT_SERIF = os.path.join(FONTS_DIR, 'NotoSerifJP-Variable.ttf')

# ── Slide Definitions ──
SLIDES = [
    {
        'image': 'room_entrance.jpg',
        'duration': 4.5,
        'texts': [
            {'text': '心斎橋に\nこんな場所が\nあったのか', 'font': FONT_MINCHO, 'size': 72,
             'pos': 'center', 'delay': 0.5, 'letter_spacing': 12, 'line_height': 1.8},
            {'text': '── 禅園心斎橋 ──', 'font': FONT_SANS, 'size': 32,
             'pos': 'center_below', 'delay': 1.0, 'letter_spacing': 8},
        ],
        'ken_burns': {'start_scale': 1.0, 'end_scale': 1.08, 'start_xy': (0, 0), 'end_xy': (-15, 10)},
    },
    {
        'image': 'bar_counter.jpg',
        'duration': 4.0,
        'texts': [
            {'text': '完全個室と\n専用バーを完備', 'font': FONT_SERIF, 'size': 52,
             'pos': 'bottom', 'delay': 0.4, 'letter_spacing': 14, 'line_height': 1.7},
        ],
        'ken_burns': {'start_scale': 1.05, 'end_scale': 1.0, 'start_xy': (10, -5), 'end_xy': (-5, 5)},
    },
    {
        'image': 'champagne_toast.jpg',
        'duration': 4.2,
        'texts': [
            {'text': '大切なお客様との\n特別なひととき', 'font': FONT_MINCHO, 'size': 56,
             'pos': 'bottom', 'delay': 0.5, 'letter_spacing': 8, 'line_height': 1.6},
        ],
        'ken_burns': {'start_scale': 1.0, 'end_scale': 1.07, 'start_xy': (0, 10), 'end_xy': (10, -10)},
    },
    {
        'image': 'wine_cuisine.jpg',
        'duration': 3.8,
        'texts': [
            {'text': '厳選されたワインと\n季節の懐石', 'font': FONT_SERIF, 'size': 48,
             'pos': 'bottom', 'delay': 0.4, 'letter_spacing': 10, 'line_height': 1.7},
        ],
        'ken_burns': {'start_scale': 1.06, 'end_scale': 1.0, 'start_xy': (-10, 0), 'end_xy': (5, 5)},
    },
    {
        'image': 'dining_scene.jpg',
        'duration': 4.0,
        'texts': [
            {'text': '会話が弾む\n上質な接待', 'font': FONT_MINCHO, 'size': 56,
             'pos': 'bottom', 'delay': 0.5, 'letter_spacing': 8, 'line_height': 1.6},
            {'text': '距離が、近くなる', 'font': FONT_SANS, 'size': 30,
             'pos': 'bottom_sub', 'delay': 0.9, 'letter_spacing': 8},
        ],
        'ken_burns': {'start_scale': 1.0, 'end_scale': 1.09, 'start_xy': (5, 5), 'end_xy': (-10, -5)},
    },
    {
        'image': 'hospitality_serve.jpg',
        'duration': 4.5,
        'texts': [
            {'text': '心を込めた\nおもてなし', 'font': FONT_SERIF, 'size': 52,
             'pos': 'bottom', 'delay': 0.4, 'letter_spacing': 14, 'line_height': 1.7},
            {'text': '丁寧な手仕事が伝わる', 'font': FONT_SANS, 'size': 28,
             'pos': 'bottom_sub', 'delay': 0.8, 'letter_spacing': 6},
        ],
        'ken_burns': {'start_scale': 1.04, 'end_scale': 1.0, 'start_xy': (0, -10), 'end_xy': (10, 5)},
    },
    {
        'image': 'sake_bar_toast.jpg',
        'duration': 4.0,
        'texts': [
            {'text': '食後のひとときも\nこの空間で', 'font': FONT_MINCHO, 'size': 56,
             'pos': 'bottom', 'delay': 0.5, 'letter_spacing': 8, 'line_height': 1.6},
            {'text': '併設バーで余韻を愉しむ', 'font': FONT_SANS, 'size': 28,
             'pos': 'bottom_sub', 'delay': 0.9, 'letter_spacing': 6},
        ],
        'ken_burns': {'start_scale': 1.0, 'end_scale': 1.06, 'start_xy': (-5, 0), 'end_xy': (5, -10)},
    },
    {
        'image': 'room_private.jpg',
        'duration': 5.5,
        'texts': [],  # Store info handled separately
        'ken_burns': {'start_scale': 1.0, 'end_scale': 1.03, 'start_xy': (0, 0), 'end_xy': (0, 0)},
        'is_store_info': True,
        'darken': 0.62,
    },
]

TRANSITION_DURATION = 0.8  # seconds


def load_and_crop_cover(path, target_w, target_h):
    """Load image and crop to cover target aspect ratio."""
    img = Image.open(path).convert('RGB')
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # Image is wider - crop width
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        # Image is taller - crop height
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))

    # Scale up to a large size for Ken Burns (allow zooming without quality loss)
    scale_size = max(target_w, target_h) * 2
    ratio = scale_size / max(img.size)
    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
    img = img.resize(new_size, Image.LANCZOS)
    return img


def apply_ken_burns(img, t, kb):
    """Apply Ken Burns effect: returns a W x H crop from the large image."""
    progress = t  # 0..1
    # Ease in-out
    progress = 0.5 - 0.5 * math.cos(progress * math.pi)

    scale = kb['start_scale'] + (kb['end_scale'] - kb['start_scale']) * progress
    ox = kb['start_xy'][0] + (kb['end_xy'][0] - kb['start_xy'][0]) * progress
    oy = kb['start_xy'][1] + (kb['end_xy'][1] - kb['start_xy'][1]) * progress

    src_w, src_h = img.size
    # Calculate crop region
    crop_w = int(W / scale)
    crop_h = int(H / scale)

    # Scale relative to source image
    ratio = src_w / W
    crop_w = int(crop_w * ratio)
    crop_h = int(crop_h * ratio)

    cx = src_w // 2 + int(ox * ratio)
    cy = src_h // 2 + int(oy * ratio)

    left = max(0, cx - crop_w // 2)
    top = max(0, cy - crop_h // 2)
    right = min(src_w, left + crop_w)
    bottom = min(src_h, top + crop_h)

    # Adjust if hitting edges
    if right - left < crop_w:
        left = max(0, right - crop_w)
    if bottom - top < crop_h:
        top = max(0, bottom - crop_h)

    cropped = img.crop((left, top, right, bottom))
    return cropped.resize((W, H), Image.LANCZOS)


def create_vignette(w, h):
    """Create a vignette overlay."""
    vignette = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    cx, cy = w * 0.52, h * 0.48
    max_r = math.sqrt(cx**2 + cy**2)
    for i in range(0, 80):
        r_ratio = 0.4 + (i / 80) * 0.6
        alpha = int((i / 80) ** 1.5 * 140)
        r = int(max_r * r_ratio)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=None,
            outline=(0, 0, 0, alpha),
            width=int(max_r * 0.02)
        )
    return vignette


def create_bottom_gradient(w, h):
    """Create bottom gradient for text readability."""
    gradient = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    gradient_height = int(h * 0.45)
    for y in range(gradient_height):
        progress = y / gradient_height
        alpha = int(progress ** 1.5 * 180)
        draw.line([(0, h - gradient_height + y), (w, h - gradient_height + y)],
                  fill=(0, 0, 0, alpha))
    return gradient


def draw_text_with_spacing(draw, text, font, x, y, fill, spacing=0, anchor='center'):
    """Draw text with letter spacing, line by line."""
    lines = text.split('\n')
    line_height = font.size * 1.7
    total_height = line_height * len(lines)

    for li, line in enumerate(lines):
        # Calculate line width with spacing
        chars = list(line)
        char_widths = []
        for c in chars:
            bbox = font.getbbox(c)
            char_widths.append(bbox[2] - bbox[0])

        total_width = sum(char_widths) + spacing * (len(chars) - 1) if chars else 0

        if anchor == 'center':
            cx = x - total_width // 2
        elif anchor == 'left':
            cx = x
        else:
            cx = x

        cy = y + li * line_height

        for i, c in enumerate(chars):
            # Shadow (multi-layer for readability)
            draw.text((cx + 3, cy + 3), c, font=font, fill=(0, 0, 0, 180))
            draw.text((cx + 2, cy + 2), c, font=font, fill=(0, 0, 0, 140))
            draw.text((cx + 1, cy + 1), c, font=font, fill=(0, 0, 0, 100))
            # Main text
            draw.text((cx, cy), c, font=font, fill=fill)
            cx += char_widths[i] + spacing

    return total_height


def render_text_overlay(frame_img, slide, t_in_slide, duration):
    """Render text overlays with fade-in animation."""
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if slide.get('is_store_info'):
        render_store_info(draw, overlay, t_in_slide, duration)
    else:
        for tdef in slide['texts']:
            delay = tdef.get('delay', 0.5)
            fade_duration = 0.6

            if t_in_slide < delay:
                continue

            fade_t = min(1.0, (t_in_slide - delay) / fade_duration)
            # Ease out
            fade_t = 1 - (1 - fade_t) ** 2
            alpha = int(255 * fade_t)
            y_offset = int(18 * (1 - fade_t))

            font_size = tdef['size']
            font = ImageFont.truetype(tdef['font'], font_size)
            spacing = tdef.get('letter_spacing', 0)

            fill = (255, 255, 255, alpha)

            pos = tdef['pos']
            if pos == 'center':
                tx, ty = W // 2, H // 2 - 100 + y_offset
                draw_text_with_spacing(draw, tdef['text'], font, tx, ty, fill, spacing, 'center')
            elif pos == 'center_below':
                tx, ty = W // 2, H // 2 + 120 + y_offset
                draw_text_with_spacing(draw, tdef['text'], font, tx, ty, fill, spacing, 'center')
            elif pos == 'center_sub':
                tx, ty = W // 2, H // 2 + 120 + y_offset
                draw_text_with_spacing(draw, tdef['text'], font, tx, ty, fill, spacing, 'center')
            elif pos == 'top_left':
                tx, ty = 80, 240 + y_offset
                draw_text_with_spacing(draw, tdef['text'], font, tx, ty, fill, spacing, 'left')
            elif pos == 'bottom':
                lines = tdef['text'].split('\n')
                line_h = font_size * tdef.get('line_height', 1.6)
                ty = H - 260 - int(line_h * len(lines)) + y_offset
                draw_text_with_spacing(draw, tdef['text'], font, W // 2, ty, fill, spacing, 'center')
            elif pos == 'bottom_sub':
                ty = H - 200 + y_offset
                draw_text_with_spacing(draw, tdef['text'], font, W // 2, ty, fill, spacing, 'center')

    frame_rgba = frame_img.convert('RGBA')
    frame_rgba = Image.alpha_composite(frame_rgba, overlay)
    return frame_rgba.convert('RGB')


def render_store_info(draw, overlay, t_in_slide, duration):
    """Render store information on the final slide."""
    elements = [
        (0.3, 'title', '禅 園'),
        (0.3, 'subtitle', 'ZENEN SHINSAIBASHI'),
        (0.8, 'divider', ''),
        (1.2, 'info', None),
    ]

    for delay, etype, text in elements:
        if t_in_slide < delay:
            continue

        fade_t = min(1.0, (t_in_slide - delay) / 0.7)
        fade_t = 1 - (1 - fade_t) ** 2
        alpha = int(255 * fade_t)
        y_off = int(15 * (1 - fade_t))

        if etype == 'title':
            font = ImageFont.truetype(FONT_MINCHO, 88)
            fill = (255, 255, 255, alpha)
            draw_text_with_spacing(draw, text, font, W // 2, 260 + y_off, fill, 24, 'center')

        elif etype == 'subtitle':
            font = ImageFont.truetype(FONT_SANS, 30)
            fill = (255, 255, 255, int(alpha * 0.8))
            draw_text_with_spacing(draw, text, font, W // 2, 380 + y_off, fill, 12, 'center')

        elif etype == 'divider':
            line_alpha = int(alpha * 0.5)
            draw.line([(W // 2 - 60, 450), (W // 2 + 60, 450)],
                      fill=(255, 255, 255, line_alpha), width=2)

        elif etype == 'info':
            info_items = [
                ('ADDRESS', '〒542-0086', None),
                (None, '大阪府大阪市中央区西心斎橋1-3-3', None),
                (None, 'オー・エム・ホテル日航ビルB2F', None),
                ('TEL', '06-6241-7027', None),
                ('HOURS', 'ランチ 11:30〜14:45（L.O.14:00）', None),
                (None, 'ディナー 17:00〜22:00（L.O.21:00）', None),
                (None, '定休日 不定休（施設に準ずる）', None),
                ('SEATS', '総席数70席 / 宴会最大30名（着席時）', None),
                (None, '全面禁煙', None),
            ]

            y_pos = 500 + y_off
            label_font = ImageFont.truetype(FONT_MINCHO, 24)
            detail_font = ImageFont.truetype(FONT_MINCHO, 30)

            for label, line1, line2 in info_items:
                if label is not None:
                    # Label
                    lfill = (255, 255, 255, int(alpha * 0.55))
                    draw_text_with_spacing(draw, label, label_font, W // 2, y_pos, lfill, 8, 'center')
                    y_pos += 34

                # Detail
                dfill = (255, 255, 255, alpha)
                draw_text_with_spacing(draw, line1, detail_font, W // 2, y_pos, dfill, 3, 'center')
                y_pos += 40
                if line2:
                    draw_text_with_spacing(draw, line2, detail_font, W // 2, y_pos, dfill, 3, 'center')
                    y_pos += 40
                if label is not None:
                    y_pos += 10

            # CTA box
            cta_y = y_pos + 8
            cta_font = ImageFont.truetype(FONT_MINCHO, 28)
            cta_text = 'ご予約はプロフィールリンクから'
            bbox = cta_font.getbbox(cta_text)
            tw = bbox[2] - bbox[0] + 60
            th = bbox[3] - bbox[1] + 26
            rx = W // 2 - tw // 2
            ry = cta_y
            draw.rectangle([rx, ry, rx + tw, ry + th],
                           outline=(255, 255, 255, int(alpha * 0.6)),
                           fill=(255, 255, 255, int(alpha * 0.1)),
                           width=2)
            dfill = (255, 255, 255, alpha)
            draw_text_with_spacing(draw, cta_text, cta_font, W // 2, ry + 5, dfill, 4, 'center')

            # Instagram handle
            handle_font = ImageFont.truetype(FONT_SANS, 26)
            hfill = (255, 255, 255, int(alpha * 0.6))
            draw_text_with_spacing(draw, '@zenen_shinsaibashi', handle_font,
                                   W // 2, cta_y + th + 28, hfill, 4, 'center')


def generate_reel():
    """Main generation function."""
    # Clean/create frames directory
    if os.path.exists(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
    os.makedirs(FRAMES_DIR)

    # Pre-load images
    print("Loading images...")
    images = {}
    for slide in SLIDES:
        img_path = os.path.join(ASSETS_DIR, slide['image'])
        images[slide['image']] = load_and_crop_cover(img_path, W, H)
        print(f"  Loaded {slide['image']}: {images[slide['image']].size}")

    # Pre-create overlays
    print("Creating overlays...")
    vignette = create_vignette(W, H)
    bottom_grad = create_bottom_gradient(W, H)

    # Calculate timing
    total_frames = 0
    slide_timings = []
    for i, slide in enumerate(SLIDES):
        start_time = sum(s['duration'] for s in SLIDES[:i])
        slide_timings.append({
            'start': start_time,
            'end': start_time + slide['duration'],
            'duration': slide['duration'],
        })
        total_frames = int((start_time + slide['duration']) * FPS)

    total_duration = sum(s['duration'] for s in SLIDES)
    total_frames = int(total_duration * FPS)
    print(f"Total duration: {total_duration}s, frames: {total_frames}")

    # Generate frames
    print("Generating frames...")
    frame_num = 0
    for frame_idx in range(total_frames):
        current_time = frame_idx / FPS

        # Find current slide
        slide_idx = 0
        for i, timing in enumerate(slide_timings):
            if timing['start'] <= current_time < timing['end']:
                slide_idx = i
                break
        else:
            slide_idx = len(SLIDES) - 1

        slide = SLIDES[slide_idx]
        timing = slide_timings[slide_idx]
        t_local = current_time - timing['start']
        t_norm = t_local / timing['duration']  # 0..1

        # Render base with Ken Burns
        base_img = images[slide['image']]
        frame = apply_ken_burns(base_img, t_norm, slide['ken_burns'])

        # Apply darkening for store info
        if slide.get('darken'):
            dark = Image.new('RGB', (W, H), (0, 0, 0))
            frame = Image.blend(frame, dark, slide['darken'])
            frame = frame.filter(ImageFilter.GaussianBlur(radius=2))

        # Apply vignette and gradient
        frame_rgba = frame.convert('RGBA')
        frame_rgba = Image.alpha_composite(frame_rgba, vignette)
        frame_rgba = Image.alpha_composite(frame_rgba, bottom_grad)
        frame = frame_rgba.convert('RGB')

        # Crossfade transition
        trans_frames = int(TRANSITION_DURATION * FPS)
        if slide_idx > 0:
            time_into_slide = t_local
            if time_into_slide < TRANSITION_DURATION:
                # We're in a transition
                prev_slide = SLIDES[slide_idx - 1]
                prev_timing = slide_timings[slide_idx - 1]
                prev_t_norm = 1.0  # end of previous slide

                prev_frame = apply_ken_burns(images[prev_slide['image']], prev_t_norm,
                                             prev_slide['ken_burns'])
                if prev_slide.get('darken'):
                    dark = Image.new('RGB', (W, H), (0, 0, 0))
                    prev_frame = Image.blend(prev_frame, dark, prev_slide['darken'])

                prev_rgba = prev_frame.convert('RGBA')
                prev_rgba = Image.alpha_composite(prev_rgba, vignette)
                prev_rgba = Image.alpha_composite(prev_rgba, bottom_grad)
                prev_frame = prev_rgba.convert('RGB')

                blend_t = time_into_slide / TRANSITION_DURATION
                # Ease in-out
                blend_t = 0.5 - 0.5 * math.cos(blend_t * math.pi)
                frame = Image.blend(prev_frame, frame, blend_t)

        # Render text
        frame = render_text_overlay(frame, slide, t_local, timing['duration'])

        # Save frame
        frame_path = os.path.join(FRAMES_DIR, f'frame_{frame_idx:05d}.jpg')
        frame.save(frame_path, 'JPEG', quality=92)

        if frame_idx % (FPS * 2) == 0:
            print(f"  Frame {frame_idx}/{total_frames} ({current_time:.1f}s)")

        frame_num += 1

    print(f"Generated {frame_num} frames")

    # Encode with ffmpeg
    print("Encoding video...")
    cmd = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', os.path.join(FRAMES_DIR, 'frame_%05d.jpg'),
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-vf', 'format=yuv420p',
        OUTPUT
    ]
    subprocess.run(cmd, check=True)
    print(f"\nDone! Output: {OUTPUT}")
    print(f"File size: {os.path.getsize(OUTPUT) / 1024 / 1024:.1f} MB")

    # Cleanup frames
    shutil.rmtree(FRAMES_DIR)
    print("Cleaned up frames directory")


if __name__ == '__main__':
    generate_reel()
