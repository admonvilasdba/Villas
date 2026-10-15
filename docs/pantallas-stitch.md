# Vila's — Pantallas y requerimientos para Stitch

Especificación funcional y de dirección visual de las pantallas **públicas** de
la carta digital de Vila's. Sirve como brief para diseñar en Stitch.

> Regla de oro: diseñar **solo lo que existe**. Esta carta es de **consulta**, no
> de pedidos. No inventar botones, formularios ni páginas que el backend no
> tenga.

---

## 1. Contexto del proyecto

- **Restaurante:** Vila's. Concepto **familiar, elegante y semi-casual**. No hay
  código de vestimenta.
- **Producto:** carta digital. La parte pública **muestra** lo que se publica
  desde el panel de administración; no permite al cliente modificar nada.
- **Stack:** backend en Django, HTML semántico con clases y estilos base. El
  diseño visual se define en Stitch y luego se aplica a las plantillas.
- **Idiomas:** Español (por defecto) e Inglés.

### Rutas reales existentes

| Ruta | Pantalla | Estado |
|---|---|---|
| `/es/` | Carta pública (Español) | Implementada |
| `/en/` | Carta pública (Inglés) | Implementada |
| `/admin/` | Panel de administración (Django Admin) | Implementado, **no se diseña aquí** |

Toda ruta no listada arriba **no existe** y no debe representarse.

---

## 2. Alcance y restricciones

### 2.1 Elementos PROHIBIDOS (no diseñar)

Para que la carta no prometa funcionalidad inexistente, **no incluir**:

- Carrito de compras, "Añadir al pedido", "Pedir", "Ordenar".
- Pagos, cajas, checkout, propinas.
- Reservaciones de mesa o de eventos.
- Cuentas de usuario: "Iniciar sesión", "Registrarse", "Mi perfil".
- Buscador, filtros avanzados, ordenamiento por el usuario.
- Favoritos, "Me gusta", compartir en redes desde la carta.
- Enlaces a rutas que no existan (ver sección 1).
- Formularios de cualquier tipo.
- Pop-ups promocionales, banners de descuentos, cookies.

### 2.2 Elementos PERMITIDOS (interacciones reales)

- **Selector de idioma** ES / EN.
- **Navegación por anclas** entre categorías dentro de la misma página.
- **Abrir y cerrar el modal** de un platillo al hacer click en su tarjeta.
- **Enlaces externos** a las redes sociales (Facebook, Instagram, TikTok) y a la
  ubicación en el footer.
- Enlaces de navegación interna que vuelvan a la propia carta.

### 2.3 Naturaleza del contenido

- Todo el contenido (categorías, subcategorías, platillos, precios, fotos,
  tiempos) es **dinámico** y viene del backend. Para el diseño, usar **datos de
  ejemplo plausibles** de un restaurante familiar.
- Los platillos **agotados o sin precio visible no aparecen**: la carta solo
  muestra lo disponible. No diseñar un estado "Agotado" en la tarjeta.
- Si una categoría o subcategoría no tiene platillos disponibles, **no se
  muestra**.

---

## 3. Inventario de pantallas

1. **Carta pública** (página única con navegación de anclas) — `/es/`, `/en/`.
2. **Modal de platillo** (capa flotante sobre la carta).
3. **Sobre nosotros** (pantalla informativa).

Estados transversales a documentar: **estado vacío**, **hover** y **elemento
activo**.

---

### 3.1 Pantalla: Carta pública

- **Objetivo:** que el cliente explore la carta de forma clara y apetecible.
- **Ruta:** `/es/` y `/en/`. Es una **página única**; todas las categorías
  conviven en la misma vista.

**Bloques (de arriba a abajo):**

1. **Header (fijo/sticky):**
   - Logo o nombre "Vila's" a la izquierda (enlace a la propia carta).
   - Selector de idioma ES / EN a la derecha (dos opciones; marcar la activa).
2. **Título principal:** `Nuestra Carta` (traducible).
3. **Navegación de anclas:** lista horizontal de las categorías visibles; al
   tocar una, hace scroll a su sección. Debe poder desplazarse en horizontal en
   móvil.
4. **Secciones por categoría** (repetible):
   - **Título de categoría** (H2).
   - **Bloques de subcategoría** (repetible):
     - **Título de subcategoría** (H3).
     - **Lista de tarjetas de platillo** (repetible).
5. **Footer:** tres zonas.
   - **Izquierda:** enlaces a las **3 redes sociales**: Facebook, Instagram y
     TikTok (iconos/enlaces externos, sin formularios ni widgets embebidos).
   - **Centro:** el **eslogan** (lema): "Vila's Su Mejor Opción Desde Diciembre
     2009".
   - **Derecha:** el **nombre del local** ("Vila's") y un **enlace a la
     ubicación** (p. ej. "Cómo llegar" → mapa externo).

**Tarjeta de platillo (elemento clickeable):**
- Imagen del platillo (si existe; si no, se muestra solo el texto).
- Nombre del platillo.
- Precio.
- Descripción breve (si existe).
- Tiempo de preparación (si existe), p. ej. "15 min".
- Toda la tarjeta es clickeable y abre el **modal de platillo**.

**Estados:**
- **Normal:** tarjeta con imagen, nombre, precio, descripción y tiempo.
- **Sin imagen:** la tarjeta se adapta sin dejar hueco.
- **Hover / foco (desktop):** realce sutil (elevación, borde o cambio de fondo).
- **Activo:** el idioma seleccionado en el selector.
- **Vacío:** cuando no hay ningún platillo disponible, mostrar un mensaje
  centrado: "La carta estará disponible pronto." (sin tarjetas ni navegación de
  anclas).

**Responsive:**
- **Móvil:** una sola columna de tarjetas, imágenes cómodas, nav de anclas con
  scroll horizontal, header compacto.
- **Tablet/Desktop:** tarjetas en una o dos columnas; aprovechar el ancho con
  márgenes generosos; la imagen puede ir a la izquierda y el texto a la derecha.

**Jerarquía tipográfica:** ver sección 5.

---

### 3.2 Pantalla/estado: Modal de platillo

- **Objetivo:** mostrar el detalle del platillo sin salir de la carta.
- **Disparador:** click (o tap) en una tarjeta de platillo.
- **Naturaleza:** capa flotante superpuesta, con fondo oscurecido detrás.

**Contenido (de arriba a abajo):**
1. **Imagen grande** del platillo (protagonista).
2. **Nombre del platillo.**
3. **Tiempo de preparación**, p. ej. "Tiempo de preparación: 15 min".
4. **Descripción breve** del platillo.
5. **Precio.**

**Comportamiento:**
- **Cerrar:** con un botón "X" en una esquina, click/tap fuera del panel, o la
  tecla `Esc`.
- **Sin botones de pedido.** El modal es solo informativo.

**Estados:**
- **Sin imagen:** diseño de respaldo elegante (fondo con textura colonial),
  nunca un marco vacío.
- **Sin descripción o sin tiempo:** el bloque se omite sin dejar espacios raros.

**Responsive:** en móvil ocupa casi toda la pantalla (o se presenta como hoja
inferior); en desktop es una tarjeta centrada con ancho máximo cómodo de lectura.

---

### 3.3 Pantalla: Sobre nosotros

- **Objetivo:** contar quién es Vila's; reforzar el carácter familiar y
  acogedor.
- **Ruta propuesta (a implementar):** `/es/nosotros/` y `/en/about/`.
- **Nota:** esta pantalla **aún no existe en el backend**; se especifica aquí
  para diseñarla y luego implementarla.

**Bloques sugeridos:**
1. **Header** igual al de la carta.
2. **Título:** el nombre del restaurante o "Sobre nosotros".
3. **Historia:** texto breve sobre el origen y la familia detrás de Vila's.
4. **Ambiente/valores:** 2–3 puntos (familiar, cocina, hospitalidad).
5. **Galería de fotos** del lugar y de los platillos.
6. **Información práctica** (opcional): horario, dirección y contacto, si el
   negocio lo proporciona.
7. **Footer** (el mismo de la carta): redes sociales a la izquierda; eslogan al
   centro; nombre del local y enlace a la ubicación a la derecha.

**Enlaces permitidos:** solo "Ver carta" (lleva a `/es/` o `/en/`). Nada de
reservas ni pedidos.

**Responsive:** bloques apilados en móvil; en desktop alternar imagen y texto.

---

## 4. Componentes reutilizables

| Componente | Descripción |
|---|---|
| **Header** | Logo/nombre + selector de idioma. Fijo al hacer scroll. |
| **Selector de idioma** | Dos opciones (ES / EN); la activa se distingue. |
| **Nav de anclas** | Accesos a cada categoría; scroll horizontal en móvil. |
| **Título de categoría** | Encabezado de sección (H2). |
| **Título de subcategoría** | Encabezado de grupo (H3). |
| **Tarjeta de platillo** | Imagen, nombre, precio, descripción, tiempo. Clickeable. |
| **Modal de platillo** | Detalle ampliado del platillo. |
| **Estado vacío** | Mensaje cuando no hay platillos disponibles. |
| **Footer** | Tres zonas. Izquierda: enlaces a Facebook, Instagram y TikTok. Centro: eslogan "Vila's Su Mejor Opción Desde Diciembre 2009". Derecha: nombre del local y enlace a la ubicación. |

---

## 5. Dirección visual

### 5.1 Concepto

**Colonial elegante, fondo claro con tonos oscuros.** Sobrio, cálido y familiar;
accesible sin ser informal. Debe sentirse como una carta impresa de buen gusto
llevada a la pantalla.

### 5.2 Tipografía

Se usan tres familias, con equivalentes libres de Google Fonts para verse igual
en todos los dispositivos.

| Elemento | Fuente | Fuente web (Google Fonts) | Uso |
|---|---|---|---|
| Títulos (H1 "Nuestra Carta" y H2 categorías) | **Didot** | `GFS Didot` | Encabezados de máximo nivel |
| Subcategorías (H3) y **nombre de platillo** | **Bodoni** | `Bodoni Moda` | Subencabezados |
| Contenido | **Times New Roman** | Fuente del sistema (websafe) | Precio, descripción, tiempo, nav, footer |

**Nombre del platillo:** se destaca con la familia Bodoni (misma que las
subcategorías, pero con **mayor peso y algo más de tamaño**) para resaltar sin
introducir una cuarta fuente ni competir con los títulos en Didot.

**Stacks CSS sugeridos:**
- Títulos: `'GFS Didot', Didot, 'Playfair Display', serif`
- Subencabezados: `'Bodoni Moda', 'Bodoni MT', 'Libre Bodoni', serif`
- Contenido: `'Times New Roman', Times, serif`

### 5.3 Paleta

| Rol | Color | Hex |
|---|---|---|
| Fondo pergamino (claro) | Crema cálido | `#F4EDE1` |
| Superficie oscura (madera) | Café profundo | `#2B1B14` |
| Texto sobre claro | Café casi negro | `#2B1B14` |
| Texto sobre oscuro | Crema | `#F4EDE1` |
| Acento principal | Dorado/bronce | `#B08D57` |
| Acento secundario | Vino/terracota | `#7B2D26` |

Reglas: fondos claros predominantes; los oscuros se usan para el header/footer,
el fondo del modal y bloques que necesiten contraste.

### 5.4 Motivos y texturas

- Referencias coloniales sutiles: **arcos**, **azulejo/talavera**, **hierro
  forjado**, **madera**.
- Ornamentos discretos y simétricos; nada recargado.
- Líneas finas como separadores entre secciones (usar el acento dorado).

### 5.5 Fotografía

- Luz **cálida**, tonos naturales.
- Fondos de **madera** o superficies oscuras que hagan resaltar el platillo.
- Encuadre cercano y apetecible; consistencia entre todas las fotos.

### 5.6 Tono y sensación

Acogedor, familiar, con aire premium pero accesible. La carta debe leerse con
facilidad y dar hambre; no debe sentirse como una app tecnológica.

---

## 6. Guía de uso en Stitch

1. Diseñar **una pantalla a la vez**, en este orden: Carta pública → Modal de
   platillo → Sobre nosotros.
2. Pegar como prompt la ficha de esa pantalla (sección 3) **junto con** la lista
   de restricciones (sección 2). Es clave incluir siempre la sección 2.1 para
   que no aparezcan botones innecesarios.
3. Indicar la dirección visual (sección 5) en el design system del proyecto para
   mantener la coherencia entre pantallas.
4. Revisar cada resultado contra la sección 2: si aparece cualquier elemento
   prohibido, corregir antes de aprobarlo.
5. Entregar el diseño aprobado para aplicarlo a `templates/` (fase posterior).

---

## 7. Anexo — Datos que alimentan la pantalla

Variables que la plantilla de la carta recibe del backend (para respetar los
límites de cada elemento):

- `categories[]`
  - `name`, `slug`
  - `visible_subcategories[]`
    - `name`, `slug`
    - `dishes[]`
      - `name`
      - `image.url` (puede no existir)
      - `price`
      - `description` (puede estar vacía)
      - `prep_time_display` (puede estar vacío)

Textos de interfaz traducibles: `Carta`, `Nuestra Carta`,
`Tiempo de preparación`, `La carta estará disponible pronto.`
