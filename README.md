# Opera Mejor — Fábrica de contenido

Videos verticales (TikTok / IG / LinkedIn) hechos a partir de un guion.

- `plantilla/` — el motor que convierte un guion en video.
- `videos/AAAA-MM-DD-tema/` — un video por carpeta (guion, post, revisión). Los MP4 van a Cloudflare R2, no aquí.
- `panel/` — página para aprobar temas deslizando (https://claude.ai/artifact/PmEKYNt6r4M2ig3rkhS2GE).
- `.claude/skills/` y `.claude/agents/` — las skills y agentes de Claude.
- `HANDOFF.md` — el plan completo.

Hacer un video: `plantilla/hacer_video.sh videos/2026-11-19-stock-de-seguridad`
