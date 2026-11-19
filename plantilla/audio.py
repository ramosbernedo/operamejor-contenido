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
# music: soft lo-fi loop (98 bpm)
bpm = 98; beat = 60/bpm; mus = np.zeros(N)
chords = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 349.2]]
def pluck(f, d=1.2):
    t = np.arange(int(d*SR))/SR; return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t))*env(len(t), .01, .35)
nb = int(total/beat) + 1
for b in range(nb):
    t0 = b*beat; ch = chords[(b//4) % 4]
    add(mus, pluck(ch[b % 4]*(2 if b % 2 else 1), 1.0), t0, .12)
    if b % 4 == 0: [add(mus, pluck(f/2, 2.5), t0, .07) for f in ch[:3]]
    if b % 2 == 0: add(mus, np.sin(2*np.pi*np.cumsum(55+80*np.exp(-np.arange(int(.3*SR))/SR*25))/SR)*env(int(.3*SR), .002, .12), t0, .35)
    else: add(mus, hp(rng.standard_normal(int(.15*SR)), 1500)*env(int(.15*SR), .002, .05), t0, .12)
    add(mus, hp(rng.standard_normal(int(.04*SR)), 6000)*env(int(.04*SR), .001, .01), t0 + beat/2, .12)
t = np.arange(N)/SR
ve = lp(np.abs(voice), 5); ve /= ve.max(); duck = 1 - .5*np.clip(ve*5, 0, 1)
fade = np.clip(np.minimum(t/.5, (total - t)/1.5), 0, 1)
out = voice*1.0 + fx*.7 + mus*.55*duck*fade
out = out[:int(total*SR)]; out = out/np.abs(out).max()*.9
sf.write("mix.wav", out, SR)
