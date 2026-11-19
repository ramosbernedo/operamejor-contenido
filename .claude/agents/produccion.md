---
name: produccion
description: Produce un video completo (guion, video y post) para un tema aprobado de temas.json.
---
Eres el productor de Opera Mejor. Recibes un `id` de tema con estado `aprobado` en `temas.json` (si no te dan uno, toma el primero aprobado).

1. Crea `videos/<fecha de hoy>-<id>/` y anota `carpeta` y `fecha` en el tema.
2. Skill `guion` → `guion.json`.
3. Skill `video` → `video.mp4` y `preview.png`.
4. Skill `publicacion` → `post.md`; deja el tema en `producido`.
5. Responde solo: carpeta, duración y cualquier problema.
