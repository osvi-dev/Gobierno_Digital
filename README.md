# Prueba Técnica de Gobierno Digital

Este proyecto consiste en una aplicación web full-stack con un backend en Django REST Framework y un frontend en React.

## Requisitos Previos

- Docker

- Node.js (versión 18 o superior)
- Python (3.10.4 o superior)

## Estructura del Proyecto

```
prueba_tecnica/
├── backend/         # API REST con Django
└── frontend/        # Aplicación React
```

## Configuración del Backend

1. Navega al directorio del backend:
```sh
cd backend
```

2. Copia o crea el archivo de variables de entorno:
```sh
cp .env.example .env
```

3. Configura las variables de entorno en el archivo `.env`:
```
# Django
SECRET_KEY=tu_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Base de datos para Django
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432

# Variables usadas por docker-compose
POSTGRES_DB=nombre_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password

```
### SECRET_KEY para Django

Ejecuta el siguiente comando para obtener una clave segura. Usa el que funcione en tu sistema:

```bash
# En Linux/macOS:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# En Windows:
py -c "import secrets; print(secrets.token_urlsafe(50))"
```

4. Inicia los servicios con Docker Compose:
```sh
docker compose up --build
```

## Migración de tablas
Ejecuta el siguiente comando para migrar las tablas hacia la base de datos:

```sh
docker compose exec web python manage.py migrate
# Este comando aplica las migraciones para crear las tablas necesarias en la base de datos
```

## Creación de un usuario
Para crear un usuario desde el contenedor debes seguir el siguiente comando:
```sh
docker compose exec web python manage.py createsuperuser
```

## Configuración del Frontend

1. Navega al directorio del frontend:
```sh
cd frontend
```

2. Instala las dependencias:
```sh
npm install
```

3. Inicia la aplicación en modo desarrollo:
```sh
npm start
```

O usando Docker:
```sh
docker compose up --build
```

## Acceso a la Aplicación

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API (Swagger): http://localhost:8000/swagger/
- Documentación API (ReDoc): http://localhost:8000/redoc/

## Características Principales

### Backend
- API REST con Django REST Framework
- Autenticación JWT
- Base de datos PostgreSQL
- Documentación automática con Swagger/OpenAPI
- Tests unitarios con pytest

### Frontend
- Interfaz de usuario moderna con React
- Diseño responsive con Tailwind CSS
- Gestión de estado con Context API
- Sistema de autenticación JWT
- Manejo de formularios con validación
- Paginación de datos
- Exportación a CSV

## Endpoints API

### Autenticación
- POST `/api/token/` - Obtener token de acceso
- POST `/api/token/refresh/` - Refrescar token

### Usuarios
- GET `/api/v1/users/` - Listar usuarios
- POST `/api/v1/users/` - Crear usuario
- PUT `/api/v1/users/{id}/` - Actualizar usuario
- DELETE `/api/v1/users/{id}/` - Eliminar usuario
- GET `/api/v1/users/export/csv/` - Exportar usuarios a CSV

## Ejecución de Tests

### Backend
```sh
cd backend
docker compose exec web pytest

# Para más información y detalle de los tests
docker compose exec web pytest -v
```

## NOTA

Los usuarios creados mediante la pagina o la API pueden usar sus credenciales para iniciar sesión en el sistema.

**Ejemplo:** si el usuario `juan` crea un nuevo usuario con el correo `pedro@test.com` y contraseña `pablo123`, entonces se podrá iniciar sesión en el sistema usando ese correo y contraseña (`pedro@test.com` / `pablo123`).

