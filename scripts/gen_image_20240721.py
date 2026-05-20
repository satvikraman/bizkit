"""
Image generator for blog post: "The Watchdog That Looked Away"
Theme: Auditor failure, Evergrande, Big Four in China
Output: blog/20240721/title_20240721.png  (1400 x 920 pre-resize)
"""
import math
from PIL import Image, ImageDraw, ImageFont

# ── constants ──────────────────────────────────────────────────────────────
W, H = 1400, 920

BG_DARK   = (8, 14, 30)
BG_MID    = (12, 22, 50)
GOLD      = (245, 193, 62)
GREEN_OK  = (39, 174, 96)
RED       = (231, 76, 60)
ORANGE    = (230, 126, 34)
CYAN      = (0, 188, 212)
WHITE     = (255, 255, 255)
OFF_WHITE = (220, 230, 245)
STAMP_RIM = (245, 193, 62)

FONT_SFNS     = "/System/Library/Fonts/SFNS.ttf"
FONT_SFNS_IT  = "/System/Library/Fonts/SFNSItalic.ttf"

def load(size):
    return ImageFont.truetype(FONT_SFNS, size)

def load_it(size):
    try:
        return ImageFont.truetype(FONT_SFNS_IT, size)
    except Exception:
        return load(size)

# ── helpers ────────────────────────────────────────────────────────────────
def draw_rounded_rect(draw, box, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                           outline=outline, width=width)

def draw_text_centered(draw, text, cx, cy, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)

def draw_text_arc(draw, text, cx, cy, radius, start_deg, font, fill):
    """Draw text characters spaced around an arc."""
    n = len(text)
    span = math.radians(60)
    step = span / max(n - 1, 1)
    mid = math.radians(start_deg)
    for i, ch in enumerate(text):
        angle = mid - span / 2 + i * step
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        bbox = draw.textbbox((0, 0), ch, font=font)
        cw = bbox[2] - bbox[0]
        ch_h = bbox[3] - bbox[1]
        draw.text((x - cw // 2, y - ch_h // 2), ch, font=font, fill=fill)

def alpha_paste(base, overlay_color, box, alpha=80):
    """Paste a semi-transparent rectangle onto base (RGBA mode assumed)."""
    ov = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]),
                   (*overlay_color, alpha))
    base.paste(ov, (box[0], box[1]), ov)

# ── canvas ─────────────────────────────────────────────────────────────────
img = Image.new("RGBA", (W, H), (*BG_DARK, 255))
draw = ImageDraw.Draw(img)

# gradient background (subtle)
for y in range(H):
    t = y / H
    r = int(BG_DARK[0] + (BG_MID[0] - BG_DARK[0]) * t)
    g = int(BG_DARK[1] + (BG_MID[1] - BG_DARK[1]) * t)
    b = int(BG_DARK[2] + (BG_MID[2] - BG_DARK[2]) * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

# faint grid lines
for x in range(0, W, 60):
    draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 12), width=1)
for y in range(0, H, 60):
    draw.line([(0, y), (W, y)], fill=(255, 255, 255, 12), width=1)

# ── floating background numbers (faint) ───────────────────────────────────
faint_items = [
    ("$78B", 70, 210, 16, (255,255,255,22)),
    ("¥4.2B", 700, 800, 22, (255,255,255,20)),
    ("14 YRS", 1150, 120, 18, (255,255,255,20)),
    ("$300B", 1050, 750, 22, (255,255,255,20)),
    ("90%", 300, 820, 24, (255,255,255,18)),
    ("0 FLAGS", 900, 200, 18, (255,255,255,22)),
    ("¥1B FINE", 180, 730, 18, (255,255,255,20)),
]
for text, x, y, size, col in faint_items:
    f = load(size)
    draw.text((x, y), text, font=f, fill=col)

# ═══════════════════════════════════════════════════════════════════════════
#  LEFT SECTION: The broken audit stamp
# ═══════════════════════════════════════════════════════════════════════════
SC_X, SC_Y, SR = 370, 490, 260   # stamp center x, y, radius

# outer glow ring
for r_off in range(30, 0, -6):
    alpha = int(60 * (1 - r_off / 30))
    glow_col = (*GOLD, alpha)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(ov)
    ov_draw.ellipse(
        [SC_X - SR - r_off, SC_Y - SR - r_off,
         SC_X + SR + r_off, SC_Y + SR + r_off],
        outline=glow_col, width=3
    )
    img = Image.alpha_composite(img, ov)
    draw = ImageDraw.Draw(img)

# serrated outer rim (dotted circle effect)
for angle_deg in range(0, 360, 8):
    a = math.radians(angle_deg)
    rx = SC_X + (SR + 16) * math.cos(a)
    ry = SC_Y + (SR + 16) * math.sin(a)
    draw.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], fill=GOLD)

# main stamp circle
draw.ellipse([SC_X - SR, SC_Y - SR, SC_X + SR, SC_Y + SR],
             fill=(14, 24, 55), outline=GOLD, width=6)

# inner circle border
draw.ellipse([SC_X - SR + 22, SC_Y - SR + 22,
              SC_X + SR - 22, SC_Y + SR - 22],
             outline=GOLD, width=2)

# "APPROVED" arc text at top of stamp
arc_font = load(30)
approved_text = "A P P R O V E D"
n = len(approved_text)
arc_r = SR - 40
for i, ch in enumerate(approved_text):
    angle = math.radians(-135 + i * (90 / max(n - 1, 1)))
    ax = SC_X + arc_r * math.cos(angle)
    ay = SC_Y + arc_r * math.sin(angle)
    bbox = draw.textbbox((0, 0), ch, font=arc_font)
    cw = bbox[2] - bbox[0]
    ch_h = bbox[3] - bbox[1]
    draw.text((ax - cw // 2, ay - ch_h // 2), ch, font=arc_font, fill=GREEN_OK)

# "PwC  AUDIT" arc text at bottom
pwc_text = "P w C   A U D I T"
n2 = len(pwc_text)
for i, ch in enumerate(pwc_text):
    angle = math.radians(45 + i * (90 / max(n2 - 1, 1)))
    ax = SC_X + arc_r * math.cos(angle)
    ay = SC_Y + arc_r * math.sin(angle)
    bbox = draw.textbbox((0, 0), ch, font=arc_font)
    cw = bbox[2] - bbox[0]
    ch_h = bbox[3] - bbox[1]
    draw.text((ax - cw // 2, ay - ch_h // 2), ch, font=arc_font, fill=GOLD)

# big checkmark in the stamp center
ck_font = load(200)
draw_text_centered(draw, "✓", SC_X, SC_Y - 15, ck_font, GREEN_OK)

# year band across center of stamp
band_y = SC_Y + 80
draw.rectangle([SC_X - SR + 30, band_y - 18, SC_X + SR - 30, band_y + 18],
               fill=GOLD)
yr_font = load(22)
draw_text_centered(draw, "14  YEARS  ·  ZERO  FLAGS", SC_X, band_y, yr_font,
                   (8, 14, 30))

# ── crack lines over the stamp ─────────────────────────────────────────────
crack_data = [
    # (start_offset_from_center_x, y, end_x_offset, end_y, width)
    (-20, SC_Y - 80, SC_X + 130, SC_Y + 200, 4),
    (30,  SC_Y - 180, SC_X - 160, SC_Y + 180, 3),
    (-60, SC_Y + 50,  SC_X + 200, SC_Y - 100, 2),
    (80,  SC_Y + 100, SC_X - 100, SC_Y - 220, 2),
]
for sx_off, sy, ex, ey, lw in crack_data:
    sx = SC_X + sx_off
    mid_x = (sx + ex) // 2 + 25
    mid_y = (sy + ey) // 2 - 25
    draw.line([(sx, sy), (mid_x, mid_y), (ex, ey)],
              fill=(*RED, 210), width=lw)
    # small branch
    draw.line([(mid_x, mid_y),
               (mid_x + 30, mid_y + 50)],
              fill=(*RED, 150), width=max(lw - 1, 1))

# ═══════════════════════════════════════════════════════════════════════════
#  CENTER DIVIDER
# ═══════════════════════════════════════════════════════════════════════════
div_x = 700
for i in range(0, H, 20):
    alpha = 60 if (i // 20) % 2 == 0 else 20
    draw.line([(div_x, i), (div_x, i + 12)],
              fill=(255, 255, 255, alpha), width=1)

# ═══════════════════════════════════════════════════════════════════════════
#  RIGHT SECTION: Bar chart — Reported vs Reality
# ═══════════════════════════════════════════════════════════════════════════
CHART_X = 780         # left edge of chart area
CHART_W = 550         # chart width
CHART_BASELINE = 740  # y of x-axis
CHART_TOP = 220       # y of tallest bar top

chart_title_font = load(26)
draw_text_centered(draw, "EVERGRANDE  REVENUE  2016 – 2020",
                   CHART_X + CHART_W // 2, 190, chart_title_font, OFF_WHITE)

BAR_W = 160
GAP   = 80

# bar 1: Reported (tall, vivid green-yellow gradient)
b1_x = CHART_X + 80
b1_h = CHART_BASELINE - CHART_TOP       # full height
b1_top = CHART_TOP

for row in range(b1_h):
    t = row / b1_h
    r = int(39  + (245 - 39)  * t)
    g = int(174 + (193 - 174) * t)
    b = int(96  + (62  - 96)  * t)
    draw.rectangle([b1_x, b1_top + row, b1_x + BAR_W, b1_top + row + 1],
                   fill=(r, g, b, 255))

# bar 1 top label
lbl_font = load(28)
draw_text_centered(draw, "$353B", b1_x + BAR_W // 2, b1_top - 25,
                   lbl_font, GREEN_OK)

# bar 2: Reality (shorter, red)
b2_x = b1_x + BAR_W + GAP
reality_frac = 0.44     # ~$275B vs $353B
b2_h = int(b1_h * reality_frac)
b2_top = CHART_BASELINE - b2_h

for row in range(b2_h):
    t = row / b2_h
    r = int(231 + (180 - 231) * t)
    g = int(76  + (30  - 76)  * t)
    b = int(60  + (30  - 60)  * t)
    draw.rectangle([b2_x, b2_top + row, b2_x + BAR_W, b2_top + row + 1],
                   fill=(r, g, b, 255))

draw_text_centered(draw, "$275B", b2_x + BAR_W // 2, b2_top - 25,
                   lbl_font, RED)

# x-axis line
draw.line([(CHART_X + 40, CHART_BASELINE),
           (CHART_X + CHART_W - 40, CHART_BASELINE)],
          fill=OFF_WHITE, width=3)

# x-axis labels
lbl_s_font = load(24)
draw_text_centered(draw, "REPORTED", b1_x + BAR_W // 2, CHART_BASELINE + 30,
                   lbl_s_font, OFF_WHITE)
draw_text_centered(draw, "ACTUAL", b2_x + BAR_W // 2, CHART_BASELINE + 30,
                   lbl_s_font, OFF_WHITE)

# "$78B HIDDEN" gap annotation
gap_mid_y = (b1_top + b2_top) // 2
annot_x = b1_x + BAR_W + 5
annot_font = load(22)

# brace lines
draw.line([(annot_x + BAR_W - 5, b1_top),
           (annot_x + BAR_W + 30, b1_top)], fill=ORANGE, width=2)
draw.line([(annot_x + BAR_W - 5, b2_top),
           (annot_x + BAR_W + 30, b2_top)], fill=ORANGE, width=2)
draw.line([(annot_x + BAR_W + 30, b1_top),
           (annot_x + BAR_W + 30, b2_top)], fill=ORANGE, width=2)

badge_box = [annot_x + BAR_W + 40, gap_mid_y - 30,
             annot_x + BAR_W + 200, gap_mid_y + 30]
draw_rounded_rect(draw, badge_box, 8, RED, outline=ORANGE, width=2)
draw_text_centered(draw, "$78B  HIDDEN",
                   (badge_box[0] + badge_box[2]) // 2,
                   (badge_box[1] + badge_box[3]) // 2,
                   annot_font, WHITE)

# ═══════════════════════════════════════════════════════════════════════════
#  TOP HEADER BAND
# ═══════════════════════════════════════════════════════════════════════════
header_alpha = Image.new("RGBA", (W, H), (0, 0, 0, 0))
header_draw  = ImageDraw.Draw(header_alpha)
header_draw.rectangle([0, 0, W, 115], fill=(5, 10, 25, 210))
img = Image.alpha_composite(img, header_alpha)
draw = ImageDraw.Draw(img)

title_font = load(62)
draw_text_centered(draw, "THE  WATCHDOG  THAT  LOOKED  AWAY",
                   W // 2, 45, title_font, WHITE)

sub_font = load(26)
draw_text_centered(draw,
                   "How the Big Four Failed Evergrande — and What It Cost China",
                   W // 2, 90, sub_font, GOLD)

# ═══════════════════════════════════════════════════════════════════════════
#  BOTTOM STRIP
# ═══════════════════════════════════════════════════════════════════════════
strip_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
s_draw   = ImageDraw.Draw(strip_ov)
for x in range(W):
    t = x / W
    r = int(180 + (231 - 180) * t)
    g = int(30  + (76  - 30)  * t)
    b = int(30  + (60  - 30)  * t)
    s_draw.line([(x, H - 55), (x, H)], fill=(r, g, b, 220))
img = Image.alpha_composite(img, strip_ov)
draw = ImageDraw.Draw(img)

stat_font = load(28)
stats_text = "PwC · 14 Years · $78B Hidden · ¥1B Fine · Big Four Under Fire"
draw_text_centered(draw, stats_text, W // 2, H - 27, stat_font, WHITE)

# ═══════════════════════════════════════════════════════════════════════════
#  LEFT PANEL LABEL
# ═══════════════════════════════════════════════════════════════════════════
label_font = load(22)
draw_text_centered(draw, "THE  AUDIT  SEAL", SC_X, SC_Y - SR - 35,
                   label_font, OFF_WHITE)

# ─── save ──────────────────────────────────────────────────────────────────
out_path = "blog/20240721/title_20240721.png"
img.convert("RGB").save(out_path, "PNG")
print(f"Saved: {out_path}")
