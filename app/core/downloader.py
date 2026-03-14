from yt_dlp import YoutubeDL
from typing import List, Optional, Tuple
from pathlib import Path

from .settings.settings import Settings
from ..utils.format_helper import is_media_file,get_only_path
from .logging.logger import get_logger

logger = get_logger(__name__)


class Downloader:
    FFMPEG_DIR = Path(__file__).parent.parent.parent / "ffmpeg" / "bin"

    def __init__(
        self,
        destination: str,
        format: str,
        progress_callback=None,
        postprocess_callback=None,
        video_quality=None,
        audio_quality=None,
    ):
        callback = progress_callback if progress_callback else self._progress_hook
        post_process_callback = (
            postprocess_callback if postprocess_callback else self._progress_hook
        )
        self.yt_dlp_info = {
            "quiet": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
        }

        self._video_quality = video_quality or Settings.get_video_quality()
        self._audio_quality = audio_quality or Settings.get_audio_quality()

        self.yt_opts = self._build_opts(
            destination, format, callback, post_process_callback
        )

    # Metadata sin descargar
    def extract_video_info(self, url: str) -> dict:
        with YoutubeDL(self.yt_dlp_info) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                logger.debug(f"Obteniendo informacion de video {url}")
                if info:
                    return self._info_to_dict(info)
                else:
                    logger.error(f"No se obtuvo informacion de video {url}")
                    return None
            except Exception as e:
                logger.error(
                    f"Error en extraccion de informacion de video {url}: {str(e)}"
                )
                return None

    def extract_playlist_info(self, url: str) -> Tuple[Optional[dict], List[dict]]:
        with YoutubeDL(self.yt_dlp_info) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                data = []
                playlist_data = self._info_playlist_to_dict(info)
                logger.debug(f"Obteniendo informacion de playlist {url}")
                for entry in info["entries"]:
                    data.append(self._info_to_dict(entry))
                return playlist_data, data
            except Exception as e:
                logger.error(
                    f"Error en extraccion de informacion de playlist {url}: {str(e)}"
                )
                return None, []

    def download(self, url: str):  # Descarga del archivo
        logger.debug(f"Llamando yt-dlp con URL: {url}")
        logger.debug(f"Llamando yt-dlp con opts: {self.yt_opts}")
        with YoutubeDL(self.yt_opts) as ytdlp:
            try:
                result = ytdlp.download([url])
            except Exception as e:
                import traceback

                logger.error(f"Error al descargar {url}: {traceback.print_exc()}")

                traceback.print_exc()
                raise

    def _progress_hook(self, data: dict):
        print(data)

    def _build_opts(
        self, destination: str, format: str, progress_callback, postprocess_callback
    ) -> dict:
        opts = {
            "retries": 3,
            "overwrites": False,  # Si existe el archivo no lo reescribimos
            "fragment_retries": 3,
            "noplaylist": True,  # Evitamos  que descargue toda la playlist en el caso de que el link sea de un video sacada desde su playlist
            
            "concurrent_fragment_downloads": 3,
            "continuedl": True,
            "progress_hooks": [progress_callback],
            "js_runtimes": {"node": {}},
            "quiet": False,
            "verbose": True,
            "no_warnings": False,
            "postprocessor_hooks": [postprocess_callback],
            "extractor_args": {
                "youtube": {
                    "player_client": Settings.get_player_client()  # [ "tv_embedded",],  # usa clientes alternativos , "web", "android", "tv_embedded"
                }
            },
        }

        #Revisamos el output del archivo
        is_med_file=is_media_file(destination)
        if is_med_file:
            _,folder,_,file_name=get_only_path(destination)
            opts["outtmpl"]= f"{folder}/{file_name}"
        else:
            opts["outtmpl"]= f"{destination}/%(title)s.%(ext)s"


        # Agregamos ratelimit
        speed_limit = Settings.get_speed_limit()
        if speed_limit:
            opts["ratelimit"] = speed_limit

        if format == "mp3":
            opts.update(
                {
                    "format": "bestaudio/best",
                    "ffmpeg_location": str(self.FFMPEG_DIR),
                    "writethumbnail": True,
                    "convert_thumbnails": "jpg",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": self._audio_quality,
                        },
                        {
                            "key": "FFmpegMetadata",  # embebe metadatos ID3
                        },
                        {
                            "key": "EmbedThumbnail",  # embebe la caratula
                        },
                    ],
                }
            )
        else:
            opts.update(
                {
                    "ffmpeg_location": str(self.FFMPEG_DIR),
                    "prefer_ffmpeg": True,
                    "format": self._video_quality,
                    "merge_output_format": "mp4",
                }
            )
        return opts

    def _info_to_dict(self, info: dict) -> dict:
        url = info.get("webpage_url") or info.get("url")
        miniatura = info.get("thumbnails")
        return {
            "id": info.get("id", ""),
            "url": url,
            "channel": info.get("webpage_url", ""),
            "title": info.get("title", ""),
            "miniatura": miniatura[0] if miniatura and len(miniatura) > 0 else [],
        }

    def _info_playlist_to_dict(self, info: dict) -> dict:
        url = info.get("webpage_url") or info.get("url") or info.get("original_url")
        return {
            "id": info.get("id", ""),
            "url": url,
            "title": info.get("title", ""),
            "playlist_count": info.get("playlist_count", 0),
        }
