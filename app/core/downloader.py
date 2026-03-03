from yt_dlp import YoutubeDL
from typing import List


class Downloader:
    def __init__(self, destination: str, format: str, progress_callback=None):
        callback = progress_callback if progress_callback else self._progress_hook
        self.yt_opts = self._build_opts(
            destination,
            format,
            callback,
        )
        self.yt_dlp_info = {
            "quiet": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
        }

    # Metadata sin descargar
    def extract_video_info(self, url: str) -> List[dict]:
        with YoutubeDL(self.yt_dlp_info) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                if info:
                    return self._info_to_dict(info)
                else:
                    return None
            except Exception as e:
                print(str(e))

    def extract_playlist_info(self, url: str) -> List[dict]:
        with YoutubeDL(self.yt_dlp_info) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                data = []
                for entry in info["entries"]:
                    data.append(self._info_to_dict(entry))
                return data
            except Exception as e:
                print(str(e))
                return []

    def download(self, url: str):
        with YoutubeDL(self.yt_opts) as ytdlp:
            ytdlp.download(url)

    def _progress_hook(self, data: dict):
        print(data)

    def _build_opts(self, destination: str, format: str, progress_callback) -> dict:
        opts = {
            "retries": 3,
            "overwrites": False,
            "fragment_retries": 3,
            "noplaylist": True,
            "outtmpl": f"{destination}/%(title)s.%(ext)s",
            "concurrent_fragment_downloads": 3,
            "continuedl": True,
            "progress_hooks": [progress_callback],
        }
        if format == "mp3":

            opts.update(
                {
                    "format": "bestaudio",
                    "extractaudio": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "0",
                        }
                    ],
                    "audioformat": "mp3",
                    "audioquality": "0",
                    "embedthumbnail": True,
                    "convert_thumbnails": "jpg",
                    "addmetadata": True,
                }
            )
        else:
            opts.update(
                {
                    "format": "bv*[height<=1080]+ba/b",
                    "merge_output_format": "mp4",
                }
            )
        return opts

    def _info_to_dict(self, info: dict) -> dict:
        return {
            "id": info["id"],
            "url": info["webpage_url"],
            "channel": info["channel"],
            "title": info["title"],
            "miniatura": info["thumbnails"][0],
        }
