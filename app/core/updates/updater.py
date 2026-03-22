from PySide6.QtCore import QThread, Signal
import sys
import json
import urllib.request
from pathlib import Path

from ..logging.logger import get_logger
import app.utils.version as V

logger = get_logger(__name__)

RELEASES_API = f"https://api.github.com/repos/{V.GITHUB_REPO}/releases/latest"


# Carpeta raiz del portable, donde esta el .exe principal
def get_app_dir() -> Path:
    # Si está compilado con Nuitka, __compiled__ existe
    if getattr(sys, "__compiled__", False):
        return Path(sys.executable).parent
    # En desarrollo apuntamos a la raíz del proyecto (donde está main.py)
    return Path(__file__).parent.parent.parent


# Retorna la carpeta updates/, la crea si no existe
def get_updates_dir() -> Path:
    app_dir = get_app_dir()
    updates_dir = app_dir / "updates"
    updates_dir.mkdir(exist_ok=True)
    return updates_dir


# Consultamos api de github para revisar por nuevas actualizaciones y comparar la version de las mismas con la que tenemos
def get_latest_release() -> dict | None:
    try:
        logger.info(
            "Consultando API GitHub por nuevas actualizaciones. Verificando última versión disponible"
        )
        req = urllib.request.Request(
            RELEASES_API, headers={"User-Agent": "YTDownloader"}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            logger.info(
                f"Ultima version disponible en GitHub es: {data.get('tag_name','desconocida')}"
            )
            return data
    except urllib.error.URLError as e:
        logger.error(f"Error al consultar GitHub: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear la respuesta de GitHub: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al consultar GitHub: {str(e)}")
        return None


# Compara el tag de la ultiama release con la version actual
def is_update_available(latest_tag: str) -> bool:
    latest = latest_tag.lstrip(
        "v"
    ).strip()  # Si hay una v al principio la limpia para dejar solo la version
    current = V.APP_VERSION.lstrip("v").strip()
    available = (
        latest != current
    )  # Si son diferentes es que hay una nueva version disponible
    logger.info(
        f"Versión actual: {current} | Última: {latest} | Actualización disponible: {available}"
    )

    return available


# Extrae la URL de descarga del archivo .7z de los assets del release, si no esta retornamos None
def get_download_url(release: dict) -> str | None:
    for asset in release.get("assets", []):
        if asset["name"].endswith(".7z"):
            logger.info(f"URL de descarga encontrada:  {asset['browser_download_url']}")
            return asset["browser_download_url"]
    logger.error("No se encontró ningún asset .7z en la release.")
    return None


# Notas de la release
def get_release_notes(release: dict) -> str:
    return release.get("body", "").strip()


def get_release_tag(release: dict) -> str:
    return release.get("tag_name", "").lstrip("v").strip()


# Con este worker se llevaran a cabo validaciones de red para busqueda de actualizaciones y que estas no bloqueen la ejecucion de la aplicacion
class CheckUpdateWorker(QThread):
    update_available = Signal(dict)
    no_update = Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        logger.info(f"Iniciando busqueda de actualizaciones desde: {RELEASES_API}")
        latest_release = get_latest_release()
        if not latest_release:
            self.no_update.emit()
            return

        is_available = is_update_available(get_release_tag(latest_release))

        if is_available:
            self.update_available.emit(latest_release)
        else:
            self.no_update.emit()
