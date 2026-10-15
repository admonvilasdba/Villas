# AGENTS.md — Vila's Carta Digital

Guía para desarrolladores que trabajen en este repositorio. Describe cómo está
estructurado el proyecto, cómo correrlo y dónde configurar las cosas importantes
(clave de ImgBB, base de datos, despliegue, etc.).

## Descripción general

Carta digital del restaurante **Vila's**, dividida en dos partes:

- **Privada (`/admin/`)**: panel de Django Admin (requiere login) donde se crean,
  editan y retiran categorías, subcategorías y platillos, incluyendo descripción,
  precio, tiempo de preparación, imagen y disponibilidad.
- **Pública (`/es/` y `/en/`)**: carta que solo muestra lo publicado en `/admin/`.
  Las categorías, subcategorías y platillos sin contenido visible se ocultan, y
  los platillos marcados como no disponibles (agotados) **no se muestran**.

El frontend público es HTML/CSS/JS servido con plantillas de Django. El diseño
visual se trabaja aparte (Stitch); este repositorio contiene el backend y el
HTML semántico con clases listas para estilar.

## Qué se implementó (resumen y decisiones)

El proyecto ya es desplegable en Render. Resumen de lo construido y de las
decisiones tomadas (para no repetir caminos ya descartados):

- **Backend Django** (`menu/`): modelos `Category`/`SubCategory`/`Dish`, Admin
  con pestañas ES/EN e inlines, y vista pública `MenuView` que oculta lo vacío o
  agotado.
- **Imágenes con ImgBB**: se evaluó Cloudinary primero, pero se descartó por
  bloqueos de acceso desde Nicaragua. Se implementó el storage propio
  `ImgBBStorage` (`menu/storage.py`), que sube cada imagen a ImgBB y guarda la
  **URL directa** en la base de datos.
- **Base de datos en Supabase**: la base *free* de Render caducaba a los 90 días;
  se pasó a un **PostgreSQL permanente en Supabase**, conectado por `DATABASE_URL`.
- **Superusuario automático**: el plan free de Render no permite Shell interactiva,
  así que `create_admin` (`menu/management/commands/create_admin.py`) lo crea
  durante el build a partir de las variables `DJANGO_SUPERUSER_*`.
- **Interfaz ES/EN**: contenido con `django-modeltranslation` y textos de interfaz
  con gettext (`.mo` compilados con `polib`).
- **Diseño**: tema oscuro y assets en `static/` (`css/menu.css`, `js/menu.js`,
  `Imagenes/Logo.svg`); la referencia visual está en `docs/pantallas-stitch.md`.
- **Pruebas**: `python manage.py test` cubre modelos, vista, admin, storage y el
  comando `create_admin` (26 pruebas).

> Historial: Cloudinary y la base *free* de Render se evaluaron y se descartaron;
> no queda ninguna dependencia de ellos en el proyecto.

## Stack

| Componente | Tecnología |
|---|---|
| Framework | Django 6.1 |
| Base de datos | PostgreSQL permanente en Supabase / SQLite en local |
| Imágenes | ImgBB (`menu/storage.py`, backend de storage personalizado) |
| Archivos estáticos | Whitenoise (producción) |
| Traducciones | `django-modeltranslation` (contenido) + `gettext` (interfaz) |
| Servidor | Gunicorn |
| Hosting | Render (ver `render.yaml`) |
| Python | 3.14 |

## Estructura del proyecto

```
vilas_carta/
├── manage.py
├── requirements.txt          # dependencias (generado con pip freeze)
├── build.sh                  # build de Render: instala, collectstatic, migrate, create_admin
├── render.yaml               # infraestructura como código (solo el servicio web)
├── .env.example              # plantilla de variables de entorno
├── vilas_carta/
│   ├── settings.py           # configuración (lee variables de entorno)
│   ├── urls.py               # /admin/ y rutas públicas con prefijo de idioma
│   ├── wsgi.py / asgi.py
├── menu/                     # app principal
│   ├── models.py             # Category, SubCategory, Dish
│   ├── admin.py              # registro del Admin (inlines, pestañas ES/EN, acciones)
│   ├── apps.py               # MenuConfig (títulos del admin en ready())
│   ├── translation.py        # campos traducibles por modelo (modeltranslation)
│   ├── storage.py            # ImgBBStorage (sube imágenes a ImgBB, guarda URL)
│   ├── views.py              # MenuView (vista pública)
│   ├── urls.py               # rutas de la app
│   ├── tests.py              # tests de modelos, vista, admin, storage y create_admin
│   ├── management/commands/
│   │   └── create_admin.py   # crea el superusuario desde DJANGO_SUPERUSER_*
│   └── migrations/           # 0001_initial, 0002_alter_dish_image
├── templates/
│   ├── base.html             # layout + selector de idioma + footer
│   └── menu/index.html       # carta pública + sección "Sobre nosotros" (#about-us)
├── static/
│   ├── css/menu.css          # estilos del tema oscuro (aprobado en Stitch)
│   ├── js/menu.js            # interacciones de la carta
│   └── Imagenes/Logo.svg     # logo
├── locale/en/LC_MESSAGES/    # traducciones de interfaz (.po fuente + .mo compilado)
├── docs/pantallas-stitch.md  # especificación visual de las pantallas (Stitch)
├── media/                    # MEDIA_ROOT de referencia; sin uso (imágenes en ImgBB; ignorado por git)
└── staticfiles/              # salida de collectstatic (ignorado por git)
```

## Variables de entorno

El proyecto usa `python-decouple` y lee un archivo `.env` en la raíz
(no versionado). Copia `.env.example` a `.env` y complétalo.

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django. En producción Render la genera sola. |
| `DEBUG` | `True` en local, `False` en producción. |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por comas. |
| `CSRF_TRUSTED_ORIGINS` | Orígenes de confianza para CSRF (dominio de Render y dominio propio). |
| `DATABASE_URL` | Cadena de conexión a Supabase (producción). Vacío en local → SQLite. |
| `TIME_ZONE` | Zona horaria (por defecto `America/Mexico_City`). |
| `IMGBB_API_KEY` | Clave de API de ImgBB. Ver siguiente sección. |
| `DJANGO_SUPERUSER_USERNAME` | Usuario del superusuario. Lo usa el comando `create_admin`. |
| `DJANGO_SUPERUSER_EMAIL` | Correo del superusuario. Lo usa `create_admin`. |
| `DJANGO_SUPERUSER_PASSWORD` | Contraseña del superusuario. Lo usa `create_admin` (nunca se registra en logs). |

### Dónde poner la clave de ImgBB

Todo el almacenamiento de imágenes se controla con **una sola variable**:
`IMGBB_API_KEY`. La clave se obtiene en https://api.imgbb.com/ (Dashboard →
API).

- En **local**: abre tu `.env` (copia de `.env.example`) y añade:

  ```
  IMGBB_API_KEY=tu_clave_de_imgbb
  ```

- En **producción (Render)**: agrega la variable de entorno `IMGBB_API_KEY`
  en la configuración del servicio (Environment → Environment Variables). Está
  declarada en `render.yaml` con `sync: false`, así que Render te pedirá el
  valor al crear el servicio.

**Comportamiento:**

- El storage por defecto es `menu.storage.ImgBBStorage`
  (`vilas_carta/settings.py`, bloque `STORAGES`): cada imagen subida se envía a
  la API de ImgBB y en la base de datos se guarda la **URL directa**.
- Si `IMGBB_API_KEY` no está definida, subir una imagen falla con
  `ImproperlyConfigured` (no hay almacenamiento local de respaldo).
- `build.sh` **no** necesita la clave; solo se usa en runtime.

**Flujo de una subida de imagen:**

1. En `/admin/` se sube la imagen del platillo (`Dish.image`).
2. Django llama a `ImgBBStorage._save()`, que hace `POST` a
   `https://api.imgbb.com/1/upload` (multipart: campo `image`; query: `key`),
   con `timeout=30`.
3. ImgBB responde `200` con la URL directa; esa URL se guarda en `Dish.image`.
4. Si falla, `_save` lanza `RuntimeError` (no se guarda nada); sin
   `IMGBB_API_KEY` lanza `ImproperlyConfigured`.

> Seguridad: el repositorio es público, así que **nunca** pongas la clave en el
> código ni en `.env.example`. Va solo en `.env` (ignorado por git) y en las
> variables de entorno de Render.

> Limitaciones de ImgBB: no se puede leer ni borrar una imagen ya subida con
> esta integración. `_open` lanza `NotImplementedError`, `exists` siempre es
> `False` y `delete` no hace nada (las imágenes reemplazadas quedan huérfanas).
> `url()` devuelve la cadena tal cual (ya es una URL absoluta). No se debe usar
> para redimensionar ni reprocesar imágenes en el servidor.

> Error `code 103` ("You have been forbidden to use this website"): ImgBB lo
> devuelve para imágenes inválidas o demasiado pequeñas (p. ej. un PNG de 1×1).
> **No** es un problema de la clave ni del código: con una imagen real la subida
> devuelve `200` y la URL. Al probar, usa una imagen real. Una clave realmente
> inválida da `code 100` ("Invalid API v1 key"), lo que permite distinguir ambas.

## Base de datos (Supabase)

En **producción** la base de datos es un **PostgreSQL permanente alojado en
Supabase** (sustituye a la base *free* de Render, que caducaba a los 90 días).

- `DATABASE_URL` contiene la **cadena de conexión de Supabase**. Se obtiene en el
  Dashboard de Supabase → *Project Settings* → *Database* → *Connection string*.
- **Recomendado:** usar la cadena del **Session Pooler**
  (`aws-0-<region>.pooler.supabase.com:5432`). Soporta **IPv4** y es la más
  compatible con Render en el plan free; la conexión directa (puerto 5432 del
  host `db.<ref>.supabase.co`) puede ser **IPv6-only** y fallar.
- **Esquema automático:** `build.sh` ejecuta `python manage.py migrate`, así que
  el esquema se **crea y se mantiene solo** en Supabase en cada deploy. No hay
  que ejecutar SQL a mano.
- **SSL:** `settings.py` usa `ssl_require=not DEBUG`, por lo que en producción se
  exige SSL (Supabase lo requiere; `dj-database-url` añade `sslmode=require`).
- **Local** sigue usando **SQLite** cuando `DATABASE_URL` está vacío.

## Cómo correr en local

```powershell
# 1. Crear y activar el entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
Copy-Item .env.example .env
# edita .env (SECRET_KEY, IMGBB_API_KEY, etc.)

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear usuario administrador
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

- Carta pública: http://localhost:8000/es/ y http://localhost:8000/en/
- Panel privado: http://localhost:8000/admin/

## Modelos (`menu/models.py`)

Todos heredan de `TimeStampedModel` (campos `created_at`, `updated_at`).

- **Category**: `name` (traducible), `slug` (auto desde `name`), `order`, `is_active`.
- **SubCategory**: `category` (FK), `name` (traducible), `slug`, `order`, `is_active`.
  El `slug` es único por categoría.
- **Dish**: `subcategory` (FK), `name` y `description` (traducibles), `price`,
  `prep_time_minutes`, `image`, `is_available`, `order`. Tiene la propiedad
  `prep_time_display`.

### Campos traducibles (ES/EN)

Se registran en `menu/translation.py`. Al añadir un campo traducible:

1. Añádelo a la clase `TranslationOptions` del modelo correspondiente.
2. Ejecuta `python manage.py makemigrations` y `migrate`.

## Admin (`/admin/`)

- `CategoryAdmin` incluye las subcategorías como *inline*.
- Los campos traducibles usan pestañas ES/EN (`TabbedTranslationAdmin`).
- `DishAdmin` muestra vista previa de imagen y trae las acciones
  **Marcar como disponibles** / **Marcar como agotados**.
- Los títulos del admin se definen en `menu/apps.py` (`MenuConfig.ready`).

## Vista pública (`menu/views.py`)

`MenuView` (ListView) arma la carta con `prefetch_related` para evitar consultas
N+1 y descarta en Python las categorías/subcategorías sin platillos disponibles.
Reglas de visibilidad:

- Categoría visible si `is_active=True` y tiene al menos una subcategoría con
  platillos disponibles.
- Subcategoría visible si `is_active=True` y tiene al menos un platillo disponible.
- Platillo visible si `is_available=True`.
- Los elementos vacíos se ocultan por completo (no se muestran como "agotado").

## Internacionalización (ES/EN)

- Idiomas en `settings.LANGUAGES`; idioma por defecto `es`.
- URLs con prefijo (`i18n_patterns`, `prefix_default_language=True`): `/es/`, `/en/`.
- Contenido de la BD: `django-modeltranslation`.
- Interfaz (plantillas): `{% translate %}` y catálogo en `locale/en/LC_MESSAGES/`.

### Regenerar las traducciones de interfaz

En Windows suele no haber `gettext` (`msgfmt`/`xgettext`). Los `.mo` se compilan
con `polib` (puro Python), que **no** está en `requirements.txt` (es una
herramienta de desarrollo). Para recompilar:

```powershell
pip install polib
python -c "import polib; polib.pofile(r'locale/en/LC_MESSAGES/django.po').save_as_mofile(r'locale/en/LC_MESSAGES/django.mo')"
```

> Los archivos `.po` y `.mo` se **versionan** (no están en `.gitignore`), porque
> el build de Render no recompila traducciones.

## Tests

```powershell
python manage.py test
```

Cubren (26 pruebas): generación de slugs, `prep_time_display`, visibilidad de la
vista pública (solo activos y disponibles), prefijos de idioma, la traducción de
interfaz, la sección "Sobre nosotros" (`#about-us`), el almacenamiento de imágenes
(`ImgBBStorage`, con `requests` mockeado) y el comando `create_admin` (omisión sin
variables, creación e idempotencia).

## Estáticos y multimedia

- **Estáticos**: `static/` (fuente) → `staticfiles/` (`collectstatic`), servidos
  por Whitenoise. En producción usa almacenamiento con *manifest*.
- **Multimedia**: todas las imágenes se suben a **ImgBB** (`menu/storage.py`) y la
  base de datos guarda la URL directa. `MEDIA_ROOT` (`media/`) queda solo como
  referencia y no se usa como storage.

## Despliegue en Render

`render.yaml` define **solo el servicio web**; la base de datos es **externa
(PostgreSQL en Supabase)** y se conecta vía la variable `DATABASE_URL`.

- Build: `./build.sh` → `pip install` + `collectstatic` + `migrate` + `create_admin`.
- Start: `gunicorn vilas_carta.wsgi:application`.
- Al crear el servicio, Render pedirá los valores de las variables con
  `sync: false`: `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
  `IMGBB_API_KEY`, `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`,
  `DJANGO_SUPERUSER_PASSWORD`.
- `PYTHON_VERSION` está fijado en `3.14.6`. Si Render no lo tiene disponible,
  ajústalo a una versión soportada (p. ej. `3.14.3`).

### Superusuario automático (`create_admin`)

El plan gratuito de Render **no permite abrir una Shell interactiva**, así que el
superusuario se crea solo durante el build con el comando `create_admin`
(`menu/management/commands/create_admin.py`), que `build.sh` ejecuta tras
`migrate`:

```powershell
python manage.py create_admin
```

- Lee `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` y
  `DJANGO_SUPERUSER_PASSWORD` (vía `python-decouple`, como el resto de config).
- Es **idempotente**: si el usuario ya existe, no lo toca (un cambio de
  contraseña hecho en `/admin/` sobrevive a los deploys).
- Si faltan `USERNAME` o `PASSWORD`, no hace nada y **no rompe el build**.
- Nunca imprime la contraseña en los logs.
- Como la base de Supabase es **permanente**, el admin se crea una sola vez; si
  algún día la base se recrea, dejar las variables puestas hace que el próximo
  build vuelva a crearlo.

En local no es necesario: basta `python manage.py createsuperuser`.

### Checklist antes de desplegar

```powershell
python manage.py check --deploy
python manage.py test
```

## Notas y trampas (gotchas)

- `modeltranslation` debe ir **antes** de `django.contrib.admin` en
  `INSTALLED_APPS`; si no, el Admin falla al autodescubrir modelos.
- Los `.mo` de `locale/` se **versionan**; el build de Render no recompila
  traducciones (compílalos con `polib`, ver *Regenerar las traducciones*).
- `media/` no se usa como storage: **todas** las imágenes se suben a ImgBB y en
  la base de datos solo se guarda la URL absoluta.
- ImgBB responde `code 103` ("forbidden") ante imágenes inválidas o demasiado
  pequeñas (1×1); con una imagen real responde `200`. `code 100` = clave
  inválida. No confundir ambos.
- Reemplazar la imagen de un platillo deja huérfana la anterior en ImgBB: no se
  puede borrar desde el servidor.
- El storage por defecto debe ser `ImgBBStorage`; si no, revisa el bloque
  `STORAGES` en `vilas_carta/settings.py`.

## Convenciones

- No añadir comentarios innecesarios en el código.
- Preferir las utilidades existentes del proyecto antes que lógica nueva.
- Al cambiar modelos: crear migración y actualizar tests.
- Mantener las plantillas con clases semánticas para que el diseño (Stitch) se
  aplique sin reestructurar el HTML.
