---
name: produccion
description: Produce un video completo (guion, video y post) para un tema aprobado del panel.
---
Eres el productor de Opera Mejor. Recibes un tema `aprobado` del panel (si no te dan uno, toma el aprobado con `creado` más antiguo).

1. Crea `videos/<fecha de publicación>-<id>/`.
2. Skill `guion` → `guion.json`.
3. Skill `video` → `video.mp4` y `preview.png`.
4. Skill `publicacion` → `post.md`. En el panel pon el tema en `producido` con su `carpeta` y `cta`.
5. **Guarda el video en la central** (el panel): sube `video.mp4` con la herramienta Artifact (`url` del panel, `file_path` del video, `asset: true`) y anota el `id` que devuelve. Luego `python3 plantilla/panel_datos.py videos/<carpeta> <id> > /tmp/datos.json` y actualiza el tema en el panel con `ArtifactData` `update` (`file_path` = ese JSON, con `if_version`).
6. Responde solo: carpeta, duración y cualquier problema.
