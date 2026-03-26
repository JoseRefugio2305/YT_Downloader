# YT Downloader

<p align="center">
  <img src="./assets/logo.png" style="width:300px; height:auto; display:block; margin:auto;">
</p>

YT Downloader es una aplicación de escritorio para Windows que permite descargar videos y audio desde YouTube, Facebook, X (Twitter) y TikTok. Soporta descargas individuales y playlists completas, con control de calidad, cola de descargas simultáneas, historial persistente y sistema de actualización automática integrado.

---
 
## Descarga del portable
 
Si solo quieres usar la aplicación sin configurar el entorno de desarrollo, descarga el portable directamente desde la sección de [Releases](https://github.com/JoseRefugio2305/YT_Downloader/releases) del repositorio. No requiere instalación ni Python.
 
---

## Requerimientos previos
 
### Para usar el portable
 
- **Node.js portable** — requerido por yt-dlp para resolver los desafíos de JavaScript de YouTube. Debe colocarse en la carpeta `node/` dentro del portable. [nodejs.org](https://nodejs.org/)
- **ffmpeg** — incluido en el portable en la carpeta `ffmpeg/bin/`.

### Para ejecutar desde el repositorio

- **Python 3.11 o superior** — [python.org](https://www.python.org/downloads/)
- **Node.js** — requerido por yt-dlp para resolver los desafíos de JavaScript que YouTube utiliza para proteger sus streams de video. Sin él, algunos videos pueden no estar disponibles para descarga. [nodejs.org](https://nodejs.org/)
- **ffmpeg** — necesario para la conversión de audio a MP3 y el merge de streams de video. Debe colocarse en la carpeta `ffmpeg/bin/` en la raíz del proyecto. [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)
 
---

## Ejecución del repositorio

1. Clona el repositorio:

```bash
git clone https://github.com/JoseRefugio2305/YT_Downloader.git
cd yt-downloader
```

2. Crea y activa un entorno virtual:

```bash
python -m venv myvenv
myvenv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Coloca ffmpeg en la carpeta correcta:

```
yt-downloader/
└── ffmpeg/
    └── bin/
        ├── ffmpeg.exe
        ├── ffplay.exe
        └── ffprobe.exe
```

5. Coloca Node JS portable en la carpeta correcta:

```
yt-downloader/
└── node/
```

6. Ejecuta la aplicación:

```bash
python main.py
```

---
## Compilación del Proyecto
Este Proyecto es compilado con [Nuitka]( https://nuitka.net/). 

### Requerimientos para compilar
 
- **MSVC 14.3 o superior** — compilador de C++ de Microsoft. Se instala a través de [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) seleccionando "Desarrollo para escritorio con C++".
- **Windows SDK** — incluido en la instalación de Build Tools. Requerido por Nuitka para generar el ejecutable.
- Asegúrate de que la ruta de `cl.exe` esté disponible en el PATH del sistema antes de compilar.
> [!NOTE]
> Si no tienes MSVC instalado, Nuitka usará automáticamente Zig como compilador alternativo.
> El ejecutable generado es equivalente, pero el tiempo de compilación puede ser
> significativamente mayor.

El comando utilizado para ello es el siguiente:
```bash
python -m nuitka --standalone --windows-console-mode=disable --enable-plugin=pyside6 --include-package-data=yt_dlp_ejs  --include-package=py7zr --include-data-dir=assets=assets --include-data-dir=node=node --include-data-dir=ffmpeg=ffmpeg/bin --windows-icon-from-ico=assets/icon.ico --output-dir=dist --output-filename=YTDownloader.exe main.py
```

El resultado es un **portable standalone** en la carpeta `dist/main.dist/` listo para distribuir sin necesidad de instalar Python en la máquina destino.


## Tecnologias utilizadas

**Lenguaje**

- Python 3.11+

**Interfaz grafica**

- PySide6 — framework de Qt para Python, usado para construir toda la interfaz de escritorio

**Descarga de contenido**

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — biblioteca de descarga de videos, fork activo de youtube-dl con soporte extendido de formatos y plataformas

**Procesamiento de audio y video**

- ffmpeg — usado para la extraccion de audio, conversion a MP3, merge de streams de video y audio, y embedding de metadatos y caratula en archivos MP3

**Resolución de challenges de JS para yt-dlp**

- NodeJS — requerido por yt-dlp para resolver los desafíos de JavaScript que YouTube utiliza para proteger sus streams de video. Sin él, algunos videos pueden no estar disponibles para descarga.

**Base de datos**

- SQLite3 — base de datos local para persistir el historial de descargas y playlists

**Configuracion**

- QSettings (PySide6) — almacenamiento persistente de preferencias del usuario

**Compilacion**
 
- [Nuitka](https://nuitka.net/) — compilador de Python a C, usado para generar el portable standalone

---

## Estructura del proyecto

```
yt-downloader/
├── main.py
├── requirements.txt
├── node/
├── ffmpeg/
│   └── bin/
├── assets/
├── data/
└── app/
    ├── core/
    │   ├── downloader.py
    │   ├── playlist_manager.py
    │   ├── settings/
    │   ├── updates/
    │   ├── logging/
    │   ├── notifications/
    │   └── workers/
    ├── database/
    │   ├── db_manager.py
    │   └── models.py
    ├── ui/
    │   ├── main_window.py
    │   └── resources/
    └── utils/
```

---

## Funcionalidades

- Descarga de videos en formato MP4 con seleccion de calidad (Mejor calidad, 1080p, 720p, 480p, 360p)
- Descarga de audio en formato MP3 con caratula y metadatos embebidos
- Soporte para playlists completas de YouTube
- Soporte para descarga de videos desde Facebook, X (Twitter) y TikTok
- Cola de descargas con limite de descargas simultaneas configurable
- Delay configurable entre descargas, aplicado de forma consistente entre cada descarga independientemente de si son individuales o parte de una playlist
- Limpieza automatica de archivos residuales al cancelar una descarga en progreso
- Historial persistente de descargas con opciones de reintento y eliminacion
- Configuracion de carpeta de destino, limite de velocidad y delay entre descargas
- Seleccion de cliente de YouTube (tv_embedded, web, android) para compatibilidad con distintos tipos de videos
- Sistema de actualizacion automatica que detecta nuevas versiones disponibles y permite descargarlas e instalarlas directamente desde la aplicacion

---

> [!NOTE]
> Este proyecto es de uso personal y educativo. El uso de esta herramienta debe respetar los términos de servicio de YouTube y las leyes de derechos de autor aplicables en tu país.
