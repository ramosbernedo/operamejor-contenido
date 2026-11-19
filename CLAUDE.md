# Opera Mejor — fábrica de contenido

Consultora de supply chain + IA en Perú. Público: dueños de bodegas, minimarkets y pymes. Videos verticales de 25–40 s en español peruano, tuteando, sin jerga.

El usuario es nuevo en programación: respóndele breve y sin tecnicismos.

## Flujo
`temas.json` guarda cada idea con su `estado`: idea → aprobado → producido → revisado → publicado (o `rechazado`).
1. Domingo: agente **research** propone ideas (estado `idea`) y el usuario aprueba.
2. Diario: agente **produccion** toma el siguiente `aprobado`, usa las skills guion → video → publicacion.
3. Agente **revisor** revisa y deja el video `revisado` o lo devuelve.

Carpeta de cada video: `videos/AAAA-MM-DD-tema/` con guion.json, post.md, revision.md. Los MP4 y WAV no se suben a git.
Al terminar, haz commit y push a `main`.
