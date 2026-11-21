Resultado: CAMBIOS

Revisado el 2026-11-21 (guion.json, post.md, preview.png, video.mp4 y 14 cuadros extraídos de 1 a 27.5 s).
Este archivo reemplaza la revisión anterior, que era de la versión con el "10%" inventado (6000 × 10% = 600) y ya no corresponde al video actual.

## Lo que está bien
- Cuenta: 1500 × 15% = 225. Coinciden la voz, los `datos` y lo que se ve en pantalla.
- Cifras: el tope ya no es un número suelto, sale de los números del negocio (venta semanal × margen). S/ 1,500 y 15% se dicen como "Ejemplo" y llevan el sello EJEMPLO. Son cifras realistas para una bodega chica (unos S/ 215 al día).
- Estrategia completa: objetivo (no fiar con la plata del proveedor), criterio (clientes de cada semana), pasos, cuándo (cada sábado) y meta medible (tope de S/ 225, no fiar más hasta cobrar).
- Solución: la cuenta del tope más los pasos son 48 de 73 palabras (66 %). Supera el 40 %.
- Técnico: el audio existe, la duración es de 28.3 s (dentro de 25–40 s) y el video mide 1080×1920. Ortografía y tildes correctas. El post es coherente con el video, el CTA `asesoria` es el mismo en voz, pantalla y post, y los hashtags están bien.

## Problemas (con la corrección exacta)

1. **Subtítulo encima de la etiqueta (escena 01, de 9 a 11 s aprox.).** La frase "Ejemplo: vendes mil quinientos a la semana y ganas el quince por ciento." ocupa 3 líneas, y la palabra "ciento." queda encima de "// 01 · tu tope". Hay que acortarla a 2 líneas:
   - chunk 0 de la escena 01 → `"Ejemplo: vendes mil quinientos y ganas *quince por ciento*."`
   - chunk 1 de la escena 01 → `"Tu tope: *doscientos veinticinco* soles."`

2. **La lógica de la regla no se explica bien (regla 0).** "Si fías más, estás prestando la plata del proveedor" no explica por qué el tope es *una semana* de ganancia y no un mes. La razón real es que cobras cada semana: lo que fías hasta el sábado tiene que salir de la ganancia de esa semana. Lo que pase de eso sale del dinero para reponer. Hay que unir la regla con el ciclo de cobro:
   - chunk 1 de la escena impacto → `"Cobras cada sábado: más que eso sale de la plata del *proveedor*."`

3. **Falta cómo saber si llegaste al tope (regla 0b).** El paso "anota fecha, nombre y monto" no dice cuándo comparar el total con los S/ 225, así que el dueño no sabe cuándo se activa el "no fías más". Cambio:
   - `pasos` → `["Solo a clientes fijos", "Anota y suma cada noche", "Cobra cada sábado"]`
   - chunks de la escena 02 → `"Uno: fía solo a clientes *fijos*."`, `"Dos: anota cada fiado y súmalo cada *noche*."`, `"Tres: cobra cada *sábado*."`, `"Si llegas al tope, no fías más hasta *cobrar*."`

4. **Montos sin moneda en pantalla.** "1500" y "225" salen sin "S/". Para que no se corten las cajas, propongo cambiar las etiquetas en lugar de los números:
   - `terminos[0]` → `["1500", "soles/semana"]`
   - `resultado` → `["225", "soles: tope"]`

5. **Largo (menor).** Son 73 palabras habladas y 28 s. El guion pide 40–60 palabras (15–22 s). Con los cambios 1–3 y el chunk 0 de la escena impacto como `"Tu fiado no debe pasar tu *ganancia* semanal."`, el total baja a unas 65 palabras.

6. **Post (menor).** Si se aplican los cambios 2 y 3, actualizar los textos para que sigan coherentes:
   - TikTok: "Fía solo a clientes fijos, anota y suma cada noche y cobra cada sábado."
   - Instagram, paso 2: "2) Anota cada fiado y suma el total cada noche."
   - Instagram, el "¿Por qué?": "Porque cobras cada sábado: lo que fíes en la semana debe salir de tu ganancia, no de la plata para reponer."

Después de corregir, hay que regenerar el video y volver a revisarlo. El tema no pasa a `revisado` en el panel hasta entonces.
