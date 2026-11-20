#!/usr/bin/env python3
"""Build the GTA 6 meme for make.fun bounty gta6-meme-x-01.

Scene: Vice City sunset. The make.fun ghost (extracted from the real press-kit
mark) rides in a pink convertible. Joke: launch-day sick day.
Top:    CALLED IN SICK TODAY
        DOCTOR'S NOTE SAYS:
Bottom: LEONIDA
Car door carries make.fun. Output 1024x1024 PNG.
"""
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os
_HERE = os.path.dirname(os.path.abspath(__file__))
MARK = os.path.join(_HERE, "assets", "mark-1024.png")
OUT = os.path.join(_HERE, "meme.png")
W = H = 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def extract_ghost():
    """Flood-fill the ghost out of the press-kit mark.

    The mark is a white ghost (black outline) holding a magenta coin with a
    white star, on a magenta disc. Fill from inside the ghost over white or
    near-black pixels; the magenta disc is the barrier, so the disc's black
    outer ring is never reached. The coin's magenta fill and white star are
    enclosed by the coin's black ring, so they come out as a hole: fill holes
    magenta, then redraw the white star.
    """
    im = Image.open(MARK).convert("RGB")
    px = im.load()
    w, h = im.size
    seen = bytearray(w * h)
    q = deque()
    q.append((500, 500))  # inside the ghost's white body
    seen[500 * w + 500] = 1
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                r, g, b = px[nx, ny]
                if min(r, g, b) > 180 or max(r, g, b) < 110:
                    seen[ny * w + nx] = 1
                    q.append((nx, ny))
    mask = Image.new("L", (w, h), 0)
    mask.putdata([255 if v else 0 for v in seen])
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    ghost = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ghost.paste(im.convert("RGBA"), (0, 0), mask)
    bbox = mask.getbbox()
    print("ghost bbox:", bbox, file=sys.stderr)
    ghost = ghost.crop(bbox)

    # Hole-fill: transparent pixels unreachable from the crop border are
    # inside the coin's ring -> magenta (the coin's fill).
    alpha = ghost.split()[3]
    aw, ah = alpha.size
    apx = alpha.load()
    reach = bytearray(aw * ah)
    q = deque()
    for x in range(aw):
        for y in (0, ah - 1):
            if apx[x, y] == 0 and not reach[y * aw + x]:
                reach[y * aw + x] = 1
                q.append((x, y))
    for y in range(ah):
        for x in (0, aw - 1):
            if apx[x, y] == 0 and not reach[y * aw + x]:
                reach[y * aw + x] = 1
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < aw and 0 <= ny < ah and not reach[ny * aw + nx] \
                    and apx[nx, ny] == 0:
                reach[ny * aw + nx] = 1
                q.append((nx, ny))
    gpx = ghost.load()
    for y in range(ah):
        for x in range(aw):
            if apx[x, y] == 0 and not reach[y * aw + x]:
                gpx[x, y] = (196, 0, 130, 255)
    return ghost


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_palm(d, x, y, s, flip, color):
    """Simple stylised palm silhouette. (x, y) = base of trunk."""
    import math
    # trunk: curved segments
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((x + (55 * t * t) * (1 if not flip else -1), y - 260 * s * t))
    d.line(pts, fill=color, width=int(18 * s), joint="curve")
    tx, ty = pts[-1]
    # fronds: smooth drooping quadratic curves, out then down
    for ang in (-170, -140, -115, -90, -65, -40, -10):
        a = math.radians(ang if not flip else 180 - ang)
        ex = tx + math.cos(a) * 135 * s
        ey = ty + 105 * s
        mx = tx + math.cos(a) * 70 * s
        my = ty - 55 * s
        curve = []
        for i in range(17):
            t = i / 16
            bx = (1 - t) ** 2 * tx + 2 * (1 - t) * t * mx + t * t * ex
            by = (1 - t) ** 2 * ty + 2 * (1 - t) * t * my + t * t * ey
            curve.append((bx, by))
        d.line(curve, fill=color, width=int(12 * s), joint="curve")


def star_points(cx, cy, r_out, r_in, points=5, rot=-90):
    import math
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def text_center(d, y, s, font, fill="white", stroke=6):
    bbox = d.textbbox((0, 0), s, font=font, stroke_width=stroke)
    w = bbox[2] - bbox[0]
    d.text(((W - w) / 2 - bbox[0], y), s, font=font, fill=fill,
           stroke_width=stroke, stroke_fill="black")
    return bbox[3] - bbox[1]


def main():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img, "RGBA")

    # --- sky gradient: purple -> magenta -> orange -> gold ---
    stops = [(0.0, (43, 16, 85)), (0.35, (150, 10, 110)),
             (0.62, (255, 90, 60)), (0.85, (255, 170, 80)),
             (1.0, (255, 209, 102))]
    for y in range(700):
        t = y / 700
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                tt = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
                col = lerp(stops[i][1], stops[i + 1][1], tt)
                break
        d.line([(0, y), (W, y)], fill=col)

    # --- sun + glow ---
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([790 - 130, 390 - 130, 790 + 130, 390 + 130],
               fill=(255, 233, 168, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([790 - 85, 390 - 85, 790 + 85, 390 + 85], fill=(255, 240, 180))

    # --- skyline silhouettes ---
    sky = (26, 11, 46)
    for (x0, x1, top) in [(0, 90, 600), (90, 170, 560), (170, 260, 620),
                          (260, 330, 580), (700, 780, 590), (780, 860, 630),
                          (860, 940, 575), (940, 1024, 615)]:
        d.rectangle([x0, top, x1, 700], fill=sky)
    # two towers with antennae
    d.rectangle([120, 520, 150, 700], fill=sky)
    d.line([(135, 520), (135, 480)], fill=sky, width=4)
    d.rectangle([880, 540, 910, 700], fill=sky)
    d.line([(895, 540), (895, 500)], fill=sky, width=4)

    # --- road ---
    d.rectangle([0, 700, W, H], fill=(36, 26, 46))
    d.rectangle([0, 700, W, 708], fill=(20, 14, 28))

    # --- palms ---
    draw_palm(d, 8, 700, 1.0, False, (20, 8, 31))
    draw_palm(d, 1016, 700, 1.15, True, (20, 8, 31))

    # --- top text ---
    f1 = ImageFont.truetype(BOLD, 62)
    f2 = ImageFont.truetype(BOLD, 56)
    text_center(d, 34, "CALLED IN SICK TODAY", f1)
    text_center(d, 116, "DOCTOR'S NOTE SAYS:", f2)

    # --- ghost in the convertible ---
    ghost = extract_ghost()
    gw, gh = ghost.size
    new_h = 400
    new_w = int(gw * new_h / gh)
    ghost = ghost.resize((new_w, new_h), Image.LANCZOS)
    # redraw the white star on the magenta coin (coin centre in the cropped
    # ghost was ~(567, 260); scale to the resized ghost)
    sc = new_h / gh
    gd2 = ImageDraw.Draw(ghost)
    gd2.polygon(star_points(567 * sc, 260 * sc, 46 * sc, 19 * sc),
                fill=(255, 255, 255, 255))
    gx = (W - new_w) // 2
    gy = 360
    # windshield behind the ghost
    d.polygon([(360, 700), (425, 645), (599, 645), (664, 700)],
              fill=(191, 232, 255), outline="black")
    d.line([(360, 700), (425, 645), (599, 645), (664, 700)],
           fill="black", width=5, joint="curve")
    img.paste(ghost, (gx, gy), ghost)
    d = ImageDraw.Draw(img, "RGBA")

    # --- car body (covers the ghost's lower half: it is riding in it) ---
    d.rounded_rectangle([150, 700, 874, 812], radius=28,
                        fill=(255, 46, 136), outline="black", width=5)
    d.line([(150, 762), (874, 762)], fill=(200, 0, 90), width=4)
    # headlight + taillight
    d.ellipse([838, 724, 866, 748], fill=(255, 244, 180), outline="black",
              width=3)
    d.ellipse([158, 724, 182, 748], fill=(255, 60, 60), outline="black",
              width=3)
    # make.fun on the door
    fdoor = ImageFont.truetype(BOLD, 44)
    tb = d.textbbox((0, 0), "make.fun", font=fdoor)
    dw = tb[2] - tb[0]
    d.text(((W - dw) / 2 - tb[0], 716), "make.fun", font=fdoor, fill="white")
    # wheels
    for cx in (300, 724):
        d.ellipse([cx - 46, 788, cx + 46, 880], fill="black", outline="black")
        d.ellipse([cx - 20, 814, cx + 20, 854], fill=(220, 220, 230),
                  outline="black", width=3)
        d.ellipse([cx - 6, 828, cx + 6, 840], fill="black")

    # --- bottom punchline ---
    f3 = ImageFont.truetype(BOLD, 108)
    text_center(d, 892, "LEONIDA", f3, stroke=8)

    img.save(OUT)
    print("saved", OUT, img.size, file=sys.stderr)


if __name__ == "__main__":
    main()
