# Opera Mejor — Máquina de contenido (handoff)

## Contexto
- Consultora "Opera Mejor" (supply chain + IA, Perú). Videos verticales TikTok/IG/LinkedIn en español.
- Prueba hecha: "Stock de seguridad" v2 (31 s), estilo inspirado en un video de referencia:
  fondo crema con cuadrícula, títulos Anton con palabra clave en rojo, etiquetas mono "// 01 · ...",
  badge numérico negro, sellos rojos rotados, subtítulos arriba palabra por palabra (énfasis en serif itálica roja),
  mascota original: caja de cartón que habla (boca sincronizada con la voz) y parpadea.
- Voz: Kokoro TTS (kokoro-onnx, voz `em_alex`, lang `es`, speed 1.12), modelo desde
  github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/ (kokoro-v1.0.int8.onnx, voices-v1.0.bin).
- Sonidos y música lo-fi sintetizados con numpy/scipy (audio.py). Fuentes de google/fonts en GitHub:
  Anton, Instrument Serif Italic, Inter, JetBrains Mono.

## Archivos
- script.json — guion por escenas (label, title, n, chunks con *énfasis*)
- tts.py — genera c{escena}_{frase}.wav + chunkdur.json
- render.py — dibuja escenas (PIL, 1080x1920, 30 fps) → scene_i.mp4 (`python3 render.py preview` | `python3 render.py 0,1,2,3,4`)
- audio.py — voz + efectos + música con ducking → voice.wav, mix.wav
- Orden: tts.py → render.py preview (genera timing.json) → audio.py → render.py 0..4 → concat + mux

## Estructura acordada
- 4 skills: Research, Guion (3 formatos rotando: "error común", "fórmula en 30 s", "mito vs realidad"), Video, Publicación.
- 3 agentes: Research (semanal, domingo), Producción (diario; escalar a 3 en paralelo), Revisor (diario, verifica datos/fórmulas/video).
- 1 tarea programada diaria 10 pm: stock de temas (mín. 7 aprobados) + (producir + revisar + avisar).
- Meta: empezar con 1 video diario, escalar a 3.

## Almacenamiento
- GitHub repo `opera-mejor-contenido`: skills/, plantilla/ (este código + fuentes), panel de temas (artifact con base de datos),
  videos/AAAA-MM-DD-tema/ (guion.json, post.md, revision.md). Sin MP4.
- Cloudflare R2 bucket `opera-mejor-videos`: MP4 y audios (misma carpeta que en GitHub).
- Cloudflare Pages (opcional): panel para aprobar temas y ver/descargar videos desde el celular.

## Siguiente paso
1. Crear el repo y subir la plantilla.
2. Convertir la plantilla en la skill de Video (script.json → MP4 con un solo comando).
3. Skill de Guion, temas.json + skill de Research, tareas programadas, subida a R2.
