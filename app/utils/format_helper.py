import re
from datetime import datetime

CHAR_PROHIB_REGEX = re.compile(r'[<>:"/\\|?*\x00-\x1F]')


def format_duration(segundos_t: int) -> str:
    horas, resto = divmod(
        segundos_t, 3600
    )  # Obtenemos las horas los segundos restantes
    minutos, segundos = divmod(
        resto, 60
    )  # Obtenemos los minutos y los segundos restantes
    return f"{horas:02}:{minutos:02}:{segundos:02}"


def format_file_size(bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0


def sanitize_filename(name: str, video_id: str) -> str:
    new_name = re.sub(CHAR_PROHIB_REGEX, "", name)
    new_name = new_name.strip()
    if new_name == "":
        new_name = f"{video_id}_{str(datetime.timestamp(datetime.now()))}"
    return new_name
