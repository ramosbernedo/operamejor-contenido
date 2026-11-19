---
name: guion
description: Escribir el guion.json de un video de Opera Mejor a partir de un tema aprobado.
---
# Guion

Escribe `videos/AAAA-MM-DD-<id>/guion.json`: una lista de 4–6 escenas, la última siempre `cierre`. Total hablado: 60–90 palabras (≈30 s).

## Formatos
- **error**: el problema → por qué pasa (el error) → la solución con números → cierre.
- **formula**: el problema → los datos → la fórmula paso a paso (`formula`) → cierre.
- **mito**: el mito (`mito`) → por qué es falso → qué hacer → cierre.

Ejemplos completos en `plantilla/ejemplos/`.

## Cada escena
```json
{"label": "// 01 · el problema", "title": ["SIN STOCK", "EL *SÁBADO*"], "n": 1, "tipo": "lista",
 "datos": {...}, "sello": {"texto": "VENTA PERDIDA"},
 "chunks": ["¿Tu bodega se queda sin *gaseosas*", "justo el *sábado*?"]}
```
- `title`: 1–2 líneas en MAYÚSCULAS, máx. ~11 letras por línea. Lo que va entre `*` sale en rojo (solo al final de la línea).
- `chunks`: 1–3 frases cortas (máx. ~8 palabras) que dice la voz. Una palabra clave entre `*` por frase. **Escribe los números en letras** ("setenta y cinco") para que la voz los lea bien.
- `n`: número de escena (no en el cierre). `sello` (opcional): 1–2 palabras; `frase` = índice del chunk tras el cual aparece (por defecto el último).

## Tipos y sus `datos`
- `lista` — algo que se acaba: `inicio`, `fin`, `icono` ("botella" | "caja"), `etiqueta`.
- `barras` — comparar: `etiquetas`, `valores` (máx. 7), `destacar` (índice), `promedio`, `nota`.
- `curva` — stock que baja a cero: `inicio`, `dias_hasta_cero`, `dias`, `etiqueta`, `llegada`.
- `formula` — cuenta paso a paso: `titulo`, `subtitulo`, `terminos` (`[["20","venta/día"], "×", ["3","días"]]`), `resultado` (`["60","pide aquí"]`). Con `titulo`, el chunk 0 presenta y el chunk 1 recorre la cuenta.
- `mito` — `mito`, `realidad` (frases de máx. 12 palabras).
- `texto` — una idea fuerte: `grande` (máx. 6 palabras), `chico`.
- `cierre` — `pregunta` opcional (por defecto "¿Qué tema sigue?").

## Reglas
- Los números deben cuadrar: lo que dice la voz = lo que muestran los datos = la cuenta correcta.
- Ejemplos de bodega peruana (gaseosas, arroz, aceite, Yape, proveedor que tarda). Nada de inglés innecesario.
