#!/usr/bin/env bash
# Uso: plantilla/hacer_video.sh videos/AAAA-MM-DD-tema
# Toma guion.json de esa carpeta y deja video.mp4 en ella.
set -e
P=$(cd "$(dirname "$0")" && pwd); OUT=$(cd "$1" && pwd)
M=${OM_MODELS:-$HOME/om-models}; export OM_MODELS=$M
pip install -q kokoro-onnx soundfile scipy pillow numpy
mkdir -p "$M"
for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
  [ -f "$M/$f" ] || curl -sSL -o "$M/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
W=$(mktemp -d); cp "$OUT/guion.json" "$W/script.json"; cd "$W"
python3 "$P/tts.py" > /dev/null
python3 "$P/render.py" preview
python3 "$P/audio.py"
python3 "$P/render.py" 0,1,2,3,4
for i in 0 1 2 3 4; do echo "file 'scene_$i.mp4'"; done > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest "$OUT/video.mp4"
cp sheet.png "$OUT/preview.png"
echo "Listo: $OUT/video.mp4"
