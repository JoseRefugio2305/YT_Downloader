from yt_dlp import YoutubeDL
from typing import List, Optional, Tuple
from pathlib import Path

from .settings import Settings


class Downloader:
    FFMPEG_DIR = Path(__file__).parent.parent.parent / "ffmpeg" / "bin"

    def __init__(
        self,
        destination: str,
        format: str,
        progress_callback=None,
        video_quality=None,
        audio_quality=None,
    ):
        callback = progress_callback if progress_callback else self._progress_hook
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
            destination,
            format,
            callback,
        )

    # Metadata sin descargar
    def extract_video_info(self, url: str) -> dict:
        with YoutubeDL(self.yt_dlp_info) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                if info:
                    return self._info_to_dict(info)
                else:
                    return None
            except Exception as e:
                print(str(e))
                return None

    def extract_playlist_info(self, url: str) -> Tuple[Optional[dict], List[dict]]:
        with YoutubeDL(self.yt_dlp_info) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                data = []
                playlist_data = self._info_playlist_to_dict(info)
                for entry in info["entries"]:
                    data.append(self._info_to_dict(entry))
                return playlist_data, data
            except Exception as e:
                print(str(e))
                return None, []

    def download(self, url: str):  # Descarga del archivo
        print(f"[Downloader] Llamando yt-dlp con URL: {url}")
        with YoutubeDL(self.yt_opts) as ytdlp:
            try:
                result = ytdlp.download([url])
            except Exception as e:
                import traceback

                traceback.print_exc()
                raise

    def _progress_hook(self, data: dict):
        print(data)

    def _build_opts(self, destination: str, format: str, progress_callback) -> dict:
        opts = {
            "retries": 3,
            "overwrites": False,  # Si existe el archivo no lo reescribimos
            "fragment_retries": 3,
            "noplaylist": True,  # Evitamos  que descargue toda la playlist en el caso de que el link sea de un video sacada desde su playlist
            "outtmpl": f"{destination}/%(title)s.%(ext)s",
            "concurrent_fragment_downloads": 3,
            "continuedl": True,
            "progress_hooks": [progress_callback],
            "js_runtimes": {"node": {}},
            "quiet": False,
            "verbose": True,
            "no_warnings": False,
            "postprocessor_hooks": [
                lambda d: print(
                    f"[PP Hook] status={d.get('status')} pp={d.get('postprocessor')}"
                )
            ],
            "extractor_args": {
                "youtube": {
                    "player_client": Settings.get_player_client()  # [ "tv_embedded",],  # usa clientes alternativos , "web", "android", "tv_embedded"
                }
            },
        }

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
            print(Settings.get_video_quality())
            opts.update(
                {
                    "ffmpeg_location": str(self.FFMPEG_DIR),
                    "prefer_ffmpeg": True,
                    "format": self._video_quality,  # TODO: Tomar las configuraciones de audio y video de settings
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
