import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR = 44100; T = json.load(open("timing.json")); CS, SD = T["CS"], T["SD"]
starts = np.cumsum([0] + SD[:-1]); total = sum(SD); N = int(total*SR) + SR
voice = np.zeros(N); fx = np.zeros(N); rng = np.random.default_rng(2)
def add(b, x, t, g=1.): i = int(t*SR); x = x[:N-i]; b[i:i+len(x)] += g*x
def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
def env(n, a, r): e = np.exp(-np.arange(n)/SR/r); ai = max(1, int(a*SR)); e[:ai] *= np.linspace(0, 1, ai); return e
def tone(f, d, r=.2, a=.003): t = np.arange(int(d*SR))/SR; return np.sin(2*np.pi*f*t)*env(len(t), a, r)
def whoosh(d=.5):
    n = int(d*SR); x = rng.standard_normal(n); o = np.zeros(n)
    for j in range(0, n, 1024): f = 400+4000*np.sin(np.pi*j/n); o[j:j+1024] = bp(x[j:j+1024], f*.6, f*1.4)
    return o*np.sin(np.linspace(0, np.pi, n))**2*1.3
def pop(f=900): t = np.arange(int(.1*SR))/SR; return np.sin(2*np.pi*(f*np.exp(-t*30)+180)*t)*env(len(t), .002, .03)
def thud(): t = np.arange(int(.5*SR))/SR; return np.sin(2*np.pi*(90*np.exp(-t*8)+45)*t)*env(len(t), .002, .12) + .5*lp(rng.standard_normal(len(t)), 900)*env(len(t), .001, .03)
def tick(): return hp(rng.standard_normal(int(.03*SR)), 3000)*env(int(.03*SR), .0005, .006)*.6
def error(): return sum(np.sign(np.sin(2*np.pi*f*np.arange(int(.35*SR))/SR))*.15*env(int(.35*SR), .005, .2) for f in (180, 190))
def truck(d=1.6): x = lp(rng.standard_normal(int(d*SR)), 160)*(1+.5*np.sin(2*np.pi*14*np.arange(int(d*SR))/SR)); return x*np.sin(np.linspace(0, np.pi, len(x)))*2.5
def chime(): return tone(1318, 1.2, .4)*.5 + tone(1760, 1.2, .5)*.4 + tone(2637, 1.2, .3)*.2
def swipe_up(): t = np.arange(int(.25*SR))/SR; return np.sin(2*np.pi*np.cumsum(300+2400*t/.25)/SR)*env(len(t), .01, .1)*.5
# voice
for i, row in enumerate(CS):
    for j, st in enumerate(row):
        a, sr = sf.read(f"c{i}_{j}.wav"); a = resample_poly(a, SR, sr)
        add(voice, a, starts[i] + st)
sf.write("voice.wav", voice[:int(total*SR)], SR)
# sfx (los eventos vienen de render.py -> timing.json)
SFX = {"whoosh": lambda *_: whoosh(), "pop": lambda f=900: pop(f), "thud": lambda *_: thud(), "tick": lambda *_: tick(),
       "error": lambda *_: error(), "truck": lambda *_: truck(), "chime": lambda *_: chime(), "swipe": lambda *_: swipe_up()}
for e in T["EV"]: add(fx, SFX[e[1]](*e[3:]), max(0, e[0]), e[2])
# music: 4 estilos; se elige con OM_MUSICA (lofi|pop|house|tension) o al azar fijo por video (OM_SEED)
import os, zlib
SEED = zlib.crc32(os.environ.get("OM_SEED", "x").encode())
STYLES = {  # bpm, swing, modo, progresión (grados), instrumento de acordes
    "lofi":    dict(bpm=84,  swing=.16, minor=False, prog=[0, 9, 5, 7],  ch="epiano"),
    "pop":     dict(bpm=108, swing=0,   minor=False, prog=[0, 7, 9, 5],  ch="pluck"),
    "house":   dict(bpm=118, swing=0,   minor=True,  prog=[0, 8, 3, 10], ch="pad"),
    "tension": dict(bpm=96,  swing=.05, minor=True,  prog=[0, 5, 8, 7],  ch="pad"),
}
sty = os.environ.get("OM_MUSICA") or list(STYLES)[SEED % 4]; S_ = STYLES[sty]
key = 57 + (SEED // 4) % 7  # La..Mi
mrng = np.random.default_rng(SEED)
bpm = S_["bpm"]; beat = 60/bpm; mus = np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def at(b): return b*beat + (S_["swing"]*beat/2 if (b*2) % 2 == 1 else 0)  # swing a los "y"
def saw(f, n): t = np.arange(n)/SR; return sum(np.sin(2*np.pi*f*k*t)/k for k in range(1, 7))
def chord_notes(root):
    if S_["minor"]: third = root + (3 if (root - key) % 12 in (0, 5, 7) else 4)
    else: third = root + (4 if (root - key) % 12 in (0, 5, 7) else 3)
    return [root, third, root+7, root + (10 if third - root == 3 else 11)]
def epiano(f, d):
    n = int(d*SR); t = np.arange(n)/SR
    x = np.sin(2*np.pi*f*t + 1.2*np.sin(2*np.pi*f*t)*np.exp(-t*3)) * env(n, .005, .9)
    return x*(1 + .25*np.sin(2*np.pi*4.5*t))
def pluck2(f, d=.4): n = int(d*SR); return lp(saw(f, n), 2500)*env(n, .003, .12)
def pad(f, d):
    n = int(d*SR); x = lp(saw(f*1.004, n) + saw(f*.996, n), 1400)
    a = np.minimum(1, np.arange(n)/SR/.4); r = np.minimum(1, (n - np.arange(n))/SR/.4); return x*a*r*.5
def bass(f, d): n = int(d*SR); t = np.arange(n)/SR; return lp(np.sin(2*np.pi*f*t) + .3*saw(f, n), 600)*env(n, .005, d*.8)
def kick(g=1.): n = int(.35*SR); t = np.arange(n)/SR; return np.sin(2*np.pi*np.cumsum(50+110*np.exp(-t*30))/SR)*env(n, .001, .14)*g
def snare(): n = int(.22*SR); return (bp(rng.standard_normal(n), 900, 6000)*.8 + tone(190, .22, .05))*env(n, .001, .07)
def clap(): n = int(.25*SR); x = bp(rng.standard_normal(n), 1000, 5000); e = sum(env(n, .001, .012)*(np.arange(n) >= int(k*.011*SR)) for k in range(3)) + env(n, .001, .1)*.6; return x*e*.6
def hat(o=False): n = int((.25 if o else .04)*SR); return hp(rng.standard_normal(n), 7000)*env(n, .001, .09 if o else .012)
def rim(): return hp(tone(1700, .05, .015), 800)
bars = int(total/(4*beat)) + 2
penta = [0, 2, 4, 7, 9] if not S_["minor"] else [0, 3, 5, 7, 10]
for bar in range(bars):
    b0 = bar*4; root = key + S_["prog"][bar % 4] - 12
    notes = chord_notes(root + 12); bl = hz(root - 12)
    if sty == "lofi":
        for f in notes: add(mus, epiano(hz(f), 4*beat), at(b0), .09)
        for bt in (0, 2.5): add(mus, kick(.9), at(b0 + bt), .5)
        for bt in (1, 3): add(mus, snare(), at(b0 + bt), .22)
        for k in range(8): add(mus, hat(), at(b0 + k/2), .05 + .03*(k % 2 == 0))
        add(mus, bass(bl*2, 2*beat), at(b0), .35); add(mus, bass(bl*2, 1.5*beat), at(b0 + 2.5), .3)
        for k in mrng.choice(8, 3, replace=False): add(mus, epiano(hz(key + 12 + penta[mrng.integers(5)]), beat), at(b0 + k/2), .05)
    elif sty == "pop":
        for bt in (0, 1.5, 2, 2.75): add(mus, kick(), at(b0 + bt), .5 if bt in (0, 2) else .3)
        for bt in (1, 3): add(mus, clap(), at(b0 + bt), .35)
        for k in range(8): add(mus, hat(), at(b0 + k/2), .06)
        for bt in (.5, 1.5, 2.5, 3.5): [add(mus, pluck2(hz(f)), at(b0 + bt), .07) for f in notes[:3]]
        for k in range(8): add(mus, bass(bl*2, beat/2), at(b0 + k/2), .3)
        for k in range(16): add(mus, pluck2(hz(notes[[0, 1, 2, 3, 2, 1][k % 6]] + 12), .2), at(b0 + k/4), .025)
    elif sty == "house":
        for bt in range(4): add(mus, kick(), at(b0 + bt), .55)
        for bt in (1, 3): add(mus, clap(), at(b0 + bt), .3)
        for bt in range(4): add(mus, hat(True), at(b0 + bt + .5), .06); add(mus, hat(), at(b0 + bt + .25), .03); add(mus, hat(), at(b0 + bt + .75), .03)
        for f in notes: add(mus, pad(hz(f), 4*beat), at(b0), .07)
        for bt in range(4): add(mus, bass(bl*2*(2 if bt % 2 else 1), beat*.45), at(b0 + bt + .5), .35)
    else:  # tension
        for bt in (0, 2.5): add(mus, kick(), at(b0 + bt), .5)
        for bt in (1, 3): add(mus, rim(), at(b0 + bt), .25)
        for k in range(16): add(mus, hat(), at(b0 + k/4), .025 + .02*(k % 4 == 0))
        for f in notes[:3]: add(mus, pad(hz(f - 12), 4*beat), at(b0), .06)
        for k in range(16): add(mus, pluck2(hz(notes[[0, 2, 1, 3][k % 4]]), .18), at(b0 + k/4), .045)
        add(mus, bass(bl, 4*beat), at(b0), .4)
if sty == "lofi": mus += lp(np.where(rng.random(N) > .9993, rng.standard_normal(N), 0), 4000)*.15 + lp(rng.standard_normal(N), 900)*.004
mus = mus/(np.abs(mus).max() + 1e-9)
print("musica:", sty, "tono:", key)
t = np.arange(N)/SR
ve = lp(np.abs(voice), 5); ve /= ve.max(); duck = 1 - .5*np.clip(ve*5, 0, 1)
fade = np.clip(np.minimum(t/.5, (total - t)/1.5), 0, 1)
out = voice*1.0 + fx*.7 + mus*.32*duck*fade
out = out[:int(total*SR)]; out = out/np.abs(out).max()*.9
sf.write("mix.wav", out, SR)
