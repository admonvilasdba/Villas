# AGENTS.md — Vila's Carta Digital

Guía para desarrolladores que trabajen en este repositorio. Describe cómo está
estructurado el proyecto, cómo correrlo y dónde configurar las cosas importantes
(credenciales de Cloudinary, base de datos, despliegue, etc.).

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

## Stack

| Componente | Tecnología |
|---|---|
| Framework | Django 6.1 |
| Base de datos | PostgreSQL en producción / SQLite en local |
| Imágenes | Cloudinary (`django-cloudinary-storage`, solo el backend de storage) |
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
├── build.sh                  # build de Render: instala, collectstatic, migrate
├── render.yaml               # infraestructura como código (servicio + Postgres)
├── .env.example              # plantilla de variables de entorno
├── vilas_carta/
│   ├── settings.py           # configuración (lee variables de entorno)
│   ├── urls.py               # /admin/ y rutas públicas con prefijo de idioma
│   ├── wsgi.py / asgi.py
├── menu/                     # app principal
│   ├── models.py             # Category, SubCategory, Dish
│   ├── admin.py              # registro del Admin (inlines, pestañas ES/EN, acciones)
│   ├── translation.py        # campos traducibles por modelo (modeltranslation)
│   ├── views.py              # MenuView (vista pública)
│   ├── urls.py               # rutas de la app
│   ├── tests.py              # tests de modelos, vista y admin
│   └── migrations/
├── templates/
│   ├── base.html             # layout + selector de idioma
│   └── menu/index.html       # carta pública
├── static/css/menu.css       # estilos base (placeholder)
├── locale/en/LC_MESSAGES/    # traducciones de interfaz (.po fuente + .mo compilado)
├── media/                    # subidas locales (solo desarrollo; ignorado por git)
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
| `DATABASE_URL` | Vacío en local (usa SQLite). En producción la provee Render. |
| `TIME_ZONE` | Zona horaria (por defecto `America/Mexico_City`). |
| `CLOUDINARY_URL` | Credenciales de Cloudinary. Ver siguiente sección. |

### Dónde poner las credenciales de Cloudinary

Toda la configuración de imágenes se controla con **una sola variable**:
`CLOUDINARY_URL`.

- En **local**: abre tu `.env` (copia de `.env.example`) y añade:

  ```
  CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
  ```

  Encuentras `API_KEY`, `API_SECRET` y `CLOUD_NAME` en el panel de Cloudinary
  (Dashboard → Account Details / API Keys).

- En **producción (Render)**: agrega la variable de entorno `CLOUDINARY_URL`
  con el mismo formato en la configuración del servicio (Environment →
  Secret File / Environment Variables). Está declarada en `render.yaml` con
  `sync: false`, así que Render te pedirá el valor al crear el servicio.

**Comportamiento según la variable:**

- Si `CLOUDINARY_URL` está definida → el storage por defecto es
  `cloudinary_storage.storage.MediaCloudinaryStorage` y las imágenes se suben a
  Cloudinary (`vilas_carta/settings.py`, bloque `STORAGES`).
- Si **no** está definida → se usa `FileSystemStorage` local (`media/`).
- `build.sh` **no** necesita configuración de Cloudinary; solo se usa en runtime.

> Nota: no instalamos la app `cloudinary_storage` en `INSTALLED_APPS` porque
> incluye un comando `collectstatic` incompatible con Django 6.1
> (`STATICFILES_STORAGE` fue eliminado). Solo se usa su clase de storage.

## Cómo correr en local

```powershell
# 1. Crear y activar el entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
Copy-Item .env.example .env
# edita .env (SECRET_KEY, CLOUDINARY_URL, etc.)

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

Cubren: generación de slugs, `prep_time_display`, visibilidad de la vista pública
(solo activos y disponibles), prefijos de idioma y la traducción de interfaz.

## Estáticos y multimedia

- **Estáticos**: `static/` (fuente) → `staticfiles/` (`collectstatic`), servidos
  por Whitenoise. En producción usa almacenamiento con *manifest*.
- **Multimedia**: local en `media/` (dev) o Cloudinary (producción).

## Despliegue en Render

`render.yaml` define el servicio web y la base de datos PostgreSQL.

- Build: `./build.sh` → `pip install` + `collectstatic` + `migrate`.
- Start: `gunicorn vilas_carta.wsgi:application`.
- Al crear el servicio, Render pedirá los valores de las variables con
  `sync: false`: `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CLOUDINARY_URL`.
- `PYTHON_VERSION` está fijado en `3.14.6`. Si Render no lo tiene disponible,
  ajústalo a una versión soportada (p. ej. `3.14.3`).

### Checklist antes de desplegar

```powershell
python manage.py check --deploy
python manage.py test
```

## Convenciones

- No añadir comentarios innecesarios en el código.
- Preferir las utilidades existentes del proyecto antes que lógica nueva.
- Al cambiar modelos: crear migración y actualizar tests.
- Mantener las plantillas con clases semánticas para que el diseño (Stitch) se
  aplique sin reestructurar el HTML.
