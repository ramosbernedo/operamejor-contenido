import json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
import os
M = os.environ.get("OM_MODELS", os.path.expanduser("~/om-models"))
k = Kokoro(f"{M}/kokoro-v1.0.int8.onnx", f"{M}/voices-v1.0.bin")
S = json.load(open("script.json")); dur = []
for i, s in enumerate(S):
    row = []
    for j, c in enumerate(s["chunks"]):
        a, sr = k.create(c.replace("*", ""), voice="em_alex", speed=1.12, lang="es")
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0]-800): nz[-1]+1600]  # trim silence
        sf.write(f"c{i}_{j}.wav", a, sr); row.append(len(a)/sr)
    dur.append(row)
json.dump(dur, open("chunkdur.json", "w")); print(dur)
