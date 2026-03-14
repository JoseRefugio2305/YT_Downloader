import logging
from pathlib import Path
import os
from logging.handlers import RotatingFileHandler

# Directorios
LOG_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")  # Archivo

# Formato de logs
LOG_FORMAT = "[%(asctime)s] on [%(name)s] Log  with level [%(levelname)s] in [%(module)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger() -> logging.Logger:
    # Definimos el logger
    logger = logging.getLogger("yt_downloader")
    logger.setLevel(logging.DEBUG)

    # Handler en consola, para mensajes en desarrollo
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # Configuraciones para el archivo de registro, este se rotara cuando llegue a los 5MB y se conservaran 5 copias
    fileHandler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fileHandler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # Agregamos los loggers
    if not logger.hasHandlers():
        logger.addHandler(consoleHandler)
        logger.addHandler(fileHandler)

    return logger


logger = setup_logger()


# Funcion para obtener un sublogger jerarquico del logger principal anime_api
def get_logger(name: str | None = None) -> logging.Logger:
    if not name:  # Si no hay nombre regresamos el principal
        return logger
    return logger.getChild(name)
