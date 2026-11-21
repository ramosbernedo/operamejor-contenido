import json, math, os, sys, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

W, H, FPS = 1080, 1920, 30
D = os.getcwd(); F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
S = json.load(open(f"{D}/script.json")); CD = json.load(open(f"{D}/chunkdur.json"))
LEAD, GAP, TAIL = 0.15, 0.15, 0.35  # ritmo rápido: escenas de 2–3 s
# chunk start times (scene-local) and scene durations
CS, SD = [], []
for i, row in enumerate(CD):
    t = 0.05 if i == 0 else LEAD; st = []  # la voz arranca de inmediato en la 1ª escena
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

def title_parts(line):
    # acepta "EL *SÁBADO*" (lo de *asteriscos* va en rojo) o el formato viejo ["EL ",0,"SÁBADO",1]
    if isinstance(line, str):
        a, _, b = line.partition("*"); return [(a, INK), (b.replace("*", ""), RED)]
    return [(line[0], INK)] + ([(line[2], RED)] if len(line) > 2 else [])

def header(c, i, t):
    s = S[i]
    al = eo((t - 0.05) / 0.3)
    paste(c, txt(s["label"], MONO(30), (140, 120, 110)), 70, 380, al=al, anchor="l")
    y = 470
    for li, line in enumerate(s["title"]):
        t0 = 0.12 + li * 0.15; p = (t - t0) / 0.35
        if p <= 0: continue
        x = 70; yo = 40 * (1 - eo(p))
        for ptxt, col in title_parts(line):
            if not ptxt: continue
            spr = txt(ptxt, ANTON(132), col)
            paste(c, spr, x - 12, y + yo + 12, al=clamp(p * 2), anchor="l"); x += spr.width - 24
        if li == 0 and s.get("n"): badge(c, s["n"], 980, y + 10, 0.3, t)
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

# ---------- tipos de escena (se eligen en el guion con "tipo") ----------
CX, CY0 = 70, 820
GREEN = (46, 150, 80); BLUE = (40, 110, 220)
def dat(i): return S[i].get("datos", {})
def last(i): return len(CS[i]) - 1
def cend(i, j): return CS[i][j] + CD[i][j]
def base_card(c, t, h=620):
    p = eo(t / 0.4); paste(c, card(940, h), W / 2, CY0 + h / 2 + 60 * (1 - p), al=p); return p
def wrap(s, f, maxw):
    out = [""]
    for w in s.split():
        tst = (out[-1] + " " + w).strip()
        if f.getlength(tst) > maxw and out[-1]: out.append(w)
        else: out[-1] = tst
    return out

def icons(d, x, y, n, kind):
    cols = [(226, 58, 46), (60, 150, 80), (240, 150, 40)]
    for k in range(n):
        bx, by = x + (k % 6) * 120, y + (k // 6) * 150; col = cols[k % 3]
        if kind == "caja":
            d.rounded_rectangle([bx, by + 40, bx + 90, by + 130], 10, fill=(214, 168, 112))
            d.rectangle([bx + 35, by + 40, bx + 55, by + 130], fill=(232, 200, 150))
        else:
            d.rounded_rectangle([bx, by + 30, bx + 70, by + 130], 18, fill=col)
            d.rectangle([bx + 24, by + 5, bx + 46, by + 32], fill=col)
            d.rectangle([bx + 20, by, bx + 50, by + 10], fill=INK)
            d.rectangle([bx, by + 62, bx + 70, by + 92], fill=WHITE)

# lista: unos productos que se van acabando. datos: inicio, fin, icono (botella|caja), etiqueta
def lista_t(i): return CS[i][0], (CS[i][last(i)] if last(i) else cend(i, 0))
def sc_lista(c, t, i):
    D_ = dat(i); ini, fin = D_.get("inicio", 18), D_.get("fin", 0)
    p = base_card(c, t)
    if p < 0.5: return
    d = ImageDraw.Draw(c); y0 = CY0 + 40 + 60 * (1 - p); t0, t1 = lista_t(i)
    for r in range(3): d.rectangle([110, y0 + r * 150 + 132, 970, y0 + r * 150 + 142], fill=(200, 190, 178))
    n = round(ini + (fin - ini) * clamp((t - t0) / max(.1, t1 - t0)))
    icons(d, 150, y0, round(18 * n / ini) if ini else 0, D_.get("icono", "botella"))
    d.text((110, y0 + 470), D_.get("etiqueta", "stock"), font=MONO(28), fill=GREY)
    d.text((830, y0 + 455), str(n), font=ANTON(70), fill=RED if n <= ini * .3 else INK)
def ev_lista(i):
    t0, t1 = lista_t(i); e = [(t0 + (t1 - t0) * k / 14, "pop", .18, 1200 - k * 30) for k in range(14)]
    if dat(i).get("fin", 0) < dat(i).get("inicio", 18): e += [(t1 + .2, "thud", .9), (t1 + .25, "error", .5)]
    return e

# barras: comparar cantidades. datos: etiquetas, valores, destacar (índice), promedio, nota
def barras_cfg(i):
    D_ = dat(i); v = D_["valores"]; h = D_.get("destacar", v.index(max(v)))
    th = CS[i][last(i)] + .9 if last(i) else CS[i][0] + .3 + len(v) * .18
    return D_, v, h, th
def sc_barras(c, t, i):
    D_, vals, hi, th = barras_cfg(i)
    if base_card(c, t) < 0.5: return
    d = ImageDraw.Draw(c); base = CY0 + 540; n = len(vals); slot = 860 / n; bw = min(90, slot * .65)
    sc = 400 / max(vals + [D_.get("promedio", 0)]); labs = D_.get("etiquetas", [""] * n)
    for k in range(n):
        t0 = th if k == hi else CS[i][0] + .1 + k * .18
        g = bo((t - t0) / .4) if t > t0 else 0
        x = 110 + k * slot + (slot - bw) / 2; h = vals[k] * sc * g; col = RED if k == hi else (60, 58, 54)
        if h > 0: d.rounded_rectangle([x, base - h, x + bw, base], 12, fill=col)
        f = MONO(28, "Bold"); d.text((x + bw / 2 - f.getlength(str(labs[k])) / 2, base + 14), str(labs[k]), font=f, fill=GREY)
        if g > .8: d.text((x + bw / 2 - ANTON(44).getlength(str(vals[k])) / 2, base - h - 60), str(vals[k]), font=ANTON(44), fill=col)
    if "promedio" in D_ and t > CS[i][0] + .3:
        q = eo((t - CS[i][0] - .3) / .6); y = base - D_["promedio"] * sc
        for xx in range(110, int(110 + 860 * q), 30): d.line([(xx, y), (xx + 16, y)], fill=BLUE, width=5)
        d.text((112, CY0 + 50), "- - - " + D_.get("nota", f"promedio {D_['promedio']}"), font=MONO(28, "Bold"), fill=BLUE)
def ev_barras(i):
    D_, v, hi, th = barras_cfg(i)
    return [(CS[i][0] + .1 + k * .18, "pop", .3, 600 + k * 80) for k in range(len(v)) if k != hi] + [(th - .25, "swipe", .8), (th, "thud", .8)]

# curva: el stock baja hasta cero. datos: inicio, dias_hasta_cero, dias, etiqueta, llegada
def curva_cfg(i):
    D_ = dat(i); a = CS[i][1] if last(i) else CS[i][0] + .5; b = CS[i][last(i)] + .4
    return D_, a, max(b, a + 1.5)
def sc_curva(c, t, i):
    D_, ta, tb = curva_cfg(i)
    if base_card(c, t) < 0.5: return
    ini, cero, tot = D_.get("inicio", 60), D_.get("dias_hasta_cero", 2.3), D_.get("dias", 3)
    d = ImageDraw.Draw(c); X0, X1, Y0, Y1 = 160, 940, CY0 + 70, CY0 + 520
    ys = lambda v: Y1 - (Y1 - Y0) * v / (ini * 1.33); xs = lambda dd: X0 + (X1 - X0) * dd / (tot + .2)
    d.line([(X0, Y0 - 10), (X0, Y1), (X1 + 20, Y1)], fill=(60, 58, 54), width=4)
    for k in range(int(tot) + 1): d.text((xs(k) - 30, Y1 + 12), f"día {k}", font=MONO(24), fill=GREY)
    stock = lambda dd: max(0, ini - ini * dd / cero)
    if t > CS[i][0] + .3:
        d.ellipse([xs(0) - 14, ys(ini) - 14, xs(0) + 14, ys(ini) + 14], fill=INK)
        paste(c, txt(D_.get("etiqueta", f"{ini} · PEDIDO"), MONO(30, "Bold"), INK), xs(0) + 30, ys(ini) - 40, al=eo((t - CS[i][0] - .3) / .3), anchor="l")
    prog = clamp((t - ta) / (tb - ta)) * tot
    if prog > 0:
        d.line([(xs(q), ys(stock(q))) for q in np.linspace(0, prog, 60)], fill=INK, width=8)
        if prog > cero:
            d.rectangle([xs(cero), ys(ini * .27), xs(prog), Y1 - 3], fill=RED)
            paste(c, txt("SIN STOCK", ANTON(34), WHITE), (xs(cero) + xs(prog)) / 2, ys(ini * .13), al=clamp((prog - cero - .2) * 3))
    if D_.get("llegada") and t > ta - .2:
        q = eo((t - ta + .2) / (tb - ta + .2)); tx = X1 + 120 - (X1 + 120 - xs(tot)) * q; ty = Y0 + 20
        d.rounded_rectangle([tx - 70, ty, tx + 10, ty + 54], 6, fill=BLUE); d.rounded_rectangle([tx + 10, ty + 16, tx + 50, ty + 54], 6, fill=(30, 80, 170))
        for wx in (tx - 45, tx + 30): d.ellipse([wx - 13, ty + 44, wx + 13, ty + 70], fill=INK)
        d.text((tx - 80, ty + 78), D_["llegada"], font=MONO(26, "Bold"), fill=BLUE)
def ev_curva(i):
    D_, ta, tb = curva_cfg(i); tz = ta + (tb - ta) * D_.get("dias_hasta_cero", 2.3) / D_.get("dias", 3)
    e = [(CS[i][0] + .3, "pop", .35, 900), (tz, "error", .45), (tz + .2, "thud", .9)]
    if D_.get("llegada"): e.append((ta, "truck", .5))
    return e

# formula: una cuenta paso a paso. datos: titulo, subtitulo, terminos [["20","venta/día"],"×",...], resultado ["75","pide aquí"]
def formula_cfg(i):
    D_ = dat(i); r = 1 if last(i) and D_.get("titulo") else 0
    items = D_["terminos"] + ["="]; n = len(items)
    ts = [CS[i][r] + .05 + CD[i][r] * k / n for k in range(n)]
    tr = min(cend(i, last(i)) + .3, SD[i] - TAIL - .2) if last(i) > r else ts[-1] + .5
    return D_, r, items, ts, tr
def sc_formula(c, t, i):
    D_, r, items, ts, tr = formula_cfg(i); y = 1020
    allit = items + [D_["resultado"]]
    ws = [max(150, ANTON(96).getlength(it[0]) + 50) if isinstance(it, list) else 80 for it in allit]
    sc = min(1., 940 / (sum(ws) + 20 * len(ws))); x = W / 2 - (sum(ws) + 20 * len(ws)) * sc / 2
    for k, (it, w) in enumerate(zip(allit, ws)):
        cx = x + (w + 20) * sc / 2; t0 = tr if k == len(allit) - 1 else ts[k]
        if isinstance(it, list): tile(c, it[0], cx, y, t0, t, it[1] if len(it) > 1 else "", hot=k == len(allit) - 1, w=int(w), sc_=sc)
        elif t > t0: paste(c, txt(it, ANTON(80), GREY), cx, y, sc=bo((t - t0) / .3) * sc)
        x += (w + 20) * sc
    if D_.get("titulo") and t < CS[i][r]:
        p = eo((t - .2) / .4); paste(c, card(940, 300), W / 2, 1020, al=p)
        if p > .4:
            paste(c, txt(D_["titulo"], ANTON(76), INK), W / 2, 980, al=p)
            if D_.get("subtitulo"): paste(c, txt(D_["subtitulo"], MONO(30, "Bold"), RED), W / 2, 1070, al=p)
def ev_formula(i):
    D_, r, items, ts, tr = formula_cfg(i)
    return [(tt, "pop", .4, 1000) for tt in ts] + [(tr - .5, "chime", .5), (tr, "thud", .8)]

def tile(c, s, cx, cy, t0, t, sub, hot=False, w=170, sc_=1.):
    if t < t0: return
    k = ("tile", s, hot, w)
    if k not in _c:
        im = card(w, 170, 24, RED if hot else WHITE).copy(); d = ImageDraw.Draw(im); f = ANTON(96)
        d.text((30 + w / 2 - f.getlength(s) / 2, 30 + 18), s, font=f, fill=WHITE if hot else INK)
        _c[k] = im
    q = (t - t0) / .35
    paste(c, _c[k], cx, cy, sc=bo(q) * sc_, al=clamp(q * 3))
    if sub: paste(c, txt(sub, MONO(24, "Bold"), GREY), cx, cy + 135, al=clamp(q * 2))

# mito: mito vs realidad. datos: mito, realidad
def mito_cfg(i): return CS[i][0] + .2, CS[i][min(1, last(i))] + .5, CS[i][last(i)] + (.3 if last(i) > 1 else 1.2)
def note(c, head, body, col, cy, al):
    f = INTER(44, "SemiBold"); ls = wrap(body, f, 820); h = 110 + 58 * len(ls)
    im = card(940, h).copy(); d = ImageDraw.Draw(im)
    d.text((80, 60), head, font=MONO(30, "Bold"), fill=col)
    for k, l in enumerate(ls): d.text((80, 110 + 58 * k), l, font=f, fill=INK)
    paste(c, im, W / 2, cy, al=al); return h
def sc_mito(c, t, i):
    D_ = dat(i); ta, tx, tr = mito_cfg(i)
    if t > ta:
        h = note(c, "MITO", D_.get("mito", ""), GREY, 960, eo((t - ta) / .4))
        if t > tx:
            q = eo((t - tx) / .25); d = ImageDraw.Draw(c)
            d.line([(140, 960 - h / 3), (140 + 800 * q, 960 - h / 3 + (2 * h / 3) * q)], fill=RED, width=14)
    if t > tr: note(c, "REALIDAD", D_.get("realidad", ""), GREEN, 1300, eo((t - tr) / .4))
def ev_mito(i):
    ta, tx, tr = mito_cfg(i); return [(ta, "pop", .35, 800), (tx, "error", .45), (tx + .05, "thud", .8), (tr, "chime", .45)]

# texto: una idea fuerte. datos: grande, chico
def sc_texto(c, t, i):
    D_ = dat(i); p = base_card(c, t, 520)
    if p < .4: return
    g = D_.get("grande", ""); big = len(g) <= 8  # cifra corta = gigante y roja (gancho)
    d = ImageDraw.Draw(c); f = ANTON(230 if big else 84); y = CY0 + (40 if big else 90) + 60 * (1 - p)
    for l in wrap(g, f, 820): d.text((130, y), l, font=f, fill=RED if big else INK); y += 290 if big else 110
    if D_.get("chico"): d.text((130, y + 30), D_["chico"], font=MONO(30, "Bold"), fill=RED)
def ev_texto(i): return [(CS[i][0] + .3, "pop", .4, 900)]

# cierre: marca Opera Mejor + llamada a comentar
def sc_cierre(c, t, i):
    cs = CS[i]; p = base_card(c, t, 520)
    if p > 0.4:
        y = CY0 + 150 + 60 * (1 - p); d = ImageDraw.Draw(c)
        d.rounded_rectangle([130, y - 60, 250, y + 60], 26, fill=RED)
        d.text((158, y - 52), "O", font=ANTON(90), fill=WHITE)
        d.text((280, y - 72), "Opera", font=ANTON(110), fill=INK)
        d.text((280 + ANTON(110).getlength("Opera "), y - 64), "Mejor", font=SERIF(124), fill=RED)
        d.text((130, y + 110), "IA y herramientas para", font=INTER(40, "Medium"), fill=(90, 85, 80))
        d.text((130, y + 165), "que tu negocio opere mejor", font=INTER(40, "Medium"), fill=(90, 85, 80))
        d.text((130, y + 260), "@operamejor", font=MONO(36, "Bold"), fill=INK)
    tq = cs[last(i)]
    if t > tq:
        q = bo((t - tq) / 0.4)
        b = Image.new("RGBA", (420, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        bd.rounded_rectangle([0, 0, 419, 120], 30, fill=INK); bd.polygon([(60, 118), (110, 118), (60, 150)], fill=INK)
        bd.text((40, 30), dat(i).get("pregunta", "¿Qué tema sigue?"), font=INTER(40, "SemiBold"), fill=WHITE)
        paste(c, b, 300, 1480, sc=q)
def ev_cierre(i): return [(CS[i][last(i)], "pop", .4, 1100), (CS[i][last(i)] + .8, "chime", .45)]

# impacto: primer segundo a pantalla completa, solo la cifra gigante. datos: cifra, sub
def sc_impacto(c, t, i):
    D_ = dat(i); s_ = D_.get("cifra", ""); f = ANTON(340)
    while f.getlength(s_) > 960 and f.size > 120: f = ANTON(f.size - 20)
    p = clamp(t / .28); shake = 10 * math.sin(t * 70) * max(0, 1 - t / .45)
    pulse = 1 + .07 * max(0, 1 - abs(t - CS[i][-1] - .1) / .15) if last(i) else 1
    paste(c, txt(s_, f, RED), W / 2 + shake, 900, sc=(1 + 1.6 * (1 - eo(p))) * pulse, al=clamp(p * 3))
    if t > .3:
        q = eo((t - .3) / .3); d = ImageDraw.Draw(c)
        d.rectangle([W / 2 - 300 * q, 1080, W / 2 + 300 * q, 1092], fill=INK)
        paste(c, txt(D_.get("sub", ""), INTER(54, "Bold"), INK), W / 2, 1170 + 20 * (1 - q), al=q)
def ev_impacto(i): return [(0, "whoosh", .5), (.03, "thud", 1.0)] + ([(CS[i][-1] + .1, "thud", .6)] if last(i) else [])

# pasos: la solución en pasos concretos, uno por frase. datos: pasos (máx. 4)
def sc_pasos(c, t, i):
    ps = dat(i).get("pasos", []); n = len(ps); h = 130 + 120 * n
    if base_card(c, t, h) < .4: return
    d = ImageDraw.Draw(c); f = INTER(46, "SemiBold")
    for k, s_ in enumerate(ps):
        t0 = CS[i][min(k, last(i))] - .05
        if t < t0: continue
        q = eo((t - t0) / .3); y = CY0 + 75 + 120 * k + 20 * (1 - q)
        im = Image.new("RGBA", (86, 86), (0, 0, 0, 0)); ImageDraw.Draw(im).ellipse([0, 0, 85, 85], fill=RED)
        fn = ANTON(54); ImageDraw.Draw(im).text((43 - fn.getlength(str(k + 1)) / 2, 6), str(k + 1), font=fn, fill=WHITE)
        paste(c, im, 160, y + 40, sc=bo((t - t0) / .3), al=q)
        lines = wrap(s_, f, 700)
        for li, l in enumerate(lines[:2]): d.text((230, y + 8 + li * 54 - (27 if len(lines) > 1 else 0)), l, font=f, fill=INK)
def ev_pasos(i): return [(CS[i][min(k, last(i))], "pop", .45, 800 + 120 * k) for k in range(len(dat(i).get("pasos", [])))]

TIPOS = {"pasos": (sc_pasos, ev_pasos), "impacto": (sc_impacto, ev_impacto), "lista": (sc_lista, ev_lista), "barras": (sc_barras, ev_barras), "curva": (sc_curva, ev_curva),
         "formula": (sc_formula, ev_formula), "mito": (sc_mito, ev_mito), "texto": (sc_texto, ev_texto), "cierre": (sc_cierre, ev_cierre)}

def sello_t(i):
    s = S[i].get("sello")
    if not s: return None
    k = min(s.get("frase", last(i)), last(i)); return min(CS[i][k] + min(1.0, CD[i][k] * .6), SD[i] - .6)
def events():
    ev = []
    for i, st in enumerate(STARTS):
        if i: ev.append((st - .2, "whoosh", .45))
        ev += [(st + .15, "pop", .35, 700), (st + .3, "pop", .35, 1000), (st + .35, "tick", .6)]
        ev += [(st + e[0],) + tuple(e[1:]) for e in TIPOS[S[i].get("tipo", "texto")][1](i)]
        ts = sello_t(i)
        if ts is not None: ev.append((st + ts, "thud", .9))
    return ev

STARTS = list(np.cumsum([0] + SD[:-1]))

def frame(i, t):
    c = BG.copy(); tipo = S[i].get("tipo", "texto")
    if tipo != "impacto": header(c, i, t)
    TIPOS[tipo][0](c, t, i)
    s = S[i].get("sello"); ts = sello_t(i)
    if s: stamp(c, s["texto"], s.get("x", 330), 1580, ts, t, rot=s.get("giro", -8), size=s.get("tam", 80))
    if tipo != "impacto": mascot(c, t, STARTS[i] + t, wave=(tipo == "cierre"), point=(tipo != "cierre"))
    draw_caption(c, i, t)
    paste(c, txt("@operamejor", MONO(24, "Bold"), (170, 160, 150)), 70, 1860, anchor="l")
    if i == len(S) - 1 and t > SD[i] - .5:
        c.alpha_composite(Image.new("RGBA", (W, H), CREAM + (int(255 * clamp((t - SD[i] + .5) / .5)),)))
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
    json.dump({"CS": CS, "SD": SD, "LEAD": LEAD, "EV": events()}, open(f"{D}/timing.json", "w"))
    load_venv()
    if sys.argv[1] == "preview":  # una imagen por escena -> sheet.png
        ims = [frame(i, SD[i] - (1.0 if i == len(S) - 1 else .3)).convert("RGB").resize((360, 640)) for i in range(len(S))]
        sh = Image.new("RGB", (360 * len(ims), 640)); [sh.paste(im, (360 * k, 0)) for k, im in enumerate(ims)]; sh.save(f"{D}/sheet.png")
        frame(0, min(.8, SD[0] - .1)).convert("RGB").save(f"{D}/portada.png")  # cuadro del gancho para la portada
    else:
        for i in (range(len(S)) if sys.argv[1] == "all" else map(int, sys.argv[1].split(","))): render(i)
