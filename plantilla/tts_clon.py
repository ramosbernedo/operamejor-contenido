# Voz clonada con F5-TTS (español). Corre en el entorno de Python 3.11 que crea hacer_video.sh.
# Uso: python tts_clon.py <voz>   (voz = nombre en plantilla/voces/, p. ej. mayron)
import json, os, re, sys, unicodedata
import numpy as np, soundfile as sf
from huggingface_hub import hf_hub_download
from f5_tts.api import F5TTS
V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voces", sys.argv[1])
ref_text = open(V + ".txt").read().strip()
tts = F5TTS(model="F5TTS_Base", ckpt_file=hf_hub_download("jpgallegoar/F5-Spanish", "model_1250000.safetensors"),
            vocab_file=hf_hub_download("jpgallegoar/F5-Spanish", "vocab.txt"), device="cpu")
from faster_whisper import WhisperModel
W = WhisperModel("small", device="cpu", compute_type="int8")
NUM = {"uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve","diez","once","doce","veinte","treinta","cuarenta","cincuenta","sesenta","setenta","ochenta","noventa","cien","mil"}
norm = lambda x: re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFKD", x.lower()).encode("ascii", "ignore").decode()).split()
def ok(text, wav):
    # F5 a veces se come la primera palabra en frases cortas: verificamos que esté
    heard = norm(" ".join(seg.text for seg in W.transcribe(wav, language="es")[0])); first = norm(text)[0]
    return first in heard or (first in NUM and any(w.isdigit() for w in heard[:3]))
def gen(text, sr_out):
    tries = [(text, 1.05), (text, 1.0), ("Y " + text[0].lower() + text[1:], 1.0), (text, .95)]
    for k, (t, sp) in enumerate(tries):
        a, sr, _ = tts.infer(V + ".wav", ref_text, t, nfe_step=int(os.environ.get("OM_NFE", "24")), speed=sp, seed=k + 7)
        a = np.asarray(a, dtype=np.float32); nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0]-800): nz[-1]+1600]
        sf.write(sr_out, a, sr)
        if ok(text, sr_out): return len(a)/sr
        print("reintento:", text, file=sys.stderr)
    return len(a)/sr
S = json.load(open("script.json")); dur = []
for i, s in enumerate(S):
    row = []
    for j, c in enumerate(s["chunks"]): row.append(gen(c.replace("*", ""), f"c{i}_{j}.wav"))
    dur.append(row)
json.dump(dur, open("chunkdur.json", "w")); print(dur)
