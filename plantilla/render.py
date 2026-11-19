import json, math, os, sys, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

W, H, FPS = 1080, 1920, 30
D = os.getcwd(); F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
S = json.load(open(f"{D}/script.json")); CD = json.load(open(f"{D}/chunkdur.json"))
LEAD, GAP, TAIL = 0.35, 0.28, 0.65
# chunk start times (scene-local) and scene durations
CS, SD = [], []
for i, row in enumerate(CD):
    t = LEAD; st = []
    for d in row: st.append(t); t += d + GAP
    CS.append(st); SD.append(t - GAP + TAIL + (1.4 if i == len(CD) - 1 else 0))

INK = (26, 24, 22); RED = (226, 58, 46); GREY = (150, 145, 138); CREAM = (236, 232, 225); WHITE = (255, 255, 255)

def font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        try: f.set_variation_by_name(var)
        except Exception: pass
    return f
ANTON = lambda s: font(f"{F}/Anton-Regular.ttf", s)
SERIF = lambda s: font(f"{F}/InstrumentSerif-Italic.ttf", s)
INTER = lambda s, v="SemiBold": font(f"{F}/Inter-VF.ttf", s, v)
MONO = lambda s, v="Medium": font(f"{F}/JetBrainsMono-VF.ttf", s, v)

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def bo(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------- background ----------
def make_bg():
    rng = np.random.default_rng(3)
    a = np.ones((H, W, 3), np.float32) * np.array(CREAM, np.float32)
    a += rng.normal(0, 3.0, (H, W, 1))
    y = np.linspace(-1, 1, H)[:, None, None]; x = np.linspace(-1, 1, W)[None, :, None]
    a *= 1 - 0.06 * (x ** 2 + y ** 2)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for gx in range(0, W, 54):
        for gy in range(0, H, 54): d.point((gx, gy), fill=(205, 200, 192, 255))
    return im
BG = make_bg()

# ---------- sprite helpers ----------
_c = {}
def txt(s, f, fill, stroke=0, sf_=None):
    k = (s, id(f), fill, stroke)
    if k in _c: return _c[k]
    bb = f.getbbox(s, stroke_width=stroke); p = 12
    im = Image.new("RGBA", (bb[2] - bb[0] + 2 * p, bb[3] - bb[1] + 2 * p), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((p - bb[0], p - bb[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sf_ or fill)
    _c[k] = im; return im

def paste(c, spr, cx, cy, sc=1., al=1., rot=0., anchor="c"):
    if al <= 0.01 or sc <= 0.01: return
    if rot: spr = spr.rotate(rot, Image.BICUBIC, expand=True)
    if abs(sc - 1) > 0.01: spr = spr.resize((max(1, int(spr.width * sc)), max(1, int(spr.height * sc))), Image.BICUBIC)
    if al < 0.99:
        spr = spr.copy(); spr.putalpha(spr.getchannel("A").point(lambda v: int(v * al)))
    x = cx - spr.width / 2 if anchor == "c" else cx
    c.alpha_composite(spr, (int(x), int(cy - spr.height / 2)))

def card(w, h, r=28, fill=WHITE):
    k = ("card", w, h, fill)
    if k in _c: return _c[k]
    im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([30, 40, 30 + w, 40 + h], r, fill=(60, 40, 20, 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).rounded_rectangle([30, 30, 30 + w, 30 + h], r, fill=fill)
    _c[k] = im; return im

def stamp(c, s, cx, cy, t0, t, rot=-8, size=74):
    if t < t0: return
    k = ("stamp", s, size)
    if k not in _c:
        f = ANTON(size); bb = f.getbbox(s)
        w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 40
        im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([10, 10, 10 + w, 10 + h], 14, outline=RED, width=7, fill=(255, 250, 245, 235))
        d.text((40 - bb[0], 30 - bb[1]), s, font=f, fill=RED)
        _c[k] = im
    p = (t - t0) / 0.22
    paste(c, _c[k], cx, cy, sc=1.8 - 0.8 * eo(p), al=clamp(p * 2), rot=rot)

def badge(c, n, cx, cy, t0, t):
    if t < t0: return
    k = ("badge", n)
    if k not in _c:
        im = Image.new("RGBA", (96, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([4, 4, 92, 92], 16, fill=INK)
        f = ANTON(62); bb = f.getbbox(str(n)); d.text((48 - (bb[0] + bb[2]) / 2, 48 - (bb[1] + bb[3]) / 2), str(n), font=f, fill=WHITE)
        _c[k] = im
    paste(c, _c[k], cx, cy, sc=bo((t - t0) / 0.35), rot=-6 * (1 - eo((t - t0) / 0.4)))

# ---------- top caption with word reveal ----------
CAPF = INTER(56, "SemiBold"); EMF = SERIF(70)
def parse(chunk):
    out = []; emph = False
    for tok in chunk.replace("*", " * ").split():
        if tok == "*": emph = not emph; continue
        if out and all(ch in ".,?!:" for ch in tok): out[-1] = (out[-1][0] + tok, out[-1][1]); continue
        out.append((tok, emph))
    return out
def draw_caption(c, i, t):
    cur = None
    for j, st in enumerate(CS[i]):
        if t >= st - 0.05: cur = j
    if cur is None: return
    words = parse(S[i]["chunks"][cur]); st = CS[i][cur]; d = CD[i][cur]
    total = sum(len(w) + 1 for w, _ in words); acc = 0
    # layout with wrapping
    x0, maxw = 70, W - 140; lines = [[]]; lw = 0
    for w, e in words:
        f = EMF if e else CAPF; ww = f.getlength(w + " ")
        if lw + ww > maxw and lines[-1]: lines.append([]); lw = 0
        lines[-1].append((w, e, ww)); lw += ww
    dr = ImageDraw.Draw(c); y = 150; k = 0
    for ln in lines:
        x = x0
        for w, e, ww in ln:
            ws = st + d * acc / total; acc += len(w) + 1
            p = clamp((t - ws) / 0.12)
            col = RED if e else INK
            col = tuple(int(GREY[q] * 0.35 + 236 * 0.65 + (col[q] - (GREY[q] * 0.35 + 236 * 0.65)) * p) for q in range(3))
            if e: dr.text((x, y - 10), w, font=EMF, fill=col)
            else: dr.text((x, y), w, font=CAPF, fill=col)
            x += ww
        y += 76

def header(c, i, t):
    s = S[i]
    al = eo((t - 0.05) / 0.3)
    paste(c, txt(s["label"], MONO(30), (140, 120, 110)), 70, 380, al=al, anchor="l")
    y = 470
    for li, line in enumerate(s["title"]):
        t0 = 0.12 + li * 0.15; p = (t - t0) / 0.35
        if p <= 0: continue
        parts = [(line[0], INK)] + ([(line[2], RED)] if len(line) > 2 else [])
        x = 70; yo = 40 * (1 - eo(p))
        for ptxt, col in parts:
            if not ptxt: continue
            spr = txt(ptxt, ANTON(132), col)
            paste(c, spr, x - 12, y + yo + 12, al=clamp(p * 2), anchor="l"); x += spr.width - 24
        if li == 0: badge(c, s["n"], 980, y + 10, 0.3, t)
        y += 150

# ---------- mascot (original: cardboard box) ----------
VENV = None
def mouth_open(gt):
    if VENV is None: return 0
    k = int(gt * 100)
    return float(VENV[k]) if 0 <= k < len(VENV) else 0
def mascot(c, t, gt, cx=850, cy=1700, point=True, wave=False):
    bob = 8 * math.sin(gt * 3.2); cy += bob
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bw, bh = 300, 260; L, T = cx - bw / 2, cy - bh / 2
    # shadow
    d.ellipse([cx - 170, cy + bh / 2 + 10 - bob, cx + 170, cy + bh / 2 + 44 - bob], fill=(80, 60, 40, 50))
    # arm
    if wave:
        ang = math.radians(-60 + 25 * math.sin(gt * 9))
        sx, sy = L + bw - 10, T + 120
        ex, ey = sx + 120 * math.cos(ang) * -1 * -1, sy + 120 * math.sin(ang)
        d.line([(sx, sy), (ex, ey)], fill=(160, 112, 62), width=26); d.ellipse([ex - 22, ey - 22, ex + 22, ey + 22], fill=(214, 168, 112))
    if point:
        sx, sy = L + 20, T + 120; ex, ey = sx - 150, sy - 120 + 10 * math.sin(gt * 4)
        d.line([(sx, sy), (ex, ey)], fill=(160, 112, 62), width=26); d.ellipse([ex - 22, ey - 22, ex + 22, ey + 22], fill=(214, 168, 112))
    # box body + lid flaps
    d.polygon([(L - 20, T), (L + 40, T - 60), (L + bw / 2, T)], fill=(196, 146, 90))
    d.polygon([(L + bw + 20, T), (L + bw - 40, T - 60), (L + bw / 2, T)], fill=(184, 134, 80))
    d.rounded_rectangle([L, T, L + bw, T + bh], 18, fill=(214, 168, 112))
    d.rectangle([L, T, L + bw, T + 22], fill=(196, 146, 90))
    d.rectangle([cx - 28, T, cx + 28, T + bh], fill=(232, 200, 150))  # tape
    # label sticker
    d.rounded_rectangle([L + 24, T + bh - 70, L + 120, T + bh - 24], 6, fill=WHITE)
    for q in range(5): d.line([(L + 34 + q * 16, T + bh - 62), (L + 34 + q * 16, T + bh - 32)], fill=INK, width=4 if q % 2 else 7)
    # face
    blink = (gt % 3.7) < 0.12
    for ex_ in (cx - 70, cx + 70):
        if blink: d.line([(ex_ - 22, T + 105), (ex_ + 22, T + 105)], fill=INK, width=8)
        else:
            d.ellipse([ex_ - 26, T + 78, ex_ + 26, T + 132], fill=WHITE)
            d.ellipse([ex_ - 13 - 6, T + 92, ex_ + 13 - 6, T + 120], fill=INK)
            d.ellipse([ex_ - 13, T + 95, ex_ - 5, T + 103], fill=WHITE)
    for ex_ in (cx - 100, cx + 100): d.ellipse([ex_ - 22, T + 145, ex_ + 22, T + 165], fill=(232, 130, 110, 140))
    m = mouth_open(gt)
    mh = 6 + 46 * m
    d.rounded_rectangle([cx - 34, T + 160, cx + 34, T + 160 + mh], radius=int(min(30, mh / 2)), fill=(90, 30, 30))
    if mh > 18: d.ellipse([cx - 18, T + 160 + mh - 16, cx + 18, T + 160 + mh - 2], fill=(220, 90, 90))
    c.alpha_composite(lay)

# ---------- scene contents ----------
CX, CY0 = 70, 820  # card left/top
def bottles(d, x, y, colors, n_visible):
    k = 0
    for row in range(3):
        for col in range(6):
            if k >= n_visible: return
            bx, by = x + col * 120, y + row * 150
            colr = colors[k % len(colors)]
            d.rounded_rectangle([bx, by + 30, bx + 70, by + 130], 18, fill=colr)
            d.rectangle([bx + 24, by + 5, bx + 46, by + 32], fill=colr)
            d.rectangle([bx + 20, by, bx + 50, by + 10], fill=INK)
            d.rectangle([bx, by + 62, bx + 70, by + 92], fill=WHITE)
            k += 1

def s0(c, t, i=0):
    cs = CS[i]; p = eo(t / 0.4)
    paste(c, card(940, 620), W / 2, CY0 + 310 + 60 * (1 - p), al=p)
    if p > 0.5:
        d = ImageDraw.Draw(c); y0 = CY0 + 40 + 60 * (1 - p)
        for r in range(3): d.rectangle([110, y0 + r * 150 + 132, 970, y0 + r * 150 + 142], fill=(200, 190, 178))
        gone = int(clamp((t - cs[0]) / (cs[2] - cs[0])) * 18)
        bottles(d, 150, y0, [(226, 58, 46), (60, 150, 80), (240, 150, 40)], 18 - gone)
        d.text((110, y0 + 470), "GASEOSAS · stock", font=MONO(28), fill=GREY)
        n = 18 - gone; f = ANTON(70)
        d.text((830, y0 + 455), f"{n}", font=f, fill=RED if n < 6 else INK)
    stamp(c, "VENTA PERDIDA", 330, 1580, cs[2] + 0.2, t)

def s1(c, t, i=1):
    cs = CS[i]; p = eo(t / 0.4)
    paste(c, card(940, 620), W / 2, CY0 + 310 + 60 * (1 - p), al=p)
    if p < 0.5: return
    d = ImageDraw.Draw(c); base = CY0 + 540; sc = 11
    days = ["L", "M", "M", "J", "V", "S"]; vals = [18, 21, 19, 20, 22, 32]
    for k in range(6):
        t0 = cs[0] + 0.1 + k * 0.18 if k < 5 else cs[1] + 0.9
        g = bo((t - t0) / 0.4) if t > t0 else 0
        x = 140 + k * 140; h = vals[k] * sc * g
        col = RED if k == 5 else (60, 58, 54)
        if h > 0: d.rounded_rectangle([x, base - h, x + 90, base], 12, fill=col)
        d.text((x + 34, base + 14), days[k], font=MONO(30, "Bold"), fill=GREY)
        if g > 0.8: d.text((x + 45 - ANTON(44).getlength(str(vals[k])) / 2, base - h - 60), str(vals[k]), font=ANTON(44), fill=col)
    ta = cs[0] + 0.3
    if t > ta:
        q = eo((t - ta) / 0.6); y = base - 20 * sc
        for xx in range(110, int(110 + 860 * q), 30): d.line([(xx, y), (xx + 16, y)], fill=(40, 110, 220), width=5)
        d.text((112, CY0 + 50), "- - - promedio 20/día", font=MONO(28, "Bold"), fill=(40, 110, 220))
    stamp(c, "+60%", 330, 1580, cs[1] + 1.1, t, rot=6, size=90)

def s2(c, t, i=2):
    cs = CS[i]; p = eo(t / 0.4)
    paste(c, card(940, 620), W / 2, CY0 + 310 + 60 * (1 - p), al=p)
    if p < 0.5: return
    d = ImageDraw.Draw(c)
    X0, X1, Y0, Y1 = 160, 940, CY0 + 70, CY0 + 520  # Y0 top (80u), Y1 bottom (0)
    ys = lambda v: Y1 - (Y1 - Y0) * v / 80; xs = lambda day: X0 + (X1 - X0) * day / 3.2
    d.line([(X0, Y0 - 10), (X0, Y1), (X1 + 20, Y1)], fill=(60, 58, 54), width=4)
    for k in range(4): d.text((xs(k) - 30, Y1 + 12), f"día {k}", font=MONO(24), fill=GREY)
    # curve: 60 -> 0 at day 2.3 (sábado), then 0
    def stock(dd): return max(0, 60 - 60 * dd / 2.3)
    prog = clamp((t - cs[1]) / (cs[2] + 0.4 - cs[1])) * 3.0 if t > cs[1] else 0
    if t > cs[0] + 0.3:
        d.ellipse([xs(0) - 14, ys(60) - 14, xs(0) + 14, ys(60) + 14], fill=INK)
        paste(c, txt("60 · PEDIDO", MONO(30, "Bold"), INK), xs(0) + 30, ys(60) - 40, al=eo((t - cs[0] - 0.3) / 0.3), anchor="l")
    if prog > 0:
        pts = [(xs(q), ys(stock(q))) for q in np.linspace(0, prog, 60)]
        d.line(pts, fill=INK, width=8)
        if prog > 2.3:
            d.rectangle([xs(2.3), ys(16), xs(min(prog, 3.0)), Y1 - 3], fill=(226, 58, 46, 255))
            paste(c, txt("SIN STOCK", ANTON(34), WHITE), (xs(2.3) + xs(min(prog, 3))) / 2, ys(8), al=clamp((prog - 2.5) * 3))
    # truck arriving at day 3
    tt = cs[1] + 0.2
    if t > tt:
        q = eo((t - tt) / (cs[2] + 0.4 - tt)); tx = X1 + 120 - (X1 + 120 - xs(3)) * q; ty = Y0 + 20
        d.rounded_rectangle([tx - 70, ty, tx + 10, ty + 54], 6, fill=(40, 110, 220)); d.rounded_rectangle([tx + 10, ty + 16, tx + 50, ty + 54], 6, fill=(30, 80, 170))
        for wx in (tx - 45, tx + 30): d.ellipse([wx - 13, ty + 44, wx + 13, ty + 70], fill=INK)
        d.text((tx - 80, ty + 78), "3 días", font=MONO(26, "Bold"), fill=(40, 110, 220))
    stamp(c, "QUIEBRE", 330, 1580, cs[2] + 0.3, t, size=90)

def tile(c, s, cx, cy, t0, t, sub, hot=False, w=170):
    if t < t0: return
    k = ("tile", s, hot, w)
    if k not in _c:
        im = card(w, 170, 24, RED if hot else WHITE).copy(); d = ImageDraw.Draw(im); f = ANTON(96)
        d.text((30 + w / 2 - f.getlength(s) / 2, 30 + 18), s, font=f, fill=WHITE if hot else INK)
        _c[k] = im
    q = (t - t0) / 0.35
    paste(c, _c[k], cx, cy, sc=bo(q), al=clamp(q * 3))
    paste(c, txt(sub, MONO(24, "Bold"), GREY), cx, cy + 135, al=clamp(q * 2))

def s3(c, t, i=3):
    cs = CS[i]; d = ImageDraw.Draw(c); y = 1020
    ops = [("×", 300), ("+", 560), ("=", 800)]
    seq = [("20", 175, cs[1] + 0.05, "venta/día"), ("3", 425, cs[1] + 0.45, "días"), ("15", 680, cs[1] + 1.0, "colchón")]
    for s, x, t0, sub in seq: tile(c, s, x, y, t0, t, sub, w=150)
    for (o, x), t0 in zip(ops, [cs[1] + 0.3, cs[1] + 0.8, cs[2] - 0.1]):
        if t > t0: paste(c, txt(o, ANTON(80), GREY), x, y, sc=bo((t - t0) / 0.3))
    tile(c, "75", 935, y, cs[2] + 0.9, t, "pide aquí", hot=True, w=170)
    if t < cs[1]:
        p = eo((t - 0.2) / 0.4)
        paste(c, card(940, 300), W / 2, 1020, al=p)
        if p > 0.4:
            paste(c, txt("STOCK DE SEGURIDAD", ANTON(76), INK), W / 2, 980, al=p)
            paste(c, txt("= colchón para los días malos", MONO(30, "Bold"), RED), W / 2, 1070, al=p)
    stamp(c, "PUNTO DE PEDIDO", 360, 1580, cs[2] + 1.4, t, rot=-6, size=70)

def s4(c, t, i=4):
    cs = CS[i]; p = eo(t / 0.4)
    paste(c, card(940, 520), W / 2, CY0 + 270 + 60 * (1 - p), al=p)
    if p > 0.4:
        y = CY0 + 150 + 60 * (1 - p); d = ImageDraw.Draw(c)
        d.rounded_rectangle([130, y - 60, 250, y + 60], 26, fill=RED)
        d.text((158, y - 52), "O", font=ANTON(90), fill=WHITE)
        d.text((280, y - 72), "Opera", font=ANTON(110), fill=INK)
        d.text((280 + ANTON(110).getlength("Opera "), y - 64), "Mejor", font=SERIF(124), fill=RED)
        d.text((130, y + 110), "IA y herramientas para", font=INTER(40, "Medium"), fill=(90, 85, 80))
        d.text((130, y + 165), "que tu negocio opere mejor", font=INTER(40, "Medium"), fill=(90, 85, 80))
        d.text((130, y + 260), "@operamejor", font=MONO(36, "Bold"), fill=INK)
    if t > cs[1]:
        q = bo((t - cs[1]) / 0.4); d = ImageDraw.Draw(c)
        b = Image.new("RGBA", (420, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle([0, 0, 419, 120], 30, fill=INK); bd.polygon([(60, 118), (110, 118), (60, 150)], fill=INK)
        bd.text((40, 30), "¿Qué tema sigue?", font=INTER(40, "SemiBold"), fill=WHITE)
        paste(c, b, 300, 1480, sc=q)
    stamp(c, "SÍGUENOS", 300, 1680, cs[1] + 0.8, t, rot=-5, size=70)
    T = SD[i]
    if t > T - 0.5: c.alpha_composite(Image.new("RGBA", (W, H), (236, 232, 225, int(255 * clamp((t - T + 0.5) / 0.5)))))

SCN = [s0, s1, s2, s3, s4]
STARTS = list(np.cumsum([0] + SD[:-1]))

def frame(i, t):
    c = BG.copy()
    header(c, i, t); SCN[i](c, t)
    mascot(c, t, STARTS[i] + t, wave=(i == 4), point=(i != 4))
    draw_caption(c, i, t)
    paste(c, txt("@operamejor", MONO(24, "Bold"), (170, 160, 150)), 70, 1860, anchor="l")
    if t < 0.12 and i > 0:  # quick flash-wipe in
        pass
    return c

def load_venv():
    global VENV
    p = f"{D}/voice.wav"
    if os.path.exists(p):
        a, sr = sf.read(p); hop = sr // 100
        e = np.array([np.sqrt(np.mean(a[k:k + hop] ** 2)) for k in range(0, len(a), hop)])
        e = e / (e.max() + 1e-9); VENV = np.clip(e * 2.2, 0, 1)

def render(i):
    n = int(round(SD[i] * FPS)); tmp = f"{D}/tmp_{i}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(n): p.stdin.write(frame(i, f / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, f"{D}/scene_{i}.mp4")

if __name__ == "__main__":
    json.dump({"CS": CS, "SD": SD, "LEAD": LEAD}, open(f"{D}/timing.json", "w"))
    load_venv()
    if sys.argv[1] == "preview":
        pts = [(0, CS[0][2] + 0.6), (1, SD[1] - 0.3), (2, SD[2] - 0.3), (3, CS[3][0] + 0.5), (3, SD[3] - 0.2), (4, SD[4] - 1.6)]
        ims = [frame(i, t).convert("RGB").resize((360, 640)) for i, t in pts]
        sh = Image.new("RGB", (360 * len(ims), 640)); [sh.paste(im, (360 * k, 0)) for k, im in enumerate(ims)]; sh.save(f"{D}/sheet.png")
        frame(*pts[4]).convert("RGB").save(f"{D}/full.png")
    else:
        for i in map(int, sys.argv[1].split(",")): render(i)
