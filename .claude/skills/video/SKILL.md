---
name: video
description: Convertir un guion.json en video MP4 vertical con voz, animación, efectos y música.
---
# Video

1. Ejecuta `plantilla/hacer_video.sh videos/<carpeta>` (≈1–2 min; la primera vez descarga la voz, ~120 MB).
2. Abre `videos/<carpeta>/preview.png` (un cuadro por escena) y revisa: textos que se salen o se tapan, números visibles y correctos.
3. Si algo se ve mal, ajusta el guion (frases o títulos más cortos) y vuelve a generar.
4. Comprueba la duración: `ffprobe -v error -show_entries format=duration -of csv=p=0 videos/<carpeta>/video.mp4`. Debe estar entre 25 y 40 s.

El MP4 no va a git. Si hay credenciales de Cloudflare R2, súbelo al bucket `opera-mejor-videos` en la misma ruta `videos/<carpeta>/video.mp4`.
