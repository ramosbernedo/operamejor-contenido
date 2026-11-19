---
name: research
description: Buscar y proponer temas nuevos para los videos de Opera Mejor y agregarlos a temas.json como ideas.
---
# Research de temas

1. Lee `temas.json` para no repetir temas.
2. Busca en la web problemas reales de inventario, compras, ventas y operación en bodegas, minimarkets y pymes de Perú (y temas de IA útiles para ellas). Prefiere fuentes peruanas y datos recientes.
3. Propón **7 ideas** y agrégalas con `"estado": "idea"`. Cada una con:
   - `id` (corto, con guiones), `tema`, `angulo` (el problema concreto en una frase, con un ejemplo de bodega)
   - `formato`: rota entre `error` (error común), `formula` (fórmula en 30 s) y `mito` (mito vs realidad)
   - `fuente`: enlace o "conocimiento general" si es un concepto clásico
4. Al usuario muéstrale solo una lista numerada corta: `1. Tema — ángulo (formato)`. Pregúntale cuáles aprueba. Cuando responda, cambia esas a `aprobado` y las demás a `rechazado`.
