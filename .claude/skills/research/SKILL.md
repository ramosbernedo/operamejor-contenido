---
name: research
description: Buscar y proponer temas nuevos para los videos de Opera Mejor y agregarlos como ideas al panel.
---
# Research de temas

1. Lee la colección `temas` del panel (ver CLAUDE.md) para no repetir temas (ni los rechazados).
   **Aprende de los resultados:** mira los temas `publicado` con `vistas`, `retencion_prom_seg`, `vio_completo_pct`, `guardados`, `comentarios` y `cta`. La retención dice si el gancho funcionó; los guardados, si el tema es útil. ¿Qué formatos, ángulos y ganchos funcionaron mejor? Propón más de eso. Lo rechazado por el usuario también enseña qué no le gusta.
2. Busca en la web problemas reales de pymes peruanas (bodegas, minimarkets, restaurantes, tiendas) en **todas las áreas del negocio**: ventas, caja y finanzas, precios y márgenes, inventario y compras, atención al cliente, marketing, personal, procesos y usos prácticos de IA. Varía las áreas: no más de 2 de cada 7 ideas sobre inventario. Prefiere fuentes peruanas y datos recientes.
3. Agrega las ideas que falten (para llegar a ~10 pendientes) con un solo `ArtifactData` batch, cada una con `estado: "idea"`, `creado` (ahora, ISO), `tema` (máx. 5 palabras), `angulo` (el problema concreto en una frase, con un ejemplo de bodega), `formato` rotando entre `sistema`, `decision` y `antes_despues` (son estrategias, no consejos: cada idea debe tener objetivo, criterio y meta medible), `fuente` (enlace o "conocimiento general"),
   `potencial` (1–5) y `porque` (una línea que explica el puntaje).

   **Potencial** = suma de 3 señales, redondeada a 1–5:
   - **Demanda:** ¿la gente lo busca o pregunta? (Google, TikTok, grupos de bodegueros/emprendedores de Perú, resultados de nuestros videos)
   - **Gancho:** ¿se puede abrir con una frase que pare el scroll en 2 segundos?
   - **Dolor o plata:** ¿toca pérdida de ventas, dinero parado, robo, vencimientos?
   Sé exigente: un 5 es raro. Pon primero (con `creado` más antiguo) las ideas de mayor potencial.
4. El usuario aprueba deslizando en el panel. No le pidas que apruebe por chat: solo mándale el link del panel en una línea.
