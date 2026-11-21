#!/usr/bin/env bash
# Uso: plantilla/hacer_video.sh videos/AAAA-MM-DD-tema
# Lee guion.json de esa carpeta y deja video.mp4 + preview.png en ella.
# Voz: OM_VOZ=mayron (por defecto, voz clonada) u OM_VOZ=kokoro (voz sintética rápida).
# Música: OM_MUSICA=lofi|pop|house|tension (si no, se elige sola según el video).
set -e
P=$(cd "$(dirname "$0")" && pwd); OUT=$(cd "$1" && pwd)
VOZ=${OM_VOZ:-mayron}
python3 -c "import kokoro_onnx, soundfile, scipy, PIL" 2>/dev/null || pip install -q kokoro-onnx soundfile scipy pillow numpy
W=$(mktemp -d); cp "$OUT/guion.json" "$W/script.json"; cd "$W"
if [ "$VOZ" = kokoro ]; then
  M=${OM_MODELS:-$HOME/om-models}; export OM_MODELS=$M; mkdir -p "$M"
  for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
    [ -f "$M/$f" ] || curl -sSL -o "$M/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
  done
  python3 "$P/tts.py" > /dev/null
else
  VENV=${OM_VENV:-$HOME/om-venv}
  if [ ! -x "$VENV/bin/python" ] || ! "$VENV/bin/python" -c "import f5_tts" 2>/dev/null; then
    command -v uv >/dev/null || pip install -q uv
    uv venv -q -p 3.11 "$VENV" && VIRTUAL_ENV=$VENV uv pip install -q f5-tts faster-whisper
  fi
  HF_HUB_DISABLE_XET=1 "$VENV/bin/python" "$P/tts_clon.py" "$VOZ" > /dev/null 2>&1
fi
python3 "$P/render.py" preview
OM_SEED=$(basename "$OUT") python3 "$P/audio.py"
python3 "$P/render.py" all
ls scene_*.mp4 | sort -V | sed "s/.*/file '&'/" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest "$OUT/video.mp4"
cp sheet.png "$OUT/preview.png"; cp portada.png "$OUT/portada.png"
echo "Listo: $OUT/video.mp4"
