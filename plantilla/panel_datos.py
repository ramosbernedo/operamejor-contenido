# Uso: python3 plantilla/panel_datos.py videos/<carpeta> [video_id] > datos.json
# Junta post.md + guion.json (+ duración del video) en los campos que muestra el panel.
import json, re, subprocess, sys, os
d = sys.argv[1].rstrip("/"); out = {}
post = open(f"{d}/post.md").read()
sec = dict((m.group(1).strip().lower(), m.group(2).strip()) for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", post, re.S | re.M))
for k, campo in [("tiktok", "post_tiktok"), ("instagram", "post_instagram"), ("linkedin", "post_linkedin"), ("portada", "portada"), ("hora", "hora")]:
    v = next((txt for name, txt in sec.items() if name.startswith(k)), None)
    if v: out[campo] = v
g = json.load(open(f"{d}/guion.json"))
out["guion_voz"] = "\n".join(c.replace("*", "") for s in g for c in s["chunks"])
mp4 = f"{d}/video.mp4"
if os.path.exists(mp4):
    out["duracion_seg"] = round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4])), 1)
if len(sys.argv) > 2: out["video_id"] = sys.argv[2]
out["carpeta"] = d
print(json.dumps(out, ensure_ascii=False))
