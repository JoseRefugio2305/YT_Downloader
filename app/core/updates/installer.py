from pathlib import Path
import py7zr
import os
import textwrap
import subprocess
from PySide6.QtWidgets import QApplication
import shutil

from .updater import get_updates_dir
from ..logging.logger import get_logger

logger = get_logger(__name__)


def extract_update(archive_path: str) -> Path:
    try:
        updates_dir = get_updates_dir()
        update_file = Path(archive_path)

        if not update_file.is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {archive_path}")

        extracted_dir = updates_dir / "extracted"
        extracted_dir.mkdir(exist_ok=True)

        with py7zr.SevenZipFile(update_file, mode="r") as update:
            logger.info(f"Iniciando extracción de {update_file}")
            update.extractall(extracted_dir)
            logger.info(f"Termino la extracción de {update_file}")
    except Exception as e:
        logger.error(f"Error en extracción de {update_file}: {str(e)}")
        raise

    return extracted_dir


def create_update_script(extracted_dir: Path, app_dir: Path) -> Path:
    script_path = get_updates_dir() / "update.bat"
    temp_backup = Path(os.environ["TEMP"]) / "ytdl_backup"

    app_dir_s = str(app_dir).replace("/", "\\")
    extracted_dir_s = str(extracted_dir).replace("/", "\\")
    temp_backup_s = str(temp_backup).replace("/", "\\")
    ruta_exe_s = str(app_dir / "YTDownloader.exe").replace("/", "\\")

    str_script_content = textwrap.dedent(
        rf"""
@echo off

timeout /t 10 /nobreak >nul

if not exist "{extracted_dir_s}\YTDownloader.exe" (
    echo No Existe el archivo instalador
    exit /b 1
)

taskkill /F /IM ffmpeg.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM YTDownloader.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

mkdir "{temp_backup_s}"
move "{app_dir_s}\updates" "{temp_backup_s}\"

if exist "{app_dir_s}\data" (
    xcopy /E /Y /I "{app_dir_s}\data" "{temp_backup_s}\data\"
)
if exist "{app_dir_s}\logs" (
    xcopy /E /Y /I "{app_dir_s}\logs" "{temp_backup_s}\logs\"
)

rmdir /s /q "{app_dir_s}"

mkdir "{app_dir_s}"

robocopy "{temp_backup_s}\updates\extracted" "{app_dir_s}" /E /IS /IT
if %errorlevel% leq 7 set errorlevel=0

if exist "{temp_backup_s}\data\" (
    xcopy /E /Y /I "{temp_backup_s}\data\" "{app_dir_s}\data\"
)
if exist "{temp_backup_s}\logs\" (
    xcopy /E /Y /I "{temp_backup_s}\logs\" "{app_dir_s}\logs\"
)

rmdir /s /q "{temp_backup_s}\"

start "" "{ruta_exe_s}"

del "%~f0"
"""
    )

    with open(script_path, "w", encoding="utf-8") as script_file:
        script_file.write(str_script_content)

    return script_path


def launch_update_and_exit(script_path: Path) -> bool:
    logger.info(f"Script de actualización original: {str(script_path)}")
    if not script_path.exists():
        logger.error(f"No existe el archivo de script en la ruta: {str(script_path)}")
        return False

    temp_script = Path(os.environ["TEMP"]) / "ytdl_update.bat"
    shutil.copy2(script_path, temp_script)

    logger.info(f"Script de actualización copia: {str(temp_script)}")
    subprocess.Popen(
        ["cmd.exe", "/c", str(temp_script)],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        close_fds=True,
    )

    QApplication.instance().quit()

    return True
