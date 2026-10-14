# 📸 Memory - App de Recuerdos Compartidos con Amigos

**Memory** es una aplicación web moderna desarrollada con **Django** que permite compartir fotos y videos de forma privada y en conjunto con amigos, organizar álbumes y grupos colaborativos, y mantener conversaciones privadas 1 a 1.

---

## ✨ Características Principales

1. **Autenticación Única por Correo y Contraseña**:
   - Registro e inicio de sesión usando exclusivamente email único y contraseña encriptada.
   - Modelo de usuario extendido con foto de perfil, portada, biografía y fecha de nacimiento.
2. **Privacidad Rigurosa entre Amigos**:
   - Los perfiles y recuerdos son privados por defecto.
   - Para poder ver el perfil y los recuerdos de un usuario, primero debes enviarle una solicitud de amistad y esta debe ser aceptada.
   - Si no son amigos, se muestra un banner elegante de bloqueo de cuenta privada con la opción de solicitar amistad.
3. **Recuerdos Compartidos (Fotos y Videos)**:
   - Feed social de recuerdos donde se pueden ver fotos en alta calidad y reproducir videos.
   - Posibilidad de etiquetar amigos en los recuerdos.
   - Sistema de "Me gusta" interactivo y comentarios.
4. **Grupos y Álbumes Colaborativos**:
   - Creación de grupos con amigos donde todos los miembros pueden subir fotos y videos en conjunto a un mismo álbum.
   - Gestión de miembros y roles de administración.
5. **Chat Privado (1 a 1)**:
   - Sección privada exclusiva para chatear directamente con amigos confirmados.
   - Envío de texto y fotos/archivos adjuntos con actualización reactiva.
6. **Diseño Visual de Primer Nivel (Glassmorphism & Dark Mode)**:
   - Interfaz moderna inspirada en lo último en diseño web: efectos de vidrio esmerilado (*glassmorphism*), degradados atmosféricos, paleta índigo/magenta/cian y tipografías *Plus Jakarta Sans* y *Outfit*.

---

## 🚀 Inicio Rápido en Local

### 1. Activar el entorno virtual:
En Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Ejecutar el servidor de desarrollo:
```powershell
python manage.py runserver
```
La aplicación estará disponible en: **http://127.0.0.1:8000/**

---

## 👤 Cuentas de Prueba Pre-configuradas

Para explorar todas las funciones de inmediato, puedes iniciar sesión con las siguientes cuentas de prueba:

| Usuario | Correo Electrónico | Contraseña | Estado / Rol |
|---|---|---|---|
| **Lucas Silva** | `usuario@memory.com` | `Memory123!` | Usuario principal (Amigo de Camila) |
| **Camila Rojas** | `camila@memory.com` | `Memory123!` | Amiga y miembro del grupo "Viaje al Sur 2026" |
| **Ignacio Gómez**| `ignacio@memory.com` | `Memory123!` | Cuenta privada sin amistad (para probar el bloqueo de privacidad) |

*(Si deseas restablecer o volver a poblar los datos de prueba, ejecuta `python seed_demo_data.py`)*

---

## ⚡ Conectar con Supabase (PostgreSQL y Storage)

El proyecto ya está 100% preparado con arquitectura híbrida para conectarse a **Supabase** de manera inmediata:

1. Abre el archivo `.env` en la raíz del proyecto.
2. Descomenta y reemplaza con tus credenciales de Supabase:
   ```env
   # 1. Base de datos PostgreSQL de Supabase
   DATABASE_URL=postgresql://postgres:[TU_CONTRASEÑA]@aws-0-[TU_REGION].pooler.supabase.com:6543/postgres

   # 2. Supabase Storage (para fotos y videos)
   SUPABASE_URL=https://[TU_PROYECTO].supabase.co
   SUPABASE_KEY=[TU_ANON_KEY]
   SUPABASE_BUCKET_MEMORIES=memory-media
   ```
3. Ejecuta las migraciones sobre Supabase:
   ```powershell
   python manage.py migrate
   ```
¡Listo! Tus usuarios, recuerdos y mensajes se almacenarán automáticamente en Supabase de forma segura.

---

## 📁 Estructura del Proyecto

```text
Memory_app/
├── accounts/          # Autenticación, modelo CustomUser, perfiles privados y edición
├── friends/           # Sistema de solicitudes de amistad, relaciones y buscador
├── memories/          # Recuerdos multimedia (fotos/videos), likes, comentarios y feed
├── groups/            # Grupos colaborativos y álbumes en conjunto
├── chat/              # Chat privado 1 a 1 entre amigos
├── memory_project/    # Configuración central (settings, urls, wsgi)
├── templates/         # Plantillas HTML con diseño glassmorphism
│   ├── base.html
│   ├── navbar.html
│   ├── accounts/
│   ├── friends/
│   ├── memories/
│   ├── groups/
│   └── chat/
├── static/css/        # Sistema de estilos modernos (styles.css)
├── seed_demo_data.py  # Script de inicialización de datos de prueba
├── .env               # Variables de entorno y conexión Supabase
└── manage.py
```
