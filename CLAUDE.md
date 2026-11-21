# Opera Mejor — fábrica de contenido

Opera Mejor (Perú) da herramientas e IA para que los negocios operen mejor: ventas, finanzas y caja, precios, inventario y compras, atención al cliente, marketing, personal y procesos. No es solo logística. **El contenido existe para vender**: muestra estrategias (métodos con objetivo, criterio y meta) que el dueño quiera implementar con ayuda de Opera Mejor, no consejos sueltos.
Público: dueños de bodegas, minimarkets, restaurantes, tiendas y pymes. Videos verticales de 15–22 s en español peruano, tuteando, sin jerga.

El usuario es nuevo en programación: respóndele breve y sin tecnicismos.

## Temas: el panel es la lista
Los temas viven en la base de datos del panel **https://claude.ai/artifact/PmEKYNt6r4M2ig3rkhS2GE** (código en `panel/aprobar.html`), colección `temas`. Léela y escríbela con la herramienta `ArtifactData` (carga su esquema con ToolSearch "select:ArtifactData"). Siempre pasa `if_version` al modificar un tema existente.

Cada tema (doc id = id corto con guiones): `tema`, `angulo`, `formato` (sistema | decision | antes_despues; los antiguos error | formula | mito ya no se usan), `fuente`, `estado`, `creado` (fecha ISO), `potencial` (1–5), `porque`; al producirlo `carpeta` y `cta`; al publicarlo `vistas`, `likes`, `comentarios`, `guardados`, `retencion_prom_seg`, `vio_completo_pct`, `fecha_publicacion` (el usuario pasa capturas de TikTok Studio; anótalas en el panel).
Estados: idea → aprobado (o rechazado, lo decide el usuario deslizando en el panel; desde ahí también puede pedir 5 temas nuevos a Claude y anotar resultados de cada video) → producido → revisado → publicado.

## El panel es la central de contenido
El usuario no quiere buscar nada en las conversaciones: **todo video terminado va al panel** (video subido como asset + textos de cada red + guion + duración, ver agente produccion paso 5). Al avisarle, mándale el link del panel.

## Stock de seguridad de temas
Siempre debe haber **7 temas aprobados**. Cada mañana, antes de producir: si hay menos de 7 aprobados y menos de 10 ideas pendientes, el agente **research** agrega ideas nuevas y se avisa al usuario con el link del panel.

## Flujo diario (7:30 am, video para hoy)
1. Revisar stock de temas (arriba).
2. Agente **produccion**: toma el aprobado más antiguo → guion → video → post.
3. Agente **revisor**: revisa y corrige.

Carpeta de cada video: `videos/AAAA-MM-DD-id/` con guion.json, post.md, revision.md. Los MP4 y WAV no se suben a git.
Al terminar, haz commit y push a `main`.
