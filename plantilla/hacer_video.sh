#!/usr/bin/env bash
# Uso: plantilla/hacer_video.sh videos/AAAA-MM-DD-tema
# Lee guion.json de esa carpeta y deja video.mp4 + preview.png en ella.
# Voz: OM_VOZ=rapida (por defecto: tu timbre, 1–2 min), OM_VOZ=clonada (F5, más natural pero 15–20 min) u OM_VOZ=kokoro (sintética, para borradores).
# Voz de referencia: OM_REF=mayron (archivo en plantilla/voces/).
# Música: OM_MUSICA=lofi|pop|house|tension (si no, se elige sola según el video).
set -e
P=$(cd "$(dirname "$0")" && pwd); OUT=$(cd "$1" && pwd)
VOZ=${OM_VOZ:-rapida}; REF=${OM_REF:-mayron}
python3 -c "import kokoro_onnx, soundfile, scipy, PIL" 2>/dev/null || pip install -q kokoro-onnx soundfile scipy pillow numpy
W=$(mktemp -d); cp "$OUT/guion.json" "$W/script.json"; cd "$W"
M=${OM_MODELS:-$HOME/om-models}; export OM_MODELS=$M; mkdir -p "$M"
for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
  [ -f "$M/$f" ] || curl -sSL -o "$M/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
command -v uv >/dev/null || pip install -q uv
if [ "$VOZ" = kokoro ]; then
  python3 "$P/tts.py" > /dev/null
elif [ "$VOZ" = rapida ]; then
  OV=${OM_OV_VENV:-$HOME/om-ov-venv}
  if ! "$OV/bin/python" -c "import openvoice, kokoro_onnx" 2>/dev/null; then
    uv venv -q -p 3.11 "$OV"
    VIRTUAL_ENV=$OV uv pip install -q --no-deps "git+https://github.com/myshell-ai/OpenVoice.git"
    VIRTUAL_ENV=$OV uv pip install -q torch librosa soundfile numpy huggingface_hub kokoro-onnx inflect unidecode eng-to-ipa pypinyin jieba cn2an
  fi
  HF_HUB_DISABLE_XET=1 "$OV/bin/python" "$P/tts_rapida.py" "$REF" > /dev/null 2>&1
else
  VENV=${OM_VENV:-$HOME/om-venv}
  if [ ! -x "$VENV/bin/python" ] || ! "$VENV/bin/python" -c "import f5_tts" 2>/dev/null; then
    uv venv -q -p 3.11 "$VENV" && VIRTUAL_ENV=$VENV uv pip install -q f5-tts faster-whisper
  fi
  HF_HUB_DISABLE_XET=1 "$VENV/bin/python" "$P/tts_clon.py" "$REF" > /dev/null 2>&1
fi
python3 "$P/render.py" preview
OM_SEED=$(basename "$OUT") python3 "$P/audio.py"
python3 "$P/render.py" all
ls scene_*.mp4 | sort -V | sed "s/.*/file '&'/" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest "$OUT/video.mp4"
cp sheet.png "$OUT/preview.png"; cp portada.png "$OUT/portada.png"
echo "Listo: $OUT/video.mp4"
