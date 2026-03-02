from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Video individual
@dataclass
class Download:
    url: str
    title: str
    format: str  # 'mp4' | 'mp3'
    status: str  # 'pending' | 'downloading' | 'completed' | 'failed' | 'cancelled'
    destination_path: str

    id: Optional[int] = None
    playlist_id: Optional[int] = (
        None  # FK a PlaylistDownload, None si es descarga individual
    )
    file_size: Optional[int] = None  # Bytes
    duration: Optional[int] = None  # Segundos
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlaylistDownload:
    url: str
    title: str
    format: str  # 'mp4' | 'mp3'
    status: str  # 'pending' | 'downloading' | 'completed' | 'partial' | 'failed' | 'cancelled'
    destination_path: str

    id: Optional[int] = None
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
