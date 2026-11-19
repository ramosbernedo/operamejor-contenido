#!/usr/bin/env bash
# Uso: plantilla/hacer_video.sh videos/AAAA-MM-DD-tema
# Lee guion.json de esa carpeta y deja video.mp4 + preview.png en ella.
set -e
P=$(cd "$(dirname "$0")" && pwd); OUT=$(cd "$1" && pwd)
M=${OM_MODELS:-$HOME/om-models}; export OM_MODELS=$M
python3 -c "import kokoro_onnx, soundfile, scipy, PIL" 2>/dev/null || pip install -q kokoro-onnx soundfile scipy pillow numpy
mkdir -p "$M"
for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
  [ -f "$M/$f" ] || curl -sSL -o "$M/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
W=$(mktemp -d); cp "$OUT/guion.json" "$W/script.json"; cd "$W"
python3 "$P/tts.py" > /dev/null
python3 "$P/render.py" preview
python3 "$P/audio.py"
python3 "$P/render.py" all
ls scene_*.mp4 | sort -V | sed "s/.*/file '&'/" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest "$OUT/video.mp4"
cp sheet.png "$OUT/preview.png"
echo "Listo: $OUT/video.mp4"
