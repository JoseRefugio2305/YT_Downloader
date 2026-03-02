import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.database.models import Download, PlaylistDownload


class DBManager:
    def __init__(self, db_path: str = "data/downloads.db"):
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Asi accedemos a columnas por nombre
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self):
        with self._connect() as conn:
            self._create_tables(conn)

    def _create_tables(
        self, conn: sqlite3.Connection
    ):  # Ejecutamos el codigo SQL para la creacion de las tablas si estas no existen en la DB
        conn.executescript(
            """
               CREATE TABLE IF NOT EXISTS playlist_downloads (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    url              TEXT    NOT NULL,
                    title            TEXT    NOT NULL,
                    format           TEXT    NOT NULL CHECK(format IN ('mp4', 'mp3')),
                    status           TEXT    NOT NULL DEFAULT 'pending'
                                             CHECK(status IN ('pending', 'downloading', 'completed',
                                                            'partial', 'failed', 'cancelled')),
                    destination_path TEXT    NOT NULL,
                    total_items      INTEGER NOT NULL DEFAULT 0,
                    completed_items  INTEGER NOT NULL DEFAULT 0,
                    failed_items     INTEGER NOT NULL DEFAULT 0,
                    created_at       TEXT    NOT NULL,
                    updated_at       TEXT    NOT NULL
               );

               CREATE TABLE IF NOT EXISTS downloads (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    url              TEXT    NOT NULL,
                    title            TEXT    NOT NULL,
                    format           TEXT    NOT NULL CHECK(format IN ('mp4', 'mp3')),
                    status           TEXT    NOT NULL DEFAULT 'pending'
                                             CHECK(status IN ('pending', 'downloading', 'completed',
                                                            'failed', 'cancelled')),
                    destination_path TEXT    NOT NULL,
                    playlist_id      INTEGER REFERENCES playlist_downloads(id) ON DELETE SET NULL,
                    file_size        INTEGER,
                    duration         INTEGER,
                    thumbnail_url    TEXT,
                    error_message    TEXT,
                    created_at       TEXT    NOT NULL,
                    updated_at       TEXT    NOT NULL
               );

               CREATE INDEX IF NOT EXISTS idx_downloads_status     ON downloads(status);
               CREATE INDEX IF NOT EXISTS idx_downloads_playlist   ON downloads(playlist_id);
               CREATE INDEX IF NOT EXISTS idx_downloads_created_at ON downloads(created_at);
          """
        )

        # CRUD Download

    def insert_download(self, download: Download) -> int:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                         INSERT INTO downloads (url, title, format, status, detination_path, playlist_id, file_size, duration, thumbnail_url, error_message, created_at, updated_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                    download.url,
                    download.title,
                    download.format,
                    download.status,
                    download.destination_path,
                    download.playlist_id,
                    download.file_size,
                    download.duration,
                    download.thumbnail_url,
                    download.error_message,
                    download.created_at,
                    download.updated_at,
                ),
            )
            return cursor.lastrowid

    def update_downloaded_status(
        self, download_id: int, status: str, error_message: Optional[str] = None
    ):
        with self._connect() as conn:
            conn.execute(
                """
                              UPDATE downloads
                                             SET status = ?, error_message = ?, updated_at = ?
                              WHERE id = ?
                              """,
                (status, error_message, datetime.now().isoformat(), download_id),
            )

    def update_download_info(self, download_id: int, **kwargs):
        if not kwargs:
            return
        kwargs["updated_at"] = datetime.now().isoformat()
        columns = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [download_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE downloads SET {columns} WHERE id = ?", values)

    def get_download_by_id(self, download_id: int) -> Optional[Download]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM downloads WHERE id = ?", (download_id)
            ).fetchone()

        return self._row_to_download(row) if row else None

    def get_downloads(self, status: Optional[str] = None, limit=200, offset: int = 0):
        query = "SELECT * FROM downloads"
        params: list = []
        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        return [self._row_to_download(r) for r in rows]

    def get_downloads_by_playlist(self, playlist_id: int):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM downloads WHERE playlist_id = ? ORDER BY created_at ASC",
                (playlist_id),
            ).fetchall()

        return [self._row_to_download(r) for r in rows]

    def delete_download(self, download_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM downloads WHERE id = ?", (download_id))

    # CRUD playlists
    def insert_playlist(self, playlist: PlaylistDownload) -> int:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                    INSERT INTO playlist_downloads (url, title, format, status, destination_path, total_items, completed_items, failed_items, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """,
                (
                    playlist.url,
                    playlist.title,
                    playlist,
                    format,
                    playlist.status,
                    playlist.destination_path,
                    playlist.total_items,
                    playlist.completed_items,
                    playlist.failed_items,
                    now,
                    now,
                ),
            )

            return cursor.lastrowid

    def update_playlist_status(self, playlist_id: int, status: str):
        with self._connect() as conn:
            conn.execute(
                """ 
               UPDATE playlist_downloads SET 
                    completed_items = (
                         SELECT COUNT(*) FROM downloads
                         WHERE playlist_id = ? AND status = 'completed'
                    ),
                    failed_items = (
                         SELECT COUNT(*) FROM downloads
                         WHERE playlist_id = ? AND statu IN ('failed', 'cancelled')
                    ),
                    updated_at = ?
               WHERE id = ?      
               """,
                (playlist_id, playlist_id, datetime.now().isoformat(), playlist_id),
            )

    def get_playlist_by_id(self, playlist_id: int) -> Optional[PlaylistDownload]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM playlist_downloads WHERE id = ?", (playlist_id)
            ).fetchone()
        return self._row_to_playlist(row) if row else None

    def get_playlists(
        self, limit: int = 100, offset: int = 0
    ) -> list[PlaylistDownload]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM playlist_downloads ORDER BY created_at DES LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()

        return [self._row_to_playlist(r) for r in rows]

    def delete_playlist(self, playlist_id: int):
        with self._connect() as conn:
            # Por la configuracion, cuando se elimine una playlist todos los videos en downloads que esten asociados a ella quedaran con playlist_id en NULL
            conn.execute("DELETE FROM playlist_downloads WHERE id = ?", (playlist_id))

    @staticmethod
    def _row_to_download(row: sqlite3.Row) -> Download:
        return Download(
            id=row["id"],
            url=row["url"],
            title=row["title"],
            format=row["format"],
            status=row["status"],
            destination_path=row["destination_path"],
            playlist_id=row["playlist_id"],
            file_size=row["file_size"],
            duration=row["duration"],
            thumbnail_url=row["thumbnail_url"],
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _row_to_playlist(row: sqlite3.Row) -> PlaylistDownload:
        return PlaylistDownload(
            id=row["id"],
            url=row["url"],
            title=row["title"],
            format=row["format"],
            status=row["status"],
            destination_path=row["destination_path"],
            total_items=row["total_items"],
            completed_items=row["completed_items"],
            failed_items=row["failed_items"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
