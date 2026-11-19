# Voz clonada con F5-TTS (español). Corre en el entorno de Python 3.11 que crea hacer_video.sh.
# Uso: python tts_clon.py <voz>   (voz = nombre en plantilla/voces/, p. ej. mayron)
import json, os, sys
import numpy as np, soundfile as sf
from huggingface_hub import hf_hub_download
from f5_tts.api import F5TTS
V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voces", sys.argv[1])
ref_text = open(V + ".txt").read().strip()
tts = F5TTS(model="F5TTS_Base", ckpt_file=hf_hub_download("jpgallegoar/F5-Spanish", "model_1250000.safetensors"),
            vocab_file=hf_hub_download("jpgallegoar/F5-Spanish", "vocab.txt"), device="cpu")
S = json.load(open("script.json")); dur = []
for i, s in enumerate(S):
    row = []
    for j, c in enumerate(s["chunks"]):
        a, sr, _ = tts.infer(V + ".wav", ref_text, c.replace("*", ""), nfe_step=int(os.environ.get("OM_NFE", "24")), speed=float(os.environ.get("OM_SPEED", "1.05")))
        a = np.asarray(a, dtype=np.float32)
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0]-800): nz[-1]+1600]
        sf.write(f"c{i}_{j}.wav", a, sr); row.append(len(a)/sr)
    dur.append(row)
json.dump(dur, open("chunkdur.json", "w")); print(dur)
