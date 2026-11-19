# Opera Mejor — Fábrica de contenido

Videos verticales (TikTok / IG / LinkedIn) hechos a partir de un guion.

- `plantilla/` — el motor que convierte un guion en video.
- `videos/AAAA-MM-DD-tema/` — un video por carpeta (guion, post, revisión). Los MP4 van a Cloudflare R2, no aquí.
- `temas.json` — lista de ideas y en qué estado está cada una.
- `skills/` — instrucciones para Claude (por hacer).
- `HANDOFF.md` — el plan completo.

Hacer un video: `plantilla/hacer_video.sh videos/2026-11-19-stock-de-seguridad`
