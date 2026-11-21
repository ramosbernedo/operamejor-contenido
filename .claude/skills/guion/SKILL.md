---
name: guion
description: Escribir el guion.json de un video de Opera Mejor a partir de un tema aprobado.
---
# Guion

Escribe `videos/AAAA-MM-DD-<id>/guion.json`: una lista de 4–6 escenas, la última siempre `cierre`. Total hablado: 40–60 palabras (15–22 s). Videos cortos retienen más.

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
- **Ritmo:** 1–2 frases por escena (cada escena dura 2–3 s). 4–5 escenas en total.
- `chunks`: 1–3 frases cortas (máx. ~8 palabras) que dice la voz. Una palabra clave entre `*` por frase. **Escribe los números en letras** ("setenta y cinco") para que la voz los lea bien.
- `n`: número de escena (no en el cierre). `sello` (opcional): 1–2 palabras; `frase` = índice del chunk tras el cual aparece (por defecto el último).

## Tipos y sus `datos`
- `impacto` — **siempre la escena 1**: la cifra del gancho gigante a pantalla completa, sin título, etiqueta ni mascota. `cifra` (corta, ej. "S/ 300"), `sub` (máx. 6 palabras). `label` y `title` vacíos (`""`, `[""]`), sin `n`. 1–2 frases.
- `lista` — algo que se acaba: `inicio`, `fin`, `icono` ("botella" | "caja"), `etiqueta`.
- `barras` — comparar: `etiquetas`, `valores` (máx. 7), `destacar` (índice), `promedio`, `nota`.
- `curva` — stock que baja a cero: `inicio`, `dias_hasta_cero`, `dias`, `etiqueta`, `llegada`.
- `formula` — cuenta paso a paso: `titulo`, `subtitulo`, `terminos` (`[["20","venta/día"], "×", ["3","días"]]`), `resultado` (`["60","pide aquí"]`). Con `titulo`, el chunk 0 presenta y el chunk 1 recorre la cuenta.
- `mito` — `mito`, `realidad` (frases de máx. 12 palabras).
- `pasos` — la solución en 2–4 pasos concretos que aparecen uno por frase: `pasos` (máx. 6 palabras cada uno). Un chunk por paso.
- `texto` — una idea fuerte: `grande` (máx. 6 palabras), `chico`.
- `cierre` — `pregunta` opcional (por defecto "¿Qué tema sigue?").

## Reglas
- **Gancho (lo más importante):** la escena 1 abre con la cifra o consecuencia más fuerte del video, no con el contexto. Ej.: "Un cliente perdido te cuesta *dos mil quinientos soles* al año." y luego se explica. El título de la escena 1 también muestra esa cifra/pérdida.
  Aprendizaje (quiebre de stock, 464 vistas): la gente se iba a los 5.8 s y solo 4.9 % lo vio completo; el número fuerte estaba recién en la escena 3.
- Nada de relleno: cada frase debe dar un dato nuevo.
- **Contexto antes de la cuenta:** después del gancho, una frase que cuente la situación (quién, qué pasó). Sin eso la cuenta no se entiende.
- **La solución es la mitad del valor:** al menos el 40% del tiempo hablado. Debe decir **qué hacer, cuánto y cuándo** (ej.: "al cerrar, multiplica tu venta por 0.85 y guarda eso"; "máximo S/ 50 por vecino, cobra cada sábado"). Prohibido cerrar con frases vagas tipo "separa la plata", "pon un límite", "controla tu stock". Si son varios pasos, usa el tipo `pasos`.
- **La solución sale de los mismos números del video** y explica su porqué (ej.: "vendes 4 por semana y vence en 2 → lleva 8"), nunca una regla suelta.
- Prueba final: ¿un bodeguero que no sabe nada del tema entiende el video a la primera? ¿Sabe **exactamente qué hacer mañana**? Si no, reescribe.
- Cuidado con unidades de tiempo: un saldo (lo que te deben hoy) no es "al mes".
- Los números deben cuadrar: lo que dice la voz = lo que muestran los datos = la cuenta correcta.
- Ejemplos de bodega peruana (gaseosas, arroz, aceite, Yape, proveedor que tarda). Nada de inglés innecesario.

## Llamado a la acción (prueba de qué funciona)
El `cierre` rota entre 3 llamados. Mira en el panel el `cta` de los últimos temas producidos y usa el que toque:
- `comentar` — voz: "¿Te pasó? *Coméntalo*." · `pregunta`: "¿Te pasó?"
- `calculadora` — voz: "Calcula tu stock gratis en *OperaMejor.pe*." · `pregunta`: "OperaMejor.pe"
- `whatsapp` — voz: "¿Quieres ayuda? *Escríbenos*." · `pregunta`: "Link en la bio"

Anota el llamado usado como `cta` en el tema del panel.
