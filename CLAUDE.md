# Opera Mejor — fábrica de contenido

Consultora de supply chain + IA en Perú. Público: dueños de bodegas, minimarkets y pymes. Videos verticales de 25–40 s en español peruano, tuteando, sin jerga.

El usuario es nuevo en programación: respóndele breve y sin tecnicismos.

## Temas: el panel es la lista
Los temas viven en la base de datos del panel **https://claude.ai/artifact/PmEKYNt6r4M2ig3rkhS2GE** (código en `panel/aprobar.html`), colección `temas`. Léela y escríbela con la herramienta `ArtifactData` (carga su esquema con ToolSearch "select:ArtifactData"). Siempre pasa `if_version` al modificar un tema existente.

Cada tema (doc id = id corto con guiones): `tema`, `angulo`, `formato` (error | formula | mito), `fuente`, `estado`, `creado` (fecha ISO), `potencial` (1–5), `porque`; al producirlo `carpeta` y `cta`; al publicarlo `vistas`, `likes`, `comentarios`, `guardados`, `retencion_prom_seg`, `vio_completo_pct`, `fecha_publicacion` (el usuario pasa capturas de TikTok Studio; anótalas en el panel).
Estados: idea → aprobado (o rechazado, lo decide el usuario deslizando en el panel) → producido → revisado → publicado.

## Stock de seguridad de temas
Siempre debe haber **7 temas aprobados**. Cada mañana, antes de producir: si hay menos de 7 aprobados y menos de 10 ideas pendientes, el agente **research** agrega ideas nuevas y se avisa al usuario con el link del panel.

## Flujo diario (7:30 am, video para hoy)
1. Revisar stock de temas (arriba).
2. Agente **produccion**: toma el aprobado más antiguo → guion → video → post.
3. Agente **revisor**: revisa y corrige.

Carpeta de cada video: `videos/AAAA-MM-DD-id/` con guion.json, post.md, revision.md. Los MP4 y WAV no se suben a git.
Al terminar, haz commit y push a `main`.
