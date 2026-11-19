---
name: research
description: Buscar y proponer temas nuevos para los videos de Opera Mejor y agregarlos a temas.json como ideas.
---
# Research de temas

1. Lee la colección `temas` del panel (ver CLAUDE.md) para no repetir temas (ni los rechazados).
2. Busca en la web problemas reales de inventario, compras, ventas y operación en bodegas, minimarkets y pymes de Perú (y usos de IA útiles para ellas). Prefiere fuentes peruanas y datos recientes.
3. Agrega las ideas que falten (para llegar a ~10 pendientes) con un solo `ArtifactData` batch, cada una con `estado: "idea"`, `creado` (ahora, ISO), `tema` (máx. 5 palabras), `angulo` (el problema concreto en una frase, con un ejemplo de bodega), `formato` rotando entre `error`, `formula` y `mito`, y `fuente` (enlace o "conocimiento general").
4. El usuario aprueba deslizando en el panel. No le pidas que apruebe por chat: solo mándale el link del panel en una línea.
