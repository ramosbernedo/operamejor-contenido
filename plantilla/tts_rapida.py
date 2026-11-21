# Voz rápida con el timbre del usuario: Kokoro (voz base) + OpenVoice (tono de la voz de referencia).
# Corre en el entorno que crea hacer_video.sh. Uso: python tts_rapida.py <voz>   (voz = nombre en plantilla/voces/)
import json, os, sys
import numpy as np, soundfile as sf
from huggingface_hub import hf_hub_download
from kokoro_onnx import Kokoro
from openvoice.api import ToneColorConverter, OpenVoiceBaseClass
V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voces", sys.argv[1])
M = os.environ.get("OM_MODELS", os.path.expanduser("~/om-models"))
BASE = os.environ.get("OM_BASE", "em_alex"); SPEED = float(os.environ.get("OM_SPEED", "1.05"))
k = Kokoro(f"{M}/kokoro-v1.0.int8.onnx", f"{M}/voices-v1.0.bin")
cfg = hf_hub_download("myshell-ai/OpenVoiceV2", "converter/config.json")
tc = ToneColorConverter.__new__(ToneColorConverter); OpenVoiceBaseClass.__init__(tc, cfg, device="cpu")  # evita un bug del constructor
tc.watermark_model = None; tc.version = getattr(tc.hps, "_version_", "v1")
tc.load_ckpt(hf_hub_download("myshell-ai/OpenVoiceV2", "converter/checkpoint.pth"))
tgt = tc.extract_se([V + ".wav"])
S = json.load(open("script.json")); dur = []
for i, s in enumerate(S):
    row = []
    for j, c in enumerate(s["chunks"]):
        a, sr = k.create(c.replace("*", ""), voice=BASE, speed=SPEED, lang="es")
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0]-800): nz[-1]+1600]
        sf.write("base.wav", a, sr)
        tc.convert(audio_src_path="base.wav", src_se=tc.extract_se(["base.wav"]), tgt_se=tgt, output_path=f"c{i}_{j}.wav", tau=0.3)
        b, sr2 = sf.read(f"c{i}_{j}.wav"); row.append(len(b) / sr2)
    dur.append(row)
json.dump(dur, open("chunkdur.json", "w")); print(dur)
